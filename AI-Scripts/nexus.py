#!/usr/bin/env python
# -*- coding: utf-8 -*-

# VidBriefs-Desktop/AI-Scripts/chatbot.py

# Dependencies ------------------------------------------------------------------
import sys
import os
import re
import time
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
import textwrap
import datetime
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

# Enhanced Web browsing functionality -------------------------------------------
def browse_website(url):
    print(blue(f"Browsing the website: {url}"))
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.title.string if soup.title else "No title found"
        
        # Extract main content more intelligently
        main_content = ""
        main_tags = soup.find_all(['article', 'main', 'div', 'section'])
        if main_tags:
            main_tag = max(main_tags, key=lambda tag: len(tag.get_text()))
            for element in main_tag.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']):
                main_content += element.get_text().strip() + "\n\n"
        else:
            for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                main_content += element.get_text().strip() + "\n\n"
        
        # Truncate content if it's too long
        max_length = 3000
        if len(main_content) > max_length:
            main_content = main_content[:max_length] + "...\n\n(Content truncated due to length)"
        
        return f"Title: {title}\n\nContent Summary:\n{main_content}"
    except Exception as e:
        return f"Error browsing the website: {str(e)}"
    
def search_relevant_links(query, num_links=3):
    search_url = f"https://www.google.com/search?q={quote_plus(query)}"
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
    system_message = f"""You are a {personality} AI assistant. Provide helpful and engaging responses. Use markdown formatting when appropriate. 
    For each response, include 3-5 relevant links to authoritative sources that provide more information on the topic discussed. 
    Format these links as [Title](URL) at the end of your response under a 'Further Reading' section.
    """
    
    if allow_web_search:
        system_message += " You have the ability to search the web for information when needed. When asked about current events or recent information, use your web browsing capability to provide up-to-date information. When you receive web content, analyze and summarize it concisely."
    if allow_analysis:
        system_message += " You can analyze and interpret code when requested."
    
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
        try:
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
    folder_name = "../Markdown"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
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
    print(bold(blue("\nEnhanced AI Chatbot Assistant with Web Browsing\n")))
    
    ai_model = input(bold("Choose your AI model (gpt/claude): ")).strip().lower()
    while ai_model not in ["gpt", "claude"]:
        print(red("Invalid choice. Please enter 'gpt' or 'claude'."))
        ai_model = input(bold("Choose your AI model (gpt/claude): ")).strip().lower()

    personality = input(bold("Customize Assistant Personality (press Enter for default): ")).strip()
    personality = personality or "BALANCED 🧠 ANALYTICAL-🎨 CREATIVE with MEDIUM 🤝 EMPATHETIC approach"

    allow_web_search = input(bold("Allow web browsing? (y/n): ")).strip().lower() == 'y'
    allow_analysis = input(bold("Allow code analysis? (y/n): ")).strip().lower() == 'y'

    print(f"\nYour {ai_model.upper()} assistant with personality: {bold(personality)}")
    print(f"Web browsing: {bold('Enabled' if allow_web_search else 'Disabled')}")
    print(f"Code analysis: {bold('Enabled' if allow_analysis else 'Disabled')}")
    print("\nType 'exit' to quit, 'restart' to start over, 'browse [URL]' for web browsing, or 'analyze [your code]' for code analysis.")

    messages = [] # initalise message list as empty

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

        if allow_web_search:
            print(blue("\nSearching the web for relevant information..."))
            search_query = user_input.replace("?", "")
            web_result = browse_website(f"https://www.google.com/search?q={search_query}")
            print(green("\nWeb Search Result:"))
            print(web_result)
            messages.append({
                "role": "system", 
                "content": f"Web search results for '{search_query}':\n\n{web_result}\n\nPlease use this information to answer the user's question."
            })

        if user_input.lower().startswith("browse ") and allow_web_search:
            url = user_input[7:]  # Remove "browse " from the start
            print(blue("\nBrowsing the web..."))
            web_result = browse_website(url)
            print(green("\nWeb Browsing Result:"))
            print(web_result)
            messages.append({"role": "user", "content": f"I browsed this website: {url}. Here's the content:\n\n{web_result}\n\nPlease summarize the key points and provide any relevant insights."})
        elif user_input.lower().startswith("analyze ") and allow_analysis:
            code_to_analyze = user_input[8:]  # Remove "analyze " from the start
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
            title = f"Response_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
            file_path = generate_markdown_file(response, title)
            print(green(f"\nExtensive response saved as: {file_path}"))

if __name__ == "__main__":
    main()