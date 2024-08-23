'''
This file will contain the code for the Huberman AI model.
- [ ] get humberman podcast data
- [ ] get huberman lab data
'''

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# VidBriefs-Desktop/AI-Scripts/huberman.py

import os
import sys
import re
import time
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
import requests
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# Initialize AI clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
claude_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Formatting functions
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

# Huberman Lab data fetching functions
def fetch_podcast_episodes():
    """Fetch Huberman Lab podcast episodes from the official website."""
    url = "https://hubermanlab.com/episodes/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    episodes = []
    for episode in soup.find_all('div', class_='episode'):
        title = episode.find('h2').text.strip()
        link = episode.find('a')['href']
        episodes.append({'title': title, 'link': link})
    return episodes

def fetch_episode_transcript(episode_link):
    """Fetch the transcript of a specific episode."""
    response = requests.get(episode_link)
    soup = BeautifulSoup(response.content, 'html.parser')
    transcript = soup.find('div', class_='transcript')
    return transcript.text.strip() if transcript else "Transcript not available."

# AI interaction function
def chat_with_ai(messages, personality, ai_model):
    system_message = f"You are an AI assistant analyzing Andrew Huberman's podcast content. {personality}"

    if ai_model == "gpt":
        try:
            messages.insert(0, {"role": "system", "content": system_message})
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error communicating with GPT: {str(e)}"
    elif ai_model == "claude":
        try:
            claude_messages = [{"role": "user", "content": messages[-1]['content']}]
            response = claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                system=system_message,
                messages=claude_messages
            )
            return response.content[0].text
        except Exception as e:
            return f"Error communicating with Claude: {str(e)}"
    else:
        return "Invalid AI model selected."

# Main function
def main():
    print(bold(blue("\nWelcome to the Huberman Lab Podcast Analyzer!\n")))

    ai_model = input(bold("Choose your AI model (gpt/claude): ")).strip().lower()
    while ai_model not in ["gpt", "claude"]:
        print(red("Invalid choice. Please enter 'gpt' or 'claude'."))
        ai_model = input(bold("Choose your AI model (gpt/claude): ")).strip().lower()

    personality = input(bold("Customize Assistant Personality (press Enter for default): ")).strip()
    personality = personality or "Provide detailed scientific analysis with practical applications."

    print(blue("\nFetching Huberman Lab podcast episodes..."))
    episodes = fetch_podcast_episodes()

    while True:
        print("\nAvailable episodes:")
        for i, episode in enumerate(episodes[:10], 1):  # Show only the first 10 episodes
            print(f"{i}. {episode['title']}")
        print("11. Search for a specific topic")
        print("12. Exit")

        choice = input(bold("\nEnter your choice (1-12): "))

        if choice == '12':
            print("Exiting...")
            break
        elif choice == '11':
            topic = input("Enter the topic you want to search for: ")
            relevant_episodes = [ep for ep in episodes if topic.lower() in ep['title'].lower()]
            if relevant_episodes:
                print("\nRelevant episodes:")
                for i, episode in enumerate(relevant_episodes, 1):
                    print(f"{i}. {episode['title']}")
                ep_choice = int(input("Choose an episode to analyze (number): ")) - 1
                episode = relevant_episodes[ep_choice]
            else:
                print("No relevant episodes found.")
                continue
        elif choice.isdigit() and 1 <= int(choice) <= 10:
            episode = episodes[int(choice) - 1]
        else:
            print(red("Invalid choice. Please try again."))
            continue

        print(blue(f"\nFetching transcript for: {episode['title']}"))
        transcript = fetch_episode_transcript(episode['link'])

        analysis_prompt = f"Analyze the following Huberman Lab podcast episode:\n\nTitle: {episode['title']}\n\nTranscript: {transcript[:2000]}...\n\nProvide a summary of the key points, main scientific concepts discussed, and practical takeaways for listeners."

        print(blue("\nAnalyzing the episode..."))
        analysis = chat_with_ai([{"role": "user", "content": analysis_prompt}], personality, ai_model)

        print(bold(green("\nAnalysis:")))
        print(analysis)

        # Save analysis to a markdown file
        filename = f"Huberman_Analysis_{episode['title'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(os.path.join("Markdown", filename), 'w') as f:
            f.write(f"# Analysis of {episode['title']}\n\n{analysis}")
        print(green(f"\nAnalysis saved to {filename}"))

        while True:
            user_question = input(bold("\nAsk a question about this episode (or type 'back' to return to episode selection): "))
            if user_question.lower() == 'back':
                break

            question_prompt = f"Based on the Huberman Lab podcast episode '{episode['title']}' and the previous analysis, please answer the following question: {user_question}"
            answer = chat_with_ai([{"role": "user", "content": question_prompt}], personality, ai_model)

            print(bold(green("\nAnswer:")))
            print(answer)

if __name__ == "__main__":
    main()