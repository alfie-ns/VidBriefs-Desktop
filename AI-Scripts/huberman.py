import os
import sys
import re
import time
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import anthropic
import markdown

'''
- [ ] Add a function to get relevant parts of the andrew huberman string
- [ ] make the ai like andrew huberman
'''

# Load environment variables
load_dotenv()

# Initialize AI clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
claude_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Formatting functions (unchanged)
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
    episodes = []
    directory = "config/Lex-Huberman/"
    for filename in os.listdir(directory):
        if filename.endswith(".md"):
            with open(os.path.join(directory, filename), 'r') as file:
                content = file.read()
                title = content.split('\n')[0].replace('# ', '')
                episodes.append({
                    'title': title,
                    'filename': filename
                })
    return episodes

def fetch_episode_transcript(filename):
    with open(os.path.join("config/Lex-Huberman/", filename), 'r') as file:
        content = file.read()
        # Remove the title (first line) from the content
        transcript = '\n'.join(content.split('\n')[1:])
    return transcript

# AI interaction function
def chat_with_ai(messages, personality, ai_model):
    system_message = f"You are an AI assistant analyzing Andrew Huberman's podcast content. {personality}"

    if ai_model == "gpt":
        try:
            messages.insert(0, {"role": "system", "content": system_message})
            response = openai_client.chat.completions.create(
                model="gpt-4-mini",
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

def select_relevant_transcript(episodes, query):
    # Simple keyword matching for now
    for episode in episodes:
        if any(keyword in episode['title'].lower() for keyword in query.lower().split()):
            return episode['filename']
    return episodes[0]['filename']  # Default to first episode if no match

# Main function
def main():
    print(bold("Welcome to the Huberman AI Assistant!"))
    
    # Fetch available episodes
    episodes = fetch_podcast_episodes()
    
    while True:
        user_input = input(blue("\nWhat would you like to know about? (Type 'exit' to quit): "))
        
        if user_input.lower() == 'exit':
            break
        
        # Select relevant transcript based on user input
        relevant_transcript = select_relevant_transcript(episodes, user_input)
        
        # Fetch and process the transcript
        transcript_content = fetch_episode_transcript(relevant_transcript)
        
        # Prepare the context for the AI
        context = f"Based on the following transcript excerpt from Andrew Huberman's podcast, answer the user's question: '{user_input}'\n\nTranscript: {transcript_content[:2000]}..."  # Limit context to avoid token limits
        
        # Generate insights using AI
        # ai_response = chat_with_ai([{"role": "user", "content": context}],
        #                            "Respond in the style of Andrew Huberman, using scientific terminology and practical advice. Be concise but thorough.",
        #                            "claude")  # or "gpt"
        
        print(green("\nAndrew Huberman AI:"), ai_response)

if __name__ == "__main__":
    main()