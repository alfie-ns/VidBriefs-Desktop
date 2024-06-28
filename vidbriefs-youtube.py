#!/usr/bin/env python

import os
import re
from openai import OpenAI
import argparse
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get OpenAI API key from environment variables
api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

def bold(text):
    return "\033[1m" + text + "\033[0m"

def blue(text):
    return "\033[34m" + text + "\033[0m"

def red(text):
    return "\033[31m" + text + "\033[0m"

def green(text):
    return "\033[32m" + text + "\033[0m"

def chat_with_gpt(messages, personality):
    messages.append({"role": "system", "content": f"You are a helpful assistant with a {personality} personality."})
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error communicating with GPT-4: {str(e)}"

def get_transcript(url):
    video_id = url.split('/')[-1] if 'youtu.be' in url else parse_qs(urlparse(url).query).get('v', [None])[0]
    
    if not video_id:
        raise ValueError("No video ID found in URL")
    
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    sentences = [entry['text'] for entry in transcript]
    return " ".join(sentences)

def main():
    parser = argparse.ArgumentParser(description="Interactive YouTube video summarizer and chatbot.")
    parser.add_argument("--personality", type=str, help="A brief summary of the chatbot's personality", default="friendly and helpful")
    args = parser.parse_args()

    messages = []
    current_transcript = ""

    print(bold(blue("Welcome to the YouTube Video Summarizer and Chatbot!")))
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
                print(bold(red("\nAssistant: ")), response)
                messages.append({"role": "assistant", "content": response})

    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()