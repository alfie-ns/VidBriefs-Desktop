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
- [X] Needs to accept general prompts where it doesn't do anything particularly functional
- [ ] Nexus2: Make nexus able to create an account on a login page
To do this, I need to give nexus the ability to interact with web pages; not just browse them.
It can also fill out forms, click buttons, and interact with the page in a more dynamic way.
- [ ] Nexus3: Make nexus able to search for and find a specific item on a shopping site
- [ ] Nexus4: Make nexus browse the dark web
- [X] Make Nexus work for both web-browsing and analysis at the same time
- [ ] When this is all done, begin making a Nexus Android app using Django API
- [X] Make a Nexus vscode development system with app/ api/ and desktop/ folders
- [ ] Make nexus able to monitor specific social media accounts
- [ ] Insert DrFit into Nexus
- [X] Insert YouTubeAnalysis into Nexus
- [X] Insert TED-Talks into Nexus
- [ ] Improve Nexus' recommendation system, so it can recommend TED talks, YouTube videos, and other content
'''

# Dependencies ------------------------------------------------------------------
import time,sys,re,os,io,json,random,schedule,threading
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
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from queue import Queue
from threading import Thread
from urllib.parse import urljoin
from urllib.parse import urlparse


task_queue = Queue()
thread_local = threading.local()

# WebBrowser Class -------------------------------------------------------------
class WebBrowser:
    def __init__(self, browser_type='chrome'):
        if browser_type.lower() == 'chrome':
            self.driver = webdriver.Chrome()
        elif browser_type.lower() == 'firefox':
            self.driver = webdriver.Firefox()
        else:
            raise ValueError("Unsupported browser type")

    def navigate(self, url):
        self.driver.get(url)

    def find_element(self, selector, by=By.CSS_SELECTOR, timeout=10):
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
        except TimeoutException:
            print(f"Element {selector} not found within {timeout} seconds")
            return None

    def click(self, selector, by=By.CSS_SELECTOR):
        try:
            element = self.find_element(selector, by)
            if element:
                element.click()
        except Exception as e:
            print(f"Error clicking element {selector}: {str(e)}")

    def input_text(self, selector, text, by=By.CSS_SELECTOR):
        try:
            element = self.find_element(selector, by)
            if element:
                element.clear()
                element.send_keys(text)
        except Exception as e:
            print(f"Error inputting text to element {selector}: {str(e)}")

    def get_text(self, selector, by=By.CSS_SELECTOR):
        try:
            element = self.find_element(selector, by)
            return element.text if element else ""
        except Exception as e:
            print(f"Error getting text from element {selector}: {str(e)}")
            return ""

    def submit_form(self, form_selector, by=By.CSS_SELECTOR):
        try:
            form = self.find_element(form_selector, by)
            if form:
                form.submit()
        except Exception as e:
            print(f"Error submitting form {form_selector}: {str(e)}")

    def close(self):
        self.driver.quit()
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
def search_and_browse(query, site=None):
    if site:
        url = f"https://www.{site}/search?q={quote_plus(query)}"
        return perform_search(url), browse_website(url)
    else:
        if is_valid_url(query):
            return [], browse_website(query)

        search_terms = generate_search_terms(query)

        threads = []
        for term in search_terms:
            thread = threading.Thread(target=perform_search_thread, args=(term,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # Collect results from all threads
        all_search_results = []
        all_browsed_content = ""
        all_youtube_results = []

        for thread in threads:
            if hasattr(thread_local, 'search_results'):
                all_search_results.extend(thread_local.search_results)
            if hasattr(thread_local, 'browsed_content'):
                all_browsed_content += thread_local.browsed_content
            if hasattr(thread_local, 'youtube_results'):
                all_youtube_results.extend(thread_local.youtube_results)

        all_results = all_search_results + [{"title": f"YouTube: {url}", "url": url} for url in all_youtube_results]

        return all_results, all_browsed_content.strip()
def perform_search_thread(term):
    search_url = f"https://www.google.com/search?q={quote_plus(term)}"
    results = perform_search(search_url)
    
    if not hasattr(thread_local, 'search_results'):
        thread_local.search_results = []
    thread_local.search_results.extend(results)
    
    if results:
        if not hasattr(thread_local, 'browsed_content'):
            thread_local.browsed_content = ""
        thread_local.browsed_content += browse_website(results[0]["url"]) + "\n\n"
    
    youtube_videos = search_youtube_videos(term, max_results=5)
    if not hasattr(thread_local, 'youtube_results'):
        thread_local.youtube_results = []
    thread_local.youtube_results.extend(youtube_videos)
def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
def perform_search(search_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        results = []
        for result in soup.select('.s-result-item'):
            title_elem = result.select_one('h2 a span')
            link_elem = result.select_one('h2 a')
            price_elem = result.select_one('.a-price-whole')
            
            if title_elem and link_elem:
                title = title_elem.text.strip()
                url = 'https://www.amazon.co.uk' + link_elem['href'] if link_elem['href'].startswith('/') else link_elem['href']
                price = price_elem.text.strip() if price_elem else 'N/A'
                results.append({"title": title, "url": url, "price": price})

        return results[:5]  # Return top 5 results
    except Exception as e:
        print(f"Error during search: {str(e)}")
        return []
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
def handle_web_interaction(user_input, ai_model, personality):
    print(blue(f"\nHandling web interaction for: {user_input}"))
    
    parts = user_input.lower().split()
    site = None
    if 'on' in parts:
        site_index = parts.index('on') + 1
        if site_index < len(parts):
            site = parts[site_index]
            search_query = ' '.join(parts[:site_index-1] + parts[site_index+1:])
        else:
            search_query = user_input
    else:
        search_query = user_input

    print(blue(f"\nTask: {search_query}"))
    print(blue(f"\nSearching on: {site if site else 'General web'}"))
    
    search_results, web_result = search_and_browse(search_query, site)
    
    print(blue(f"\nFound {len(search_results)} search results"))
    print(blue(f"Web result length: {len(web_result)}"))

    if search_results:
        print(green("\nTop Search Results:"))
        for i, result in enumerate(search_results[:5], 1):
            print(f"{i}. {result['title']} - {result['url']}")

    analysis_prompt = f"""
    Based on the following web search results and content:

    Search Results:
    {' '.join([f"{i}. {result['title']} - {result['url']}" for i, result in enumerate(search_results[:5], 1)])}

    Content:
    {summarise_content(web_result, max_length=500)}

    Please provide a concise summary addressing the user's request: "{search_query}"
    Focus on the most relevant information and top-rated products if applicable.
    List at least 5 specific recommendations with brief descriptions if available.
    """

    summary = chat_with_ai([{"role": "user", "content": analysis_prompt}], personality, ai_model)
    
    print(green("\nSummary:"))
    print(summary)

    return summary
def get_ai_actions(page_content, task, ai_model, personality):
    prompt = f"""
    Given this webpage content:
    {page_content}

    And this task:
    {task}

    Provide a list of actions to perform on the webpage. Each action should be a JSON object with the following properties:
    - 'type': 'click', 'input', or 'extract'
    - 'selector': the CSS selector to identify the element
    - 'value': (for 'input' type) the text to input

    Respond with only the JSON array of actions, no additional explanation.
    """
    
    response = chat_with_ai([{"role": "user", "content": prompt}], personality, ai_model)
    return json.loads(response)
def perform_action(browser, action):
    action_type = action['type']
    selector = action['selector']
    
    if action_type == 'click':
        browser.click(selector)
    elif action_type == 'input':
        browser.input_text(selector, action['value'])
    elif action_type == 'extract':
        extracted_text = browser.get_text(selector)
        print(f"Extracted: {extracted_text}")
def summarize_interaction(initial_content, final_content, task, ai_model, personality):
    prompt = f"""
    Initial webpage content:
    {initial_content}

    Final webpage content:
    {final_content}

    Task performed:
    {task}

    Summarize the changes that occurred and whether the task was successfully completed.
    """
    
    return chat_with_ai([{"role": "user", "content": prompt}], personality, ai_model)

# [ ] Perodic Web Browsing -----------------------------------------------------
def monitor_website(url, check_interval_minutes):
    def job():
        content = browse_website(url)
        # Analyze content for changes or specific information
        analyze_and_report(content)

    schedule.every(check_interval_minutes).minutes.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)
def analyze_and_report(content):
    # Use AI to analyze content and generate report
    analysis = chat_with_ai([{"role": "user", "content": f"Analyze this content for significant changes or important information:\n\n{content}"}], personality, ai_model)
    # Send report (e.g., via email, Slack, etc.)
    send_report(analysis)
# [ ] ai navigation functions --------------------------------------------------
def ai_navigate_webpage(url, task_description, ai_model, personality):
    browser = WebBrowser()
    try:
        browser.navigate(url)
        
        page_content = browser.driver.page_source
        
        analysis_prompt = f"""
        Given this webpage content:
        {page_content}
        
        And this task:
        {task_description}
        
        Provide a list of actions to perform on the webpage. Each action should be a JSON object with the following properties:
        - 'type': 'click', 'input', or 'extract'
        - 'selector': the CSS selector to identify the element
        - 'value': (for 'input' type) the text to input
        
        Respond with only the JSON array of actions, no additional explanation.
        """
        
        actions = json.loads(chat_with_ai([{"role": "user", "content": analysis_prompt}], personality, ai_model))
        
        for action in actions:
            if action['type'] == 'click':
                browser.click(action['selector'])
            elif action['type'] == 'input':
                browser.input_text(action['selector'], action['value'])
            elif action['type'] == 'extract':
                extracted_text = browser.get_text(action['selector'])
                print(f"Extracted: {extracted_text}")
        
        final_content = browser.driver.page_source
        return summarise_content(final_content)
    finally:
        browser.close()
def take_screenshot(driver, filename):
    driver.save_screenshot(filename)
def human_like_typing(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.1, 0.3))
# [ ] Task queuing and execution -----------------------------------------------
def worker():
    """Worker function to process tasks from the queue."""
    while True:
        task = task_queue.get()
        if task is None:
            break
        try:
            execute_task(task)
        except Exception as e:
            print(f"Error executing task: {e}")
        finally:
            task_queue.task_done()
def start_worker_threads(num_threads):
    """Start a specified number of worker threads."""
    threads = []
    for _ in range(num_threads):
        t = Thread(target=worker)
        t.daemon = True  # Set as daemon so they exit when the main program does
        t.start()
        threads.append(t)
    return threads
def execute_task(task):
    """Execute a given task based on its type."""
    task_type = task.get('type')
    if task_type == 'web_browse':
        url = task.get('url')
        print(f"Browsing {url}")
        # Simulate web browsing
        time.sleep(random.uniform(1, 5))
    elif task_type == 'analyze':
        content = task.get('content')
        print(f"Analyzing content: {content[:50]}...")
        # Simulate content analysis
        time.sleep(random.uniform(2, 8))
    elif task_type == 'report':
        report = task.get('report')
        print(f"Generating report: {report[:50]}...")
        # Simulate report generation
        time.sleep(random.uniform(3, 10))
    else:
        print(f"Unknown task type: {task_type}")
def add_task(task):
    """Add a task to the queue."""
    task_queue.put(task)
def stop_workers(threads):
    """Stop all worker threads."""
    for _ in threads:
        task_queue.put(None)
    for t in threads:
        t.join()
# [X] System Functions ---------------------------------------------------------
def detect_input_type(user_input, ai_model, personality, current_transcript, conversation_context):
    if current_transcript is not None:
        return 'youtube_question'

    # Check for specific input types first
    if 'youtube.com' in user_input or 'youtu.be' in user_input:
        return 'youtube'
    elif user_input.startswith('tedtalk:') or 'ted talk' in user_input or 'tedtalk' in user_input or 'tedtalks' in user_input or 'ted talks' in user_input:
        return 'tedtalk'
    elif user_input.lower().startswith('browse:') or 'search' in user_input or 'web' in user_input or is_valid_url(user_input):
        return 'browse'
    elif user_input.lower().startswith('analyse:') or 'code' in user_input or 'python' in user_input or 'analyse' in user_input or 'analyze' in user_input:
        return 'analysis'
    elif any(keyword in user_input.lower() for keyword in ['what are', 'find', 'search for', 'look up', 'best', 'top']):
        return 'web_interaction'

    # List of common greetings or casual conversation starters
    general_queries = [
        'how are you', 'how you doing', 'what\'s up', 'hello', 'hi', 'hey',
        'good morning', 'good afternoon', 'good evening', 'what\'s new',
        'how\'s it going', 'how have you been', 'what\'s happening'
    ]

    # Check if the user input matches any general queries
    if any(query in user_input.lower() for query in general_queries):
        return 'general'

    # Check for hypothetical scenarios or conversation continuations
    hypothetical_phrases = ['what if', 'suppose', 'imagine if', 'how about', 'in that case']
    if any(phrase in user_input.lower() for phrase in hypothetical_phrases):
        return 'general'

    # Check for subject consistency with previous context
    if conversation_context and is_conversation_continuation(user_input, conversation_context[-1]):
        return 'general'

    # For other queries, use AI to determine the appropriate category
    prompt = f"""
    Analyze the following user input and determine the most appropriate category:

    User Input: "{user_input}"
    Previous Context: {conversation_context[-1] if conversation_context else 'None'}

    Categories:
    1. analysis: If the input is related to programming, algorithms, data structures, or mathematical operations that can be solved with code.
    2. browse: If the input is a general question, fact-checking, or information-seeking query that would benefit from web search.
    3. tedtalk: If the input is specifically related to TED talks or requesting information about TED talks.
    4. huberman: If the input is related to anything about Andrew Huberman or his podcasts.
    5. Web Interaction: If the input involves interacting with a website, filling out forms, or performing specific actions on a webpage return 'web_interaction'.
    6. general: If the input is part of a casual conversation, greeting, general query, or a continuation of the previous context.

    Consider the following guidelines:
    - Use 'analysis' only for queries that clearly involve programming or require mathematical computations.
    - Use 'browse' for queries that require current information or specific fact-checking.
    - Use 'tedtalk' for any queries specifically about TED talks.
    - Use 'huberman' for queries related to Andrew Huberman or his work.
    - If the query can be answered with general knowledge, is a continuation of the previous context, or doesn't fit the above categories, classify it as 'general'.
    - Consider the previous context when determining if this is a continuation of a conversation.

    Respond with ONLY "analysis", "browse", "tedtalk", "huberman", "web_interaction" or "general".
    """

    response = chat_with_ai([{"role": "user", "content": prompt}], personality, ai_model, False, False)

    detected_type = response.strip().lower()
    #print(f"Detected Input Type: {detected_type}")

    if detected_type not in ['analysis', 'browse', 'tedtalk', 'huberman','web_interaction', 'general']:
        return 'general'  # Default to general if unsure

    return detected_type
def is_conversation_continuation(current_input, previous_input):
    current_subjects = extract_subjects(current_input)
    previous_subjects = extract_subjects(previous_input)
    return bool(set(current_subjects) & set(previous_subjects))
def extract_subjects(text):
    # This is a simplified subject extraction. In a real-world scenario,
    # you might want to use NLP libraries for more accurate subject extraction.
    words = text.lower().split()
    return [word for word in words if len(word) > 3 and word.isalpha()]
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
def apply_markdown_styling(text):
    """
    Apply markdown-like styling to text.
    Converts text between double asterisks or colons to bold, removing the markers.
    """
    def replace_bold(match):
        return bold(match.group(1))

    # Replace text between double asterisks, removing the asterisks
    text = re.sub(r'\*\*([^*]+)\*\*', replace_bold, text)

    # Replace text between colons, removing the colons
    text = re.sub(r':([^:]+):', replace_bold, text)

    return text
# ------------------------------------------------------------------------------
# Main 🟥 ----------------------------------------------------------------------
# ------------------------------------------------------------------------------
def main():
    os.system('clear')
    print(bold(blue("\nEnhanced AI Nexus Assistant\n")))
    
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
    print("- 'TedTalk Analysis: Ask Nexus about TED Talks'")
    print("- 'Huberman: [EPISODE]' to analyze Huberman Lab podcast")
    print("- 'Browse: [URL]' for direct web browsing")
    print("- Ask any question for web searching or code analysis\n")

    messages = []  # initialise message list
    current_transcript = None  # initialise current transcript
    conversation_context = []  # initialise conversation context

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
        
        # Update conversation context with user input
        conversation_context.append(user_input)
        #print("Adding user input to the conversation context")
        if len(conversation_context) > 5:  # Keep only the last 5 interactions
            conversation_context.pop(0)
            #print("Popping the first element of the conversation context")
        
        input_type = detect_input_type(user_input, ai_model, personality, current_transcript, conversation_context)
        
        
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
        
        # In the main loop, replace the existing web_interaction handling with:
        elif input_type == 'web_interaction':
            print(blue("\nInitiating web search..."))
            response = handle_web_interaction(user_input, ai_model, personality)
            print(bold(green("\nWeb Search Results:")))
            print(apply_markdown_styling(response))
            messages.append({"role": "assistant", "content": response})
            if len(response.split()) > 100:
                file_path = generate_markdown_file(response, "Web_Interaction_Summary")
                print(green(f"\nSummary saved as: {file_path}"))
        # ---------------------------------------------------------------------
        # [ ] Huberman Lab
        elif input_type == 'huberman':
            episode_title = user_input[9:].strip()
            podcast_content = analyze_huberman_podcast(episode_title)
            print(blue("\nAnalysing Huberman Lab podcast..."))
            analysis_prompt = f"Analyse this Huberman Lab podcast episode and provide insights:\n\n{podcast_content}"
            response = chat_with_ai([{"role": "user", "content": analysis_prompt}], personality, ai_model)

        # ---------------------------------------------------------------------
        # [X] Web Browsing
        if input_type == 'browse' or input_type == 'url':
            #print("Web-browsing detected.")
            if user_input.lower().startswith("browse:"):
                url = user_input[7:].strip()
                print(blue(f"\nBrowsing the specific URL: {url}"))
                _, web_result = search_and_browse(url)
            else:
                print(blue("\nNexus is deciding what to search based on your input..."))
                search_query = chat_with_ai([{"role": "user", "content": f"Based on this user input: '{user_input}', what should I search for to provide the most relevant information? Respond with only the search query, no explanation."}], personality, ai_model)
                print(blue(f"\nNexus-determined search query: {search_query}"))
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
            #print("General query detected.")
            messages.append({"role": "user", "content": user_input})

            print(blue("\nThinking..."))
            response = chat_with_ai(messages, personality, ai_model)

            print(bold(green("\nAssistant: ")) + response)
            messages.append({"role": "assistant", "content": response})

            if len(response.split()) > 100:
                file_path = generate_markdown_file(response)
                print(green(f"\nResponse saved as: {file_path}"))

        # ---------------------------------------------------------------------
        if 'response' in locals():
            conversation_context.append(response)
            if len(conversation_context) > 5:
                conversation_context.pop(0)
        

if __name__ == "__main__":
    main()
