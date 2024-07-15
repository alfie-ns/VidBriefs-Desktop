#!/usr/bin/env python

from openai import OpenAI
import argparse
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
import sys, os, re
import textwrap

# Load environment variables from .env file
load_dotenv()

# Get OpenAI API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")
# || api_key = "sk-...J

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Check if running in a terminal that supports formatting
def supports_formatting():
    return sys.stdout.isatty()

# Formatting functions
def format_text(text, format_code):
    if supports_formatting():
        return f"\033[{format_code}m{text}\033[0m"
    return text

def bold(text):
    return format_text(text, "1")

def blue(text):
    return format_text(text, "34")

def red(text):
    return format_text(text, "31")

def green(text):
    return format_text(text, "32")

def chat_with_gpt(messages, personality):
    messages.append({"role": "system", "content": f"You are a helpful assistant with a {personality} personality."})
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error communicating with GPT-4o: {str(e)}"
    

def get_transcript(url):
    video_id = url.split('/')[-1] if 'youtu.be' in url else parse_qs(urlparse(url).query).get('v', [None])[0]
    
    if not video_id:
        raise ValueError("No video ID found in URL")
    
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    sentences = [entry['text'] for entry in transcript]
    return " ".join(sentences)

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

def main():
    print(bold(blue("\nWelcome to the YouTube Video Summarizer and Chatbot!")))
    print("Before we begin, let's personalize your experience\n")
    choice = input(bold(textwrap.dedent("""
    How would you like to personalise the assistant? 
    (Choose one or combine, e.g., 'concise and technical')

    Options:
    - concise         - analytical     - creative
    - humorous        - empathetic     - motivational
    - skeptical       - educational    - technical
    - casual          - formal         - enthusiastic

    Your choice: """)))
    
    parser = argparse.ArgumentParser(description="Interactive YouTube video summarizer and chatbot.")
    parser.add_argument("--personality", type=str, help=f"Personality of the assistant: {choice}", default=choice or "friendly and helpful")
    args = parser.parse_args()

    messages = []
    current_transcript = ""

    print("\nGreat! Your assistant will be", bold(args.personality))
    print("Paste a YouTube URL to start chatting with GPT-4o about videos of your interest.")
    print("Type 'exit' to quit the program.")

    try:
        while True:
            user_input = input(bold("\nEnter a YouTube URL or your message: ")).strip()

            if user_input.lower() == 'exit':
                print("Exiting...")
                break

            if 'youtube.com' in user_input or 'youtu.be' in user_input:
                try:
                    current_transcript = get_transcript(user_input)
                    messages = [{"role": "system", "content": f"You are a helpful assistant with a {args.personality} personality. Here's a transcript of a YouTube video: {current_transcript}"}]
                    print(bold(green("New video transcript loaded. You can now ask questions about this video.")))
                except Exception as e:
                    print(red(f"Error loading video transcript: {str(e)}"))
                    continue
            else:
                if not current_transcript:
                    print(red("Please load a YouTube video first by pasting its URL."))
                    continue
                
                messages.append({"role": "user", "content": user_input})
                response = chat_with_gpt(messages, args.personality)
                print(bold(red("\nAssistant: ")) + apply_markdown_styling(response))
                messages.append({"role": "assistant", "content": response})

    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()