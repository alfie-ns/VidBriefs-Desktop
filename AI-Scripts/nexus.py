#!/usr/bin/env python
# -*- coding: utf-8 -*-

# VidBriefs-Desktop/AI-Scripts/nexus.py

'''
Nexus is an AI assistant that can communicate with users, 
search the web for relevant information, execute python code,
analyze YouTube transcripts, TED talks, Sight Repo data,
and Huberman Lab podcasts.

TODO:s
- [ ] Make nexus able to create an account on a login page
- [ ] Make nexus able to search for and find a specific item on a shopping site
- [ ] Make nexus browse the dark web
- [ ] Make Nexus work for both web-browsing and analysis at the same time
- [ ] When this is all done, begin making a Nexus Android app using Django API
- [X] Make a Nexus vscode development system with app/ api/ and desktop/ folders
'''

# Dependencies ------------------------------------------------------------------
import time,sys,re,os
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
import textwrap
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import threading
from urllib.parse import urlparse
from urllib.parse import quote_plus
from contextlib import redirect_stdout
import io
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

# Load environment variables
load_dotenv()

# Initialise API clients
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

# Enhanced Web browsing functionality ------------------------------------------
def search_and_browse(query):
    if is_valid_url(query):
        return [], browse_website(query)
    
    search_terms = generate_search_terms(query)
    search_results = []
    browsed_content = ""
    youtube_results = []
    
    # Use threading to perform searches concurrently
    def perform_search_thread(term):
        nonlocal search_results, browsed_content, youtube_results
        search_url = f"https://www.google.com/search?q={quote_plus(term)}"
        results = perform_search(search_url)
        search_results.extend(results)
        
        if results:
            browsed_content += browse_website(results[0]["url"]) + "\n\n"
        
        # Add YouTube search
        youtube_videos = search_youtube_videos(term, max_results=5)
        youtube_results.extend(youtube_videos)
    
    threads = []
    for term in search_terms:
        thread = threading.Thread(target=perform_search_thread, args=(term,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    # Combine all results
    all_results = search_results + [{"title": f"YouTube: {url}", "url": url} for url in youtube_results]
    
    return all_results, browsed_content.strip()

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
    headers = {'User-Agent': 'Mosilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
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

    it truncates the output to a maximum length of 3000 characters and adds an ellipsis;
    this is let the user know that the content has been truncated/shortened. It shortens
    to reduce an overload of information and to keep the output concise and readable.

    """
    try:
        headers = {'User-Agent': 'Mosilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
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

def summarise_content(content, max_length=1500):
    """
    Summarise the content to a specified maximum length.
    
    :param content: Original content to summarise
    :param max_length: Maximum length of the summary
    :return: Summarised content
    """
    if len(content) <= max_length:
        return content
    
    # Simple summarisation by keeping the first few sentences
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-s][a-s]\.)(?<=\.|\?)\s', content)
    summary = ""
    for sentence in sentences:
        if len(summary) + len(sentence) > max_length:
            break
        summary += sentence + " "
    
    return summary.strip() + "...\n\n(Content summarised due to length)"

def search_relevant_links(query, num_links=3):
    search_url = f"https://www.google.com/search?q={quote_plus(query)}"  # Encode query for safe inclusion in URL

    headers = {'User-Agent': 'Mosilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
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
# YouTube [ ] ---------------------------------------------------------------------
def search_youtube_videos(query, max_results=100):
    base_url = "https://www.youtube.com/results"
    videos = []
    
    for i in range(0, max_results, 20):
        params = {
            "search_query": query,
            "sp": "CAI%253D",
            "start": i
        }
        response = requests.get(base_url, params=params)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        video_links = soup.find_all('a', href=re.compile(r'/watch\?v='))
        
        for link in video_links:
            href = link.get('href')
            if href.startswith('/watch?v='):
                full_link = f"https://www.youtube.com{href}"
                if full_link not in videos:
                    videos.append(full_link)
                    
                    if len(videos) >= max_results:
                        return videos
    
    return videos
# AI System -------------------------------------------------------------------
def execute_python_code(code):
    """
    Execute Python code and return the output.
    """
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        try:
            exec(code, {})
        except Exception as e:
            print(f"Error: {str(e)}")
    return buffer.getvalue()

def chat_with_ai(messages, personality, ai_model, allow_web_search=False, allow_analysis=False):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_year = datetime.now().year
    
    system_message = f"""
    You are a {personality} AI assistant, designed to provide helpful, engaging, and accurate responses.
    Your base knowledge cutoff is April 2023, but you have additional capabilities to access the web

    CORE INSTRUCTIONS:
    1. Provide accurate and up-to-date information, utilising web search when enabled.
    2. Maintain the specified personality in your responses.
    3. Be concise for simple queries and elaborate when necessary.
    4. Use your youtube 
    5. Always consider the current date ({current_time}) when discussing recent events or information.

    CAPABILITIES:
    - Web Search: {'' if allow_web_search else 'Not '}Enabled. 
      {f"You can access current information up to {current_time}. Always adjust information to be relative to the current year {current_year}." if allow_web_search else "Rely on your existing knowledge base."}
    - YouTube Search: {'' if allow_web_search else 'Not '}Enabled.
      When web search is enabled, you can also search for and reference relevant YouTube videos.
    - Code Analysis: {'' if allow_analysis else 'Not '}Enabled. 
      {f"You can analyse, interpret, and suggest Python code when appropriate." if allow_analysis else "Avoid in-depth code analysis."}
    - Real-time Updates: When web search is enabled, you can provide up-to-date information on current events and recent developments.


    RESPONSE STRUCTURE:
    1. Address the query directly and concisely.
    2. If web search is used, integrate the information seamlessly, citing sources when appropriate.
    3. For code-related queries (if enabled):
       a. Suggest appropriate Python code to address the query.
       b. Present the code within a Python code block.
       c. Explain the code's functionality and how it addresses the user's query.
    4. Provide additional context or explanation if beneficial.
    5. Suggest follow-up questions or areas for further exploration when appropriate.

    Remember, your primary goal is to assist the user effectively while adhering to these guidelines. Utilise your capabilities to provide the most accurate and helpful information possible.
    """
    
    if allow_web_search:
        system_message += f""" You have the ability to search the web for information when needed. When 
        asked about current events or recent information, use your web browsing capability to provide
        up-to-date information. The current date and time is {current_time}, and the current year is
        {current_year}. When you receive web content, analyse and summarise it concisely, ensuring 
        you're referring to the most recent information available."""

        if len(messages) > 0:
            last_message = messages[-1]['content']
            search_results, browsed_content = search_and_browse(last_message)
            
            if search_results:
                system_message += f"\n\nSearch Results:\n"
                for i, result in enumerate(search_results, 1):
                    system_message += f"{i}. {result['title']} - {result['url']}\n"
            
            if browsed_content:
                summarised_content = summarise_content(browsed_content)
                system_message += f"\n\nBrowsed Content:\n{summarised_content}"
    
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
        try: # this line of code will transform or filter the original messages list to create a format that the claude_client can use
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

def intelligent_code_analysis(user_input, ai_model, personality):
    code_query = re.sub(r'^(an[ae]ly[sz]e):\s*', '', user_input, flags=re.IGNORECASE).strip()
    
    code_generation_prompt = f"""Given the user input: "{code_query}"
    Generate Python code to solve this problem or answer this query.
    The code should be executable and print the result.
    Provide only the Python code, without any explanations or markdown formatting."""
    
    generated_code = chat_with_ai([{"role": "user", "content": code_generation_prompt}], personality, ai_model, False, True)
    
    print(blue("\nGenerated Python code:"))
    print(generated_code)
    
    execution_result = execute_python_code(generated_code)
    
    print(blue("\nExecution result:"))
    print(execution_result)

    analysis_prompt = f"""User input: {code_query}
    Generated and executed Python code:
    ```python
    {generated_code}
    ```
    Execution result:
    {execution_result}

    Please provide an analysis of this code and its execution, including:
    1. Explanation of how the code addresses the user's query
    2. Breakdown of the code's functionality
    3. Interpretation of the execution result
    4. Any relevant Python or domain-specific concepts used"""

    analysis = chat_with_ai([{"role": "user", "content": analysis_prompt}], personality, ai_model, False, True)
    return analysis

# Youtube --------------------------------------------
def extract_video_id(url):
    """Extract video ID from YouTube URL."""
    if 'youtu.be' in url:
        return url.split('/')[-1]
    else:
        return parse_qs(urlparse(url).query).get('v', [None])[0]
def get_youtube_transcript(video_id):
    """Get the transcript for a YouTube video."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return ' '.join([entry['text'] for entry in transcript])
    except Exception as e:
        return f"Error: {str(e)}"
# TED Talk  ------------------------------------------
def analyse_ted_talk(talk_title):
    """Analyze TED talk content."""
    talk_content = get_ted_talk_content(talk_title)
    return talk_content
def get_ted_talk_content(talk_title):
    """Fetch and return the content of a TED talk given its title."""
    for root, dirs, files in os.walk("config/TED-talks"):
        for file in files:
            if file.endswith(".md") and talk_title in file:
                with open(os.path.join(root, file), 'r') as f:
                    return f.read()
    return "Talk content not found."
# Sight Repo  ----------------------------------------
def analyse_sight_repo_data():
    """Analyze Sight Repo data."""
    transcript, metadata, annotation, comment = choose_random_data()
    content = f"Transcript: {read_file_content(os.path.join('transcripts', transcript))}\n\n"
    content += f"Metadata: {read_file_content(os.path.join('metadata', metadata))}\n\n"
    content += f"Annotation: {read_file_content(os.path.join('annotations', annotation))}\n\n"
    content += f"Comment: {read_file_content(os.path.join('comments', comment))}"
    return content
# Huberman Lab  ---------------------------------------
def analyse_huberman_podcast(episode_title):
    """Analyze Huberman Lab podcast content."""
    podcast_content = get_huberman_podcast_content(episode_title)
    return podcast_content
def get_huberman_podcast_content(episode_title):
    """Fetch and return the content of a Huberman Lab podcast episode."""
    directory = "config/Lex-Huberman/"
    for filename in os.listdir(directory):
        if filename.endswith(".md") and episode_title.lower() in filename.lower():
            with open(os.path.join(directory, filename), 'r') as file:
                content = file.read()
                return '\n'.join(content.split('\n')[1:])  # Remove the title
    return "Podcast content not found."
# Markdown File Generation ----------------------------
def read_file_content(filepath):
    """Read and return the content of a file."""
    with open(os.path.join("config", "sight-repo", "data", filepath), 'r') as file:
        return file.read()


    """Fetch and return the content of a Huberman Lab podcast episode."""
    directory = "config/Lex-Huberman/"
    for filename in os.listdir(directory):
        if filename.endswith(".md") and episode_title.lower() in filename.lower():
            with open(os.path.join(directory, filename), 'r') as file:
                content = file.read()
                return '\n'.join(content.split('\n')[1:])  # Remove the title
    return "Podcast content not found."
def generate_markdown_file(content, title=None):
    """Generate a Markdown file with the given content and title."""
    folder_name = "Markdown"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    # Here's where we correctly call the new function
    filename = generate_markdown_filename(content, title)
    
    file_path = os.path.join(folder_name, filename)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return file_path
def generate_markdown_filename(content, title=None):
    """
    Generate a descriptive filename for markdown content.
    
    :param content: The content of the markdown file
    :param title: An optional title for the content
    :return: A string containing the generated filename
    """
    # If no title is provided, try to extract one from the content
    if not title:
        # Look for the first heading in the content
        match = re.search(r'^#\s*(.+)$', content, re.MULTILINE)
        if match:
            title = match.group(1)
        else:
            # If no heading, use the first line (truncated)
            title = content.split('\n')[0][:50]
    
    # Clean the title to make it filename-friendly
    clean_title = re.sub(r'[^\w\s-]', '', title.lower())
    clean_title = re.sub(r'\s+', '-', clean_title)
    
    # Truncate the title if it's too long
    max_title_length = 50
    if len(clean_title) > max_title_length:
        clean_title = clean_title[:max_title_length].rstrip('-')
    
    # Add a timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    return f"{clean_title}_{timestamp}.md"

# ------------------------------------------------------------------------------
# Main 🟥 ----------------------------------------------------------------------
# ------------------------------------------------------------------------------
def main():
    os.system('clear')
    print(bold(blue("\nEnhanced AI Nexus Assistant with Multiple Functionalities\n")))
    
    ai_model = input(bold("Choose your AI model (gpt/claude): ")).strip().lower()
    while ai_model not in ["gpt", "claude"]:
        print(red("Invalid choice. Please enter 'gpt' or 'claude'."))
        ai_model = input(bold("Choose your AI model (gpt/claude): ")).strip().lower()

    personality = input(bold("Customise Assistant Personality (press Enter for default): ")).strip()
    personality = personality or "BALANCED 🧠 ANALYTICAL-🎨 CREATIVE with MEDIUM 🤝 EMPATHETIC approach"

    allow_web_search = input(bold("Allow intelligent web browsing? (y/n): ")).strip().lower() == 'y'
    allow_analysis = input(bold("Allow code analysis? (y/n): ")).strip().lower() == 'y'

    print(f"\nYour {ai_model.upper()} assistant with personality: {bold(personality)}")
    print(f"Intelligent web browsing: {bold('Enabled' if allow_web_search else 'Disabled')}")
    print(f"Code analysis: {bold('Enabled' if allow_analysis else 'Disabled')}")
    print("\nType 'exit' to quit, 'restart' to start over, or enter your query.")
    print("Available commands:")
    print("- 'youtube: [URL]' to analyze YouTube video")
    print("- 'tedtalk: [TITLE]' to analyze TED talk")
    print("- 'sight: analyze' to analyze Sight Repo data")
    print("- 'huberman: [EPISODE]' to analyze Huberman Lab podcast")
    print("- 'browse: [URL]' for direct web browsing")
    print("For code analysis, make sure to make it clear that's what you want it to do.\n")

    messages = []  # initialise message list

    while True:
        user_input = input(bold("\nYou: ")).strip()

        if user_input.lower() == 'exit':
            os.system('clear')
            print("\nExiting...")
            time.sleep(.5)
            sys.exit()

        if user_input.lower() == "restart":
            print(bold(green("\nRestarting the assistant...")))
            main()
            return

        if user_input.lower().startswith("youtube:"):
            video_url = user_input[8:].strip()
            transcript = analyze_youtube_transcript(video_url)
            print(blue("\nAnalyzing YouTube video..."))
            analysis_prompt = f"Analyze this YouTube video transcript and provide insights:\n\n{transcript}"
            response = chat_with_ai([{"role": "user", "content": analysis_prompt}], personality, ai_model, allow_web_search, allow_analysis)

        elif user_input.lower().startswith("tedtalk:"):
            talk_title = user_input[8:].strip()
            talk_content = analyze_ted_talk(talk_title)
            print(blue("\nAnalyzing TED talk..."))
            analysis_prompt = f"Analyze this TED talk and provide insights:\n\n{talk_content}"
            response = chat_with_ai([{"role": "user", "content": analysis_prompt}], personality, ai_model, allow_web_search, allow_analysis)

        elif user_input.lower() == "sight: analyze":
            sight_data = analyze_sight_repo_data()
            print(blue("\nAnalyzing Sight Repo data..."))
            analysis_prompt = f"Analyze this Sight Repo data and provide insights:\n\n{sight_data}"
            response = chat_with_ai([{"role": "user", "content": analysis_prompt}], personality, ai_model, allow_web_search, allow_analysis)

        elif user_input.lower().startswith("huberman:"):
            episode_title = user_input[9:].strip()
            podcast_content = analyze_huberman_podcast(episode_title)
            print(blue("\nAnalyzing Huberman Lab podcast..."))
            analysis_prompt = f"Analyze this Huberman Lab podcast episode and provide insights:\n\n{podcast_content}"
            response = chat_with_ai([{"role": "user", "content": analysis_prompt}], personality, ai_model, allow_web_search, allow_analysis)

        else:
            # Existing web browsing and code analysis logic
            if allow_web_search:
                if user_input.lower().startswith("browse:"):
                    url = user_input[7:].strip()
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
                print(summarise_content(web_result))
                messages.append({
                    "role": "system", 
                    "content": f"Web search and browsing results for '{user_input}':\n\n{web_result}\n\nPlease use this information to inform your response."
                })

            messages.append({"role": "user", "content": user_input})

            print(blue("\nThinking..."))
            response = chat_with_ai(messages, personality, ai_model, allow_web_search, allow_analysis)
            
            if allow_analysis:
                analysis_decision_prompt = f"""
                Given the input: "{user_input}", respond with "Yes" if it meets ANY of these:
                1. Requests Python code or scripts.
                2. Involves math operations or calculations.
                3. Asks for data manipulation or analysis.
                4. Mentions programming concepts (e.g., function, loop, algorithm).
                5. Can be solved with code.

                Examples that should return "Yes":
                - "Write a Python script for prime numbers."
                - "Sort a list in descending order."
                - "Calculate the average of 10, 15, 20."
                - "Create a palindrome function."
                - "Find duplicates in a list."

                Respond ONLY with "Yes" or "No".
                """
                analysis_decision = chat_with_ai([{"role": "user", "content": analysis_decision_prompt}], personality, ai_model, False, False).strip().lower()

                if analysis_decision == "yes":
                    print(blue("\nAnalyzing and executing code..."))
                    response = intelligent_code_analysis(user_input, ai_model, personality)

        print(bold(green("\nAssistant: ")) + response)
        messages.append({"role": "assistant", "content": response})

        if len(response.split()) > 100:
            file_path = generate_markdown_file(response)
            print(green(f"\nResponse saved as: {file_path}"))

if __name__ == "__main__":
    main()