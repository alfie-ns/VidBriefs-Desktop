#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''   AI-Scripts/news.py

This script will be similar to the other except this time it will be an AI assistant that will search for 
news using the NEWS API and categorise the news into the following categories:
    "Important",
    "Interesting",
    "Other"

    [X] I willf find out how to use the newsapi: newapi key located in vidbriefs-desktop/.env file
    [X] I will create the script search for news based on the user's conversation.
    
    furthermore this needs to call newsapi, ive cot the require key in .env

    Furthermore, this script will be the fastest way a user can get news on a specific topic.
'''

# VidBriefs-Desktop/AI-Scripts/news.py

# Dependencies ------------------------------------------------------------------
import time, json, re, os, sys
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
import textwrap
import datetime
from newsapi import NewsApiClient
from bs4 import BeautifulSoup
import requests

# Load environment variables
load_dotenv()

# Initialize API clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
claude_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
newsapi = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))

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

# News fetching and categorization functions ------------------------------------
def fetch_news(query):
    try:
        news = newsapi.get_everything(q=query, language='en', sort_by='relevancy', page_size=10)
        return news['articles']
    except Exception as e:
        print(red(f"Error fetching news: {str(e)}"))
        return []
    
def browse_website(url):
    print(f"Browsing the website: {url}")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.title.string if soup.title else "No title found"
        
        main_content = ""
        main_tags = soup.find_all(['article', 'main', 'div', 'section'])
        if main_tags:
            main_tag = max(main_tags, key=lambda tag: len(tag.get_text()))
            for element in main_tag.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']):
                main_content += element.get_text().strip() + "\n\n"
        else:
            for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                main_content += element.get_text().strip() + "\n\n"
        
        max_length = 3000
        if len(main_content) > max_length:
            main_content = main_content[:max_length] + "...\n\n(Content truncated due to length)"
        
        return f"Title: {title}\n\nContent Summary:\n{main_content}"
    except Exception as e:
        return f"Error browsing the website: {str(e)}"

def get_news_or_web_search(query):
    news_articles = get_news(query)
    if not news_articles:
        print("No news articles found. Performing a web search...")
        web_result = browse_website(f"https://www.google.com/search?q={query}")
        return [{"title": "Web Search Result", "description": web_result, "url": f"https://www.google.com/search?q={query}"}]
    return news_articles


def categorize_news(articles, ai_model):
    categorized_news = {"Important": [], "Interesting": [], "Other": []}
    
    for article in articles:
        category = chat_with_ai([{
            "role": "user", 
            "content": f"Categorize this news article as 'Important', 'Interesting', or 'Other'. Respond with just the category name. Title: {article['title']}\nDescription: {article['description']}"
        }], "analytical", ai_model)
        
        category = category.strip()
        if category not in categorized_news:
            category = "Other"
        
        categorized_news[category].append(article)
    
    return categorized_news

# AI Communication Function -----------------------------------------------------
def chat_with_ai(messages, personality, ai_model):
    system_message = f"""You are a {personality} AI assistant specialised in analysing and categorizing news. 
    Provide concise and insightful responses. If the user asks about recent events or news, 
    use the get_news function to fetch the latest information. Always aim to be helpful and informative."""
    
    functions = [
        {
            "name": "get_news",
            "description": "Fetch news articles based on a query",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query for news articles"
                    }
                },
                "required": ["query"]
            }
        }
    ]
    
    if ai_model == "gpt":
        try:
            messages.insert(0, {"role": "system", "content": system_message})
            response = openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                functions=functions,
                function_call="auto"
            )
            
            message = response.choices[0].message
            
            if message.function_call:
                function_name = message.function_call.name
                function_args = json.loads(message.function_call.arguments)
                
                if function_name == "get_news":
                    news_articles = get_news(function_args.get("query"))
                    
                    # Process the news articles
                    categorized_news = categorize_news(news_articles, ai_model)
                    summary = summarize_news(categorized_news, function_args.get("query"), ai_model)
                    
                    # Generate the response
                    return f"I found some news about '{function_args.get('query')}'. Here's a summary:\n\n{summary}"
            
            return message.content
        except Exception as e:
            return f"Error communicating with GPT: {str(e)}"
    elif ai_model == "claude":
        # Note: As of my last update, Claude doesn't support function calling in the same way as GPT.
        # For Claude, we'll implement a simpler version that checks for news-related queries.
        try:
            claude_messages = [{"role": m['role'], "content": m['content']} for m in messages]
            response = claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=300,
                system=system_message,
                messages=claude_messages
            )
            
            content = response.content[0].text
            
            # Check if the response suggests searching for news
            if "search for news" in content.lower() or "find information" in content.lower() or "latest information" in content.lower():
                query = messages[-1]['content']  # Use the last user message as the query
                news_articles = get_news(query)
                
                if news_articles:
                    categorized_news = categorize_news(news_articles, ai_model)
                    summary = summarize_news(categorized_news, query, ai_model)
                    return f"I found some news about '{query}'. Here's a summary:\n\n{summary}"
                else:
                    return "I couldn't find any relevant news articles for that topic."
            
            return content
        except Exception as e:
            return f"Error communicating with Claude: {str(e)}"
    else:
        return "Invalid AI model selected."

def summarize_news(categorized_news, query, ai_model):
    summary_request = f"Summarize the key points from these news articles about '{query}'. Highlight any significant trends or important information."
    return chat_with_ai([{"role": "user", "content": summary_request}, 
                         {"role": "system", "content": str(categorized_news)}], 
                        "analytical and concise", ai_model)
# Markdown formatting and file-saving functions ---------------------------------
def generate_markdown(query, categorized_news, summary):
    markdown_content = f"# News Analysis: {query}\n\n"
    markdown_content += f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    for category, news_list in categorized_news.items():
        markdown_content += f"## {category} News\n\n"
        for article in news_list:
            markdown_content += f"### {article['title']}\n"
            markdown_content += f"{article['description']}\n"
            markdown_content += f"Source: {article['source']['name']}\n"
            markdown_content += f"[Read more]({article['url']})\n\n"
    
    markdown_content += f"## Summary\n\n{summary}\n"
    
    return markdown_content

def save_markdown_file(content, query):
    folder_name = "Markdown"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    filename = f"{query.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    file_path = os.path.join(folder_name, filename)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return file_path

# Main function -----------------------------------------------------------------
def main():
    os.system('clear')
    print(bold(blue("\nAI News Assistant\n")))
    
    ai_model = input(bold("Choose your AI model (gpt/claude): ")).strip().lower()
    while ai_model not in ["gpt", "claude"]:
        print(red("Invalid choice. Please enter 'gpt' or 'claude'."))
        ai_model = input(bold("Choose your AI model (gpt/claude): ")).strip().lower()

    print("\nType 'exit' to quit or 'restart' to start over.")

    conversation_history = [
        {"role": "system", "content": "You are an AI assistant specialized in providing up-to-date news information. When users ask about current events, recent happenings, or any topic that might benefit from the latest news, always aim to search for and provide the most recent, relevant information. If a query seems to require current news or data, respond by indicating that you will search for the latest information on that topic."}
    ]

    while True:
        user_input = input(bold("\nYou: ")).strip()

        if user_input.lower() == 'exit':
            os.system('clear')
            print("\nExiting...")
            time.sleep(1.5)
            sys.exit()

        if user_input.lower() == "restart":
            print(bold(green("\nRestarting the assistant...")))
            main()
            return

        conversation_history.append({"role": "user", "content": user_input})
        
        # Let the AI interpret the user's input and potentially fetch news
        response = chat_with_ai(conversation_history, "conversational and knowledgeable", ai_model)
        
        # Check if the response contains news information
        if "Here's a summary of the news I found:" in response:
            print(blue("\nSearching for relevant news..."))
            
            # Extract the summary from the response
            summary_start = response.index("Here's a summary of the news I found:")
            summary = response[summary_start:].strip()
            
            print(bold("\n" + summary))
            
            # Fetch the actual news articles for categorization and markdown generation
            articles = fetch_news(user_input)
            
            if articles:
                categorized_news = categorize_news(articles, ai_model)
                
                # Generate and save markdown file
                markdown_content = generate_markdown(user_input, categorized_news, summary)
                file_path = save_markdown_file(markdown_content, user_input)
                print(green(f"\nDetailed analysis saved to: {file_path}"))
            else:
                print(red("Warning: News summary generated, but no articles were found when fetching."))
        
        elif "I couldn't find any relevant news articles for that topic." in response:
            print(red(response))
        
        else:
            # If it's not a news query, just display the response
            print(bold(red("\nAssistant: ")) + response)
        
        # Add the AI's response to the conversation history
        conversation_history.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()