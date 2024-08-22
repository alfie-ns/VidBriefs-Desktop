#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''   AI-Scripts/news.py

This script will be similar to the other except this time it will be an AI assistant that will search for 
news using the NEWS API and categorise the news into the following categories:
    "Important",
    "Interesting",
    "Other"

    [X] I willf find out how to use the newsapi: newapi key located in vidbriefs-desktop/.env file
    [ ] I will create the script search for news based on the user's conversation.

    Furthermore, this script will be the fastest way a user can get news on a specific topic.
'''

# VidBriefs-Desktop/AI-Scripts/news.py



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
from newsapi import NewsApiClient

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
    system_message = f"You are a {personality} AI assistant specialized in analyzing and categorizing news. Provide concise and insightful responses."
    
    if ai_model == "gpt":
        try:
            messages.insert(0, {"role": "system", "content": system_message})
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=100
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error communicating with GPT: {str(e)}"
    elif ai_model == "claude":
        try:
            claude_messages = [{"role": m['role'], "content": m['content']} for m in messages]
            response = claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=100,
                system=system_message,
                messages=claude_messages
            )
            return response.content[0].text
        except Exception as e:
            return f"Error communicating with Claude: {str(e)}"
    else:
        return "Invalid AI model selected."

# Main function -----------------------------------------------------------------
def main():
    os.system('clear')
    print(bold(blue("\nAI News Assistant\n")))
    
    ai_model = input(bold("Choose your AI model (gpt/claude): ")).strip().lower()
    while ai_model not in ["gpt", "claude"]:
        print(red("Invalid choice. Please enter 'gpt' or 'claude'."))
        ai_model = input(bold("Choose your AI model (gpt/claude): ")).strip().lower()

    print("\nType 'exit' to quit or 'restart' to start over.")

    while True:
        query = input(bold("\nEnter a news topic or query: ")).strip()

        if query.lower() == 'exit':
            os.system('clear')
            print("\nExiting...")
            time.sleep(1.5)
            sys.exit()

        if query.lower() == "restart":
            print(bold(green("\nRestarting the assistant...")))
            main()
            return

        print(blue("\nFetching and categorizing news..."))
        articles = fetch_news(query)
        if not articles:
            print(red("No news articles found for this query."))
            continue

        categorized_news = categorize_news(articles, ai_model)

        for category, news_list in categorized_news.items():
            print(bold(f"\n{category} News:"))
            for article in news_list:
                print(f"- {article['title']}")
                print(f"  {article['description']}")
                print(f"  Source: {article['source']['name']}")
                print(f"  URL: {article['url']}")
                print()

        summary = chat_with_ai([{
            "role": "user", 
            "content": f"Provide a brief summary of the key points from these news articles about '{query}'. Highlight any significant trends or important information."
        }], "analytical and concise", ai_model)

        print(bold("\nSummary:"))
        print(summary)

if __name__ == "__main__":
    main()