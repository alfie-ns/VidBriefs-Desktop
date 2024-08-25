'''
This file will contain the code for the Huberman AI model.
- [X] get humberman podcast data
- [X] get huberman lab data
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
    # this function needs to go into config/Lex-Huberman and fetch the data from that directory
    pass

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

# Main function ----------------------------------------------------------------
def main():
    '''
    The Script will contain th functionality to give insights directly from Andrew Huberman, where th
    AI is essentially Andrew Huberman himself. It will get the preview of different transcripts in Lex-Huberman/
    and then decide on what markdown file to traverse to get the insights; then will teach them to the user. 
    Furthermore, however, the AI will be slightly trained on how Andrew Huberman talks and the answers he gives.
    '''

if __name__ == "__main__":
    main()