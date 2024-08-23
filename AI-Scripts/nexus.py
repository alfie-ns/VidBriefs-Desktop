#!/usr/bin/env python
# -*- coding: utf-8 -*-

# VidBriefs-Desktop/AI-Scripts/nexus.py

# Dependencies ------------------------------------------------------------------
import time,sys,re,os
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
import textwrap
from datetime import datetime
import markdown2
import requests
from bs4 import BeautifulSoup
import threading
from urllib.parse import urlparse
from urllib.parse import quote_plus

# Load environment variables
load_dotenv()

# Initialize API clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
claude_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Formatting functions ----------------------------------------------------------
def supports_formatting():
    return sys.stdout.isatty()

def format_text(text, format_code):
    return f"\033[{format_code}m{text}\033[0m" if supports_formatting() else text

def bold(text):
    return format_text(text, "1")

def blue(text):
    return format_text(text, "34")

def red(text):
    return format_text(text, "31")

def green(text):
    return format_text(text, "32")

'''
Truncation refers to the process of shortening something by cutting off part of it. 
In computing, truncation typically involves limiting the length of a string, number,
or other data type to a specified maximum, discarding any excess content.

For example, if you have a text string that exceeds a certain length and you only want
to display a portion of it, you would truncate the string, keeping only the first part 
and removing the rest. Often, an ellipsis (”…”) is added to indicate that the content
has been shortened.

In mathematics, truncation can also refer to reducing the number of digits in a number,
either by cutting off digits after a certain point (e.g., truncating the decimal part of
a number) or by rounding down to a specific place value.

The function truncates the output to clean away the unnecessary 'machine logic'

it truncates the output to a maximum length of 3000 characters and adds an ellipsis;
this is let the user know that the content has been truncated/shortened. It shortens
to reduce an overload of information and to keep the output concise and readable.
'''

# Enhanced Web browsing functionality ----------------------------------------------
def search_and_browse(query):
    """
    Intelligently search for relevant websites based on the query and browse the most relevant ones.
    
    :param query: User's input (can be a URL or a search query)
    :return: Tuple of (search_results, browsed_content)
    """
    # Check if the query is a valid URL
    if is_valid_url(query):
        return [], browse_website(query)
    
    # If not a URL, treat as a search query
    search_terms = generate_search_terms(query)
    search_results = []
    browsed_content = ""
    
    for term in search_terms:
        search_url = f"https://www.google.com/search?q={quote_plus(term)}"
        results = perform_search(search_url)
        search_results.extend(results)
        
        if results:
            browsed_content += browse_website(results[0]["url"]) + "\n\n"
    
    return search_results, browsed_content.strip()

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def generate_search_terms(query):
    """Generate multiple search terms based on the user's query."""
    # This is a simple implementation. You can make this more sophisticated with NLP techniques.
    base_terms = query.lower().split()
    additional_terms = [
        " ".join(base_terms),
        "best " + " ".join(base_terms),
        "popular " + " ".join(base_terms),
        " ".join(base_terms) + " examples",
        " ".join(base_terms) + " guide"
    ]
    return list(set(additional_terms))  # Remove duplicates

def perform_search(search_url):
    """Perform a search and return the results."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        for result in soup.select('.yuRUbf')[:3]:  # Get top 3 results
            title_elem = result.select_one('h3')
            link_elem = result.select_one('a')
            if title_elem and link_elem:
                title = title_elem.text
                url = link_elem['href']
                results.append({"title": title, "url": url})
        
        return results
    except Exception as e:
        print(f"Error during search: {str(e)}")
        return []
def browse_website(url):
    """
    Browse a website and extract relevant content.
    
    :param url: URL of the website to browse
    :return: Extracted content from the website
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.title.string if soup.title else "No title found"
        
        # Extract main content more intelligently
        main_content = extract_main_content(soup)
        
        # Truncate content if it's too long
        max_length = 3000
        if len(main_content) > max_length:
            main_content = main_content[:max_length] + "...\n\n(Content truncated due to length)"
        
        return f"Title: {title}\n\nContent Summary:\n{main_content}"
    except Exception as e:
        return f"Error browsing the website: {str(e)}"

def extract_main_content(soup):
    """
    Extract the main content from a BeautifulSoup object.
    
    :param soup: BeautifulSoup object of the webpage
    :return: Extracted main content as a string
    """
    # Try to find the main content container
    main_tags = soup.find_all(['article', 'main', 'div', 'section'])
    if main_tags:
        main_tag = max(main_tags, key=lambda tag: len(tag.get_text()))
    else:
        main_tag = soup
    
    # Extract text from relevant elements
    content = []
    for element in main_tag.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']):
        text = element.get_text().strip()
        if text:
            content.append(text)
    
    # Join the extracted text
    return "\n\n".join(content)

def summarize_content(content, max_length=1500):
    """
    Summarize the content to a specified maximum length.
    
    :param content: Original content to summarize
    :param max_length: Maximum length of the summary
    :return: Summarized content
    """
    if len(content) <= max_length:
        return content
    
    # Simple summarization by keeping the first few sentences
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', content)
    summary = ""
    for sentence in sentences:
        if len(summary) + len(sentence) > max_length:
            break
        summary += sentence + " "
    
    return summary.strip() + "...\n\n(Content summarized due to length)"

def search_relevant_links(query, num_links=3):
    search_url = f"https://www.google.com/search?q={quote_plus(query)}"  # Encode query for safe inclusion in URL

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = []
        for result in soup.select('.yuRUbf > a')[:num_links]:
            title = result.select_one('h3').text
            url = result['href']
            links.append(f"[{title}]({url})")
        
        return links
    except Exception as e:
        print(red(f"Error searching for links: {str(e)}"))
        return []

# AI Communication Function -----------------------------------------------------
def chat_with_ai(messages, personality, ai_model, allow_web_search=False, allow_analysis=False):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_year = datetime.now().year
    
    system_message = f"""You are a {personality} AI assistant. Provide helpful and engaging responses. 
    If web search is allowed, use the provided search results and browsed content to inform your answers.
    Always cite your sources when using information from web searches.
    
    IMPORTANT: The current date and time is {current_time}, and the current year is {current_year}. 
    This information overrides any dates found in web search results. When discussing current events 
    or recent information, always refer to this current date and year as the present, and adjust your 
    responses accordingly.
    """
    
    if allow_web_search:
        system_message += f" You have the ability to search the web for information when needed. When asked about current events or recent information, use your web browsing capability to provide up-to-date information, but always adjust the information to be relative to the current year {current_year}. When you receive web content, analyze and summarize it concisely, ensuring you're referring to the most recent information available, updated to the current year when necessary."
    
    if allow_analysis:
        system_message += " You can analyse and interpret code when requested."
    
    if allow_web_search and len(messages) > 0:
        last_message = messages[-1]['content']
        search_results, browsed_content = search_and_browse(last_message)
        
        if search_results:
            system_message += f"\n\nSearch Results:\n"
            for i, result in enumerate(search_results, 1):
                system_message += f"{i}. {result['title']} - {result['url']}\n"
        
        if browsed_content:
            summarized_content = summarize_content(browsed_content)
            system_message += f"\n\nBrowsed Content:\n{summarized_content}"
    
    
    if allow_web_search:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_year = datetime.now().year
        system_message += f" You have the ability to search the web for information when needed. When asked about current events or recent information, use your web browsing capability to provide up-to-date information. The current date and time is {current_time}, and the current year is {current_year}. When you receive web content, analyze and summarize it concisely, ensuring you're referring to the most recent information available."
    if allow_analysis:
        system_message += " You can analyse and interpret code when requested."
    
    if ai_model == "gpt":
        try:
            messages.insert(0, {"role": "system", "content": system_message})
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini", 
                messages=messages,
                max_tokens=1000
            )
            ai_response = response.choices[0].message.content
        except Exception as e:
            return f"Error communicating with GPT: {str(e)}"
    elif ai_model == "claude":
        try: # this line of code will ransform or filter the original messages list to create a format that the claude_client can use
            claude_messages = [{"role": m['role'], "content": m['content']} for m in messages]
            response = claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                system=system_message,
                messages=claude_messages
            )
            ai_response = response.content[0].text
        except Exception as e:
            return f"Error communicating with Claude: {str(e)}"
    else:
        return "Invalid AI model selected."
    
    # If the AI didn't provide links, we can still use our search function
    if "Further Reading" not in ai_response:
        keywords = re.findall(r'\b\w+\b', ai_response)[:3]  # Use the first 3 words as keywords
        links = []
        for keyword in keywords:
            links.extend(search_relevant_links(keyword, num_links=1))
        
        if links:
            ai_response += "\n\nFurther Reading:\n" + "\n".join(links)
    
    return ai_response

def generate_markdown_file(content, title):
    folder_name = "Markdown"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{title}_{timestamp}.md"
    file_path = os.path.join(folder_name, filename)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n\n")
        f.write(content)
    
    return file_path

# ------------------------------------------------------------------------------
# Main 🟥 ----------------------------------------------------------------------
# ------------------------------------------------------------------------------
def main():
    os.system('clear')
    print(bold(blue("\nEnhanced AI Nexus Assistant with Intelligent Web Browsing\n")))
    
    ai_model = input(bold("Choose your AI model (gpt/claude): ")).strip().lower()
    while ai_model not in ["gpt", "claude"]:
        print(red("Invalid choice. Please enter 'gpt' or 'claude'."))
        ai_model = input(bold("Choose your AI model (gpt/claude): ")).strip().lower()

    personality = input(bold("Customize Assistant Personality (press Enter for default): ")).strip()
    personality = personality or "BALANCED 🧠 ANALYTICAL-🎨 CREATIVE with MEDIUM 🤝 EMPATHETIC approach"

    allow_web_search = input(bold("Allow intelligent web browsing? (y/n): ")).strip().lower() == 'y'
    allow_analysis = input(bold("Allow code analysis? (y/n): ")).strip().lower() == 'y'

    print(f"\nYour {ai_model.upper()} assistant with personality: {bold(personality)}")
    print(f"Intelligent web browsing: {bold('Enabled' if allow_web_search else 'Disabled')}")
    print(f"Code analysis: {bold('Enabled' if allow_analysis else 'Disabled')}")
    print("\nType 'exit' to quit, 'restart' to start over, or enter your query.")
    print("The AI will intelligently decide what to search based on your input.")
    print("For direct web browsing, start your query with 'browse:'")
    print("For code analysis, start your query with 'analyze:'")

    messages = []  # initialise message list

    while True:
        user_input = input(bold("\nYou: ")).strip()

        if user_input.lower() == 'exit': # Exit the program
            os.system('clear')
            print("\nExiting...")
            time.sleep(.5)
            sys.exit()

        if user_input.lower() == "restart": # Restart the program
            print(bold(green("\nRestarting the assistant...")))
            main()
            return

        if allow_web_search: # if web search is allowed
            # ----------------- Web Browsing ---------------------
            if user_input.lower().startswith("browse:"): # if the user input starts with browse:
                url = user_input[7:].strip()  # Remove "browse:" from the start
                print(blue(f"\nBrowsing the specific URL: {url}"))
                _, web_result = search_and_browse(url)
            else:
                print(blue("\nAI is deciding what to search based on your input..."))
                search_query = chat_with_ai([{"role": "user", "content": f"Based on this user input: '{user_input}', what should I search for to provide the most relevant information? Respond with only the search query, no explanation."}], personality, ai_model, False, False)
                print(blue(f"\nAI-determined search query: {search_query}"))
                print(blue("\nSearching and browsing the web for relevant information..."))
                search_results, web_result = search_and_browse(search_query)
                if search_results:
                    print(green("\nTop Search Results:"))
                    for i, result in enumerate(search_results, 1):
                        print(f"{i}. {result['title']} - {result['url']}")
            
            print(green("\nWeb Browsing Result:"))
            print(summarize_content(web_result))
            messages.append({
                "role": "system", 
                "content": f"Web search and browsing results for '{user_input}':\n\n{web_result}\n\nPlease use this information to inform your response."
            })

        if allow_analysis and user_input.lower().startswith("analyze:"):
            code_to_analyze = user_input[8:].strip()  # Remove "analyze:" from the start
            print(blue("\nAnalyzing code..."))
            analysis_request = f"Please analyze and interpret the following code:\n\n{code_to_analyze}"
            messages.append({"role": "user", "content": analysis_request})
        else:
            messages.append({"role": "user", "content": user_input})

        print(blue("\nThinking..."))
        response = chat_with_ai(messages, personality, ai_model, allow_web_search, allow_analysis)
        
        print(bold(red("\nAssistant: ")) + response)
        messages.append({"role": "assistant", "content": response})

        if len(response.split()) > 100:
            title = f"Response_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            file_path = generate_markdown_file(response, title)
            print(green(f"\nExtensive response saved as: {file_path}"))

if __name__ == "__main__":
    main()