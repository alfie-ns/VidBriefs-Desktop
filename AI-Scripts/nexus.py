#!/usr/bin/env python
# -*- coding: utf-8 -*-

# VidBriefs-Desktop/AI-Scripts/nexus.py

'''
Nexus is an AI assistant that can communicate with users, 
search the web for relevant information, execute python code,
analyze YouTube transcripts, TED talks, Sight Repo data,
and Huberman Lab podcasts.

TODO:
- [X] make web-browsing and code analysis work together all the time
- [ ] Nexus2: Make nexus able to create an account on a login page
To do this, I need to give nexus the ability to interact with web pages; not just browse them.
It can also fill out forms, click buttons, and interact with the page in a more dynamic way.
- [ ] Make nexus able to search for and find a specific item on a shopping site
- [ ] Make nexus browse the dark web
- [ ] Make Nexus work for both web-browsing and analysis at the same time
- [ ] When this is all done, begin making a Nexus Android app using Django API
- [X] Make a Nexus vscode development system with app/ api/ and desktop/ folders
- [ ] Make nexus able to monitor specific social media accounts
- [ ] Insert DrFit into Nexus
- [X] Insert YouTubeAnalysis into Nexus
- [X] Insert TED-Talks into Nexus
- [ ] Improve Nexus' reccoemndation system, for tedtalks first
'''

# Dependencies ------------------------------------------------------------------
import time,sys,re,os,io
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
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from collections import defaultdict

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
# [X] System Functions ---------------------------------------------------------
def detect_input_type(user_input, ai_model, personality, current_transcript):
    if current_transcript is not None:
        return 'youtube_question'
    
    # Check for specific input types first
    if 'youtube.com' in user_input or 'youtu.be' in user_input:
        return 'youtube'
    elif user_input.lower().startswith('browse:') or is_valid_url(user_input):
        return 'browse'
    
    # For general queries, use AI to determine if it's a code analysis or web search query
    prompt = f"""
    Analyze the following user input and determine if it's more likely to be a code analysis request or a web search query:
    
    User Input: "{user_input}"
    
    If the input is related to programming, algorithms, data structures, or mathematical operations that can be solved with code, respond with "analysis".
    If the input is a general question, fact-checking, or information-seeking query that would benefit from web search, respond with "browse".
    If the input is related to ted talks, respond with "tedtalk".
    If the input is related to anything Andrew Huberman, respond with "huberman".
    Respond with ONLY "analysis" or "browse" or "tedtalk" or "huberman". If unsure, respond with "general".
    """
    
    response = chat_with_ai([{"role": "user", "content": prompt}], personality, ai_model, False, False)
    
    detected_type = response.strip().lower()
    
    if detected_type not in ['analysis', 'browse', 'tedtalk', 'huberman', 'youtube']:
        return 'browse'  # Default to web search if unsure
    
    return detected_type
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
    4.  
    5. Always consider the current date ({current_time}) when discussing recent events or information.

    CAPABILITIES:
    - Web Search: Always enabled. You can access current information up to {current_time}. Always adjust information to be relative to the current year {current_year}.
    - YouTube Search: Enabled. You can search for and reference relevant YouTube videos.
    - Code Analysis: Always enabled. You normally run Python code to address math-related queries.
    - Real-time Updates: You can provide up-to-date information on current events and recent developments.

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

    Please provide a brief analysis of this code and its execution, including:
    1. Explanation of how the code addresses the user's query
    2. Breakdown of the code's functionality
    3. Interpretation of the execution result
    4. Any relevant Python or domain-specific concepts used"""

    analysis = chat_with_ai([{"role": "user", "content": analysis_prompt}], personality, ai_model, False, True)
    return analysis
# [X] Youtube ------------------------------------------------------------------
def extract_video_id(url):
    """Extract video ID from YouTube URL."""
    if 'youtu.be' in url:
        #print("extract_video_id is used")
        return url.split('/')[-1]
    else:
        return parse_qs(urlparse(url).query).get('v', [None])[0]
def get_youtube_transcript(video_id):
    """Get the transcript for a YouTube video."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        #print(f"Transcript: {transcript}")
        
        return ' '.join([entry['text'] for entry in transcript])
    except Exception as e:
        return f"Error: {str(e)}"
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
# [X] TED Talk  ---------------------------------------------------------------
def analyse_ted_talk(talk_title):
    """Analyze TED talk content."""
    talk_content = get_ted_talk_content(talk_title)
    return talk_content
def classify_talk_topics():
    """Classify TED talks into broad topics based on their titles and content."""
    all_talks = get_all_talk_titles()
    topic_keywords = {
        'psychology': ['psychology', 'mind', 'brain', 'behavior', 'mental', 'cognitive'],
        'technology': ['technology', 'innovation', 'digital', 'computer', 'ai', 'robot'],
        'science': ['science', 'research', 'discovery', 'experiment', 'scientific'],
        'society': ['society', 'culture', 'community', 'social', 'politics', 'education'],
        'business': ['business', 'entrepreneurship', 'finance', 'economy', 'management'],
        'arts': ['art', 'music', 'creativity', 'design', 'performance', 'literature'],
        'health': ['health', 'medical', 'wellness', 'disease', 'treatment', 'body'],
        'environment': ['environment', 'climate', 'sustainability', 'ecology', 'green'],
    }
    
    talk_topics = defaultdict(list)
    
    for talk in all_talks:
        content = get_ted_talk_content(talk)
        text = (talk + ' ' + content).lower()
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text for keyword in keywords):
                talk_topics[topic].append(talk)
    
    return talk_topics
def recommend_ted_talks(query, num_recommendations=3):
    """
    Search for and recommend TED Talks based on the user's query.
    """
    all_talks = get_all_talk_titles()
    relevant_talks = []

    # Preprocess query
    query_keywords = set(query.lower().split())

    for talk in all_talks:
        content = get_ted_talk_content(talk)
        title_keywords = set(talk.lower().replace('_', ' ').split())
        content_keywords = set(content.lower().split())

        # Calculate relevance score based on keyword matches in title and content
        title_matches = len(query_keywords.intersection(title_keywords))
        content_matches = len(query_keywords.intersection(content_keywords))

        # Increase weight for exact phrase matches
        if query.lower() in talk.lower().replace('_', ' '):
            title_matches += 10
        if query.lower() in content.lower():
            content_matches += 5

        relevance_score = (title_matches * 5) + content_matches  # Weight title matches more heavily

        # Only include talks with a significant relevance score
        if relevance_score > 2:  # Adjust this threshold as needed
            relevant_talks.append((talk, relevance_score))
    
    # Sort by relevance score and get top recommendations
    relevant_talks.sort(key=lambda x: x[1], reverse=True)
    recommendations = relevant_talks[:num_recommendations]
    
    # If we don't have enough recommendations, include some random talks
    if len(recommendations) < num_recommendations:
        remaining_talks = [talk for talk in all_talks if talk not in [r[0] for r in recommendations]]
        random_recommendations = random.sample(remaining_talks, min(num_recommendations - len(recommendations), len(remaining_talks)))
        recommendations.extend([(talk, 0) for talk in random_recommendations])
    
    return [talk for talk, score in recommendations]
def get_ted_talk_content(talk_title):
    """Fetch and return the content of a TED talk given its title."""
    for root, dirs, files in os.walk("config/TED-talks"):
        for file in files:
            if file.endswith(".md") and talk_title in file:
                with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                    return f.read()
    return "Talk content not found."
def get_all_talk_titles():
    """Get all TED Talk titles from the local directory."""
    titles = []
    for root, dirs, files in os.walk("config/TED-talks"):
        for file in files:
            if file.endswith(".md"):
                titles.append(file[:-3])  # Remove .md extension
    return titles# [ ] Sight Repo  --------------------------------------------------------------
def analyse_sight_repo_data():
    """Analyze Sight Repo data."""
    transcript, metadata, annotation, comment = choose_random_data()
    content = f"Transcript: {read_file_content(os.path.join('transcripts', transcript))}\n\n"
    content += f"Metadata: {read_file_content(os.path.join('metadata', metadata))}\n\n"
    content += f"Annotation: {read_file_content(os.path.join('annotations', annotation))}\n\n"
    content += f"Comment: {read_file_content(os.path.join('comments', comment))}"
    return content
# [ ] Huberman Lab  ------------------------------------------------------------
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
# Markdown File Generation -----------------------------------------------------
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

    print(f"\nYour {ai_model.upper()} assistant with personality: {bold(personality)}")
    print("Intelligent web browsing and code analysis are now always available.")
    print("\nType 'exit' to quit, 'restart' to start over, or enter your query.")
    print("What can Nexus do?:")
    print("- 'YouTube Analysis: Paste in a YouTube link and ask questions about the video'")
    print("- 'TedTalk Analysis: Ask Nexus to summarise ted talks'")
    print("- 'Huberman: [EPISODE]' to analyze Huberman Lab podcast")
    print("- 'Browse: [URL]' for direct web browsing")
    print("- Ask any question for web searching or code analysis\n")

    messages = []  # initialise message list
    current_transcript = None  # initialise current transcript

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
        
        input_type = detect_input_type(user_input, ai_model, personality, current_transcript)
        # call detect_input_type to find out what the user wants to do
        
        # ---------------------------------------------------------------------
        # [X] Analysis
        if input_type == 'analysis':
            print(blue("\nPerforming code analysis..."))
            analysis = intelligent_code_analysis(user_input, ai_model, personality)
            print(bold(green("\nCode Analysis:")) + analysis)
            messages.append({"role": "assistant", "content": analysis})
            if len(analysis.split()) > 100:
                file_path = generate_markdown_file(analysis, "Code_Analysis")
                print(green(f"\nAnalysis saved as: {file_path}"))
            continue
        
        # ---------------------------------------------------------------------
        # [X] Youtube
        if input_type == 'youtube':
            video_id = extract_video_id(user_input)
            current_transcript = get_youtube_transcript(video_id)
            print(green("\nYouTube Transcript Loaded. You can now ask questions about this video."))
            messages.append({"role": "system", "content": f"Successfully loaded YouTube transcript; answer questions based on this video in the next prompt."})
            continue  # Go back to the start of the loop to allow user to ask question
        if input_type == 'youtube_question':
            # We have a loaded transcript, so this input is a question about the video
            analysis_prompt = f"Based on this YouTube video transcript:\n\n{current_transcript}\n\nAnswer the following question: {user_input}"
            print(blue("\nNexus is watching the video..."))
            response = chat_with_ai([{"role": "user", "content": analysis_prompt}], personality, ai_model)
            print(bold(green("\nAssistant: ")) + response)
            messages.append({"role": "assistant", "content": response})
            if len(response.split()) > 100:
                file_path = generate_markdown_file(response)
                print(green(f"\nResponse saved as: {file_path}"))
            current_transcript = None  # Reset the current transcript
            continue  # Go back to the start of the loop
        
        # ---------------------------------------------------------------------
        # [X] TED Talk
        elif input_type == 'tedtalk':
            print(blue("\nSearching for relevant TED Talks..."))
            recommended_talks = recommend_ted_talks(user_input, num_recommendations=3)
            
            if recommended_talks:
                print(green("\nRecommended TED Talks:"))
                for i, talk in enumerate(recommended_talks, 1):
                    print(f"{i}. {talk}")
                
                talk_choice = input(bold("\nEnter the number of the talk you'd like to analyze, or press Enter to skip: "))
                if talk_choice.isdigit() and 1 <= int(talk_choice) <= len(recommended_talks):
                    chosen_talk = recommended_talks[int(talk_choice) - 1]
                    talk_content = get_ted_talk_content(chosen_talk)
                    print(blue(f"\nAnalyzing TED talk: {chosen_talk}"))
                    analysis_prompt = f"Analyze this TED talk and provide insights:\n\n{talk_content}"
                    response = chat_with_ai([{"role": "user", "content": analysis_prompt}], personality, ai_model)
                    print(bold(green("\nAssistant: ")) + response)
                    messages.append({"role": "assistant", "content": response})
                    
                    if len(response.split()) > 100:
                        file_path = generate_markdown_file(response, f"TED_Talk_Analysis_{chosen_talk}")
                        print(green(f"\nAnalysis saved as: {file_path}"))
                else:
                    print("Skipping TED Talk analysis.")
            else:
                print(red("No relevant TED Talks found."))
                print("Searching the web for information on this topic instead.")
                input_type = 'browse'  # Switch to web browsing if no TED talks found
            
            if input_type != 'browse':
                continue
        
        # ---------------------------------------------------------------------
        # [ ] Huberman Lab
        elif input_type == 'huberman':
            episode_title = user_input[9:].strip()
            podcast_content = analyze_huberman_podcast(episode_title)
            print(blue("\nAnalyzing Huberman Lab podcast..."))
            analysis_prompt = f"Analyze this Huberman Lab podcast episode and provide insights:\n\n{podcast_content}"
            response = chat_with_ai([{"role": "user", "content": analysis_prompt}], personality, ai_model)

        # ---------------------------------------------------------------------
        # [X] Web Browsing
        if input_type == 'browse' or input_type == 'url':
            if user_input.lower().startswith("browse:"):
                url = user_input[7:].strip()
                print(blue(f"\nBrowsing the specific URL: {url}"))
                _, web_result = search_and_browse(url)
            else:
                print(blue("\nAI is deciding what to search based on your input..."))
                search_query = chat_with_ai([{"role": "user", "content": f"Based on this user input: '{user_input}', what should I search for to provide the most relevant information? Respond with only the search query, no explanation."}], personality, ai_model)
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

        # ---------------------------------------------------------------------
        # [X] General query handling
        if input_type == 'general':
            print("General query detected.")
            messages.append({"role": "user", "content": user_input})

            print(blue("\nThinking..."))
            response = chat_with_ai(messages, personality, ai_model)

            print(bold(green("\nAssistant: ")) + response)
            messages.append({"role": "assistant", "content": response})

            if len(response.split()) > 100:
                file_path = generate_markdown_file(response)
                print(green(f"\nResponse saved as: {file_path}"))

if __name__ == "__main__":
    main()
