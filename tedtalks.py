#!/usr/bin/env python
# -*- coding: utf-8 -*- 

# Dependencies ------------------------------------------------------------------
import sys, os, re, time # system operations, regular expressions, time
from dotenv import load_dotenv # for loading environment variables from .env file

# --------------AI APIS----------------

from openai import OpenAI
import anthropic

# --------------TED Talk Data----------------

import pandas as pd # for reading CSV files
import requests # for making HTTP requests
from bs4 import BeautifulSoup # for parsing HTML

# --------------formatting dependencies----------------

import textwrap # for text formatting
import datetime # for timestamping files
import tiktoken # for tokenizing text
import argparse # for command-line arguments

# ------------------------------------------------------------------------------
# tedbriefs.py 🟣 --------------------------------------------------------------
# -------------------------------------initialisation---------------------------

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
claude_api_key = os.getenv("ANTHROPIC_API_KEY")

# Initialise AI clients
openai_client = OpenAI(api_key=openai_api_key)
claude_client = anthropic.Anthropic(api_key=claude_api_key)

# --------------------------------------------------------------------------------
# Formatting Functions 🟨 --------------------------------------------------------
# --------------------------------------------------------------------------------

# Check if running in a terminal that supports formatting
def supports_formatting():
    return sys.stdout.isatty()

# Formatting functions --------------------------------------------------------
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

# --------------------------------------------------------------------------------
# General Functions 🟩 -----------------------------------------------------------
# --------------------------------------------------------------------------------

# AI Communication Functions -----------------------------------------------------
def chat_with_ai(messages, personality, ai_model, ted_talk_url):
    system_message = f"You are a helpful assistant with a {personality} personality."
    instruction = f"You will assist the user with their question about the TED talk and generate markdown files. When referencing the talk, always use this exact link: {ted_talk_url}. Do not generate or use any placeholder or example links."
    
    if ai_model == "gpt":
        try:
            messages.insert(0, {"role": "system", "content": system_message, "role": "system", "content": instruction})
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error communicating with GPT: {str(e)}"
    elif ai_model == "claude":
        try:
            claude_messages = [
                {"role": "user", "content": messages[-1]['content']}
            ]
            response = claude_client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                system=system_message,
                messages=claude_messages
            )
            return response.content[0].text
        except Exception as e:
            return f"Error communicating with Claude: {str(e)}"
    else:
        return "Invalid AI model selected."

def process_transcript(chunks, query, personality, ai_model):
    """Process the transcript, either as a whole or in chunks."""
    if len(chunks) == 1:
        # Process the entire transcript at once
        full_query = f"Based on this transcript, {query}\n\nTranscript:\n{chunks[0]}"
        return chat_with_ai([{"role": "user", "content": full_query}], personality, ai_model)
    else:
        # Process in chunks
        combined_response = ""
        for i, chunk in enumerate(chunks):
            chunk_query = f"Based on this part of the transcript, {query}\n\nTranscript part {i+1}:\n{chunk}"
            chunk_response = chat_with_ai([{"role": "user", "content": chunk_query}], personality, ai_model)
            combined_response += f"\n\nInsights from part {i+1}:\n{chunk_response}"
        return combined_response  

# Transcript Processing Functions -------------------------------------------------
def num_tokens_from_string(string: str, encoding_name: str = "cl100k_base") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens 

def split_transcript(transcript, max_tokens=125000):
    """Split the transcript into chunks if it exceeds max_tokens."""
    if num_tokens_from_string(transcript) <= max_tokens:
        return [transcript]  # Return the entire transcript as a single chunk

    words = transcript.split()
    chunks = []
    current_chunk = []
    current_count = 0

    for word in words:
        word_tokens = num_tokens_from_string(word)
        if current_count + word_tokens > max_tokens:
            chunks.append(' '.join(current_chunk))
            current_chunk = []
            current_count = 0
        current_chunk.append(word)
        current_count += word_tokens

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

def get_ted_transcript(url):
    """Fetch and return the transcript of a TED talk given its URL."""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    transcript_div = soup.find('div', class_='transcript__inner')
    
    if not transcript_div:
        raise ValueError("Transcript not found on the page.")
    
    paragraphs = transcript_div.find_all('p')
    transcript = ' '.join([p.text for p in paragraphs])
    return transcript

# Text Styling and Markdown Functions ------------------------------------------------
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

def extract_markdown(text):
    """Extract markdown content from the text."""
    # Check if the text contains any Markdown-like formatting
    if re.search(r'(^|\n)#|\*\*|__|\[.*\]\(.*\)|\n-\s', text):
        return text  # Return the entire text if it contains Markdown formatting
    return None

def slugify(text):
    """
    Create a slug from the given text.
    """
    # Convert to lowercase
    text = text.lower()
    # Remove non-word characters (everything except numbers and letters)
    text = re.sub(r'[^\w\s-]', '', text)
    # Replace all spaces with hyphens
    text = re.sub(r'\s+', '-', text)
    return text

def generate_markdown_file(content, title, ted_talk_url):
    """Generate a Markdown file with the given content, title, and TED talk link in a 'Markdown' folder."""
    if not title or title.strip() == "":
        title = "Untitled Document"
    
    folder_name = "Markdown"
    
    # Create the folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    # Generate a slug for the filename
    slug = slugify(title)
    
    # Create a unique filename with a timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{slug}_{timestamp}.md"
    
    # Full path for the file
    file_path = os.path.join(folder_name, filename)
    
    # Write the content to the markdown file
    with open(file_path, 'w') as f:
        f.write(f"# {title}\n\n")
        f.write(content)
        f.write(f"\n\n---\n\n[Link to TED Talk]({ted_talk_url})")
    
    return file_path

# ------------------------------------------------------------------------------
# Main 🟥 -------------------------------------------------------------- 
# ------------------------------------------------------------------------------
def main():
    while True:  # Outer loop for restart 'break' functionality
        os.system('clear')
        # ----------------- Main Program -----------------
        print(bold(blue("\nTED Talk Transcript AI Assistant\n")))
        
        ai_model = input(bold("Choose your AI model (gpt/claude): ")).strip().lower()
        while ai_model not in ["gpt", "claude"]:
            print(red("Invalid choice. Please enter 'gpt' or 'claude'."))
            ai_model = input(bold("Choose your AI model (gpt/claude): ")).strip().lower()

        # Personalise assistant ------------------------------------------------
        personality_choice = input(bold(textwrap.dedent("""
            How would you like to personalise the assistant?
            (Feel free to describe the personality in your own words, or use the suggestions below)

            Learning Style Examples:
            - 🧠 ANALYTICAL: "HIGH 🧠 ANALYTICAL with MEDIUM 🔬 TECHNICAL focus"
            - 🎨 CREATIVE: "MEDIUM 🎨 CREATIVE with LOW 🌈 VISUAL emphasis"
            - 🗣️ PERSUASIVE: "BALANCED 🗣️ PERSUASIVE-🧠 LOGICAL approach"
            - 🌐 MULTIDISCIPLINARY: "HIGH 🌐 MULTIDISCIPLINARY with MEDIUM 🔗 CONTEXTUALIZING"
            - 📚 ACADEMIC: "HIGH 📚 ACADEMIC with LOW 🧪 EXPERIMENTAL style"
            - 🤔 SOCRATIC: "MEDIUM 🤔 SOCRATIC with HIGH 🔍 QUESTIONING focus"
            - 🤝 EMPATHETIC: "HIGH 🤝 EMPATHETIC with MEDIUM 👥 COLLABORATIVE approach"
            - 💡 INNOVATIVE: "BALANCED 💡 INNOVATIVE-🔬 TECHNICAL style"
            - 📊 DATA-DRIVEN: "HIGH 📊 DATA-DRIVEN with LOW 🖼️ CONCEPTUAL emphasis"
            - 🧩 PROBLEM-SOLVING: "MEDIUM 🧩 PROBLEM-SOLVING with HIGH 🔀 ADAPTIVE focus"

            Combine these or create your own to define the AI's learning style and personality.
            Remember, you can specify intensity levels (LOW, MEDIUM, HIGH, BALANCED) and combine traits.

            Your choice: """)))

        personality = personality_choice or "BALANCED 🧠 ANALYTICAL-🎨 CREATIVE with HIGH 🌐 MULTIDISCIPLINARY focus. MEDIUM 🗣️ PERSUASIVE with LOW 🤔 SOCRATIC questioning. HIGH 📊 DATA-DRIVEN and MEDIUM 🤝 EMPATHETIC approach."

        print(f"\nGreat! Your {ai_model.upper()} assistant will be", bold(personality))
        print("Paste a TED talk URL to start chatting about the talk.")
        print("Type 'exit' to quit the program or 'restart' to start over.")

        messages = []
        current_transcript = ""
        transcript_chunks = []

        try:
            current_ted_talk_url = ""
            while True:
                user_input = input(bold("\nEnter a TED talk URL, your message, 'restart', or 'exit': ")).strip()

                if user_input.lower() == 'exit':
                    os.system('clear')
                    print("\nExiting...")
                    time.sleep(1.5)
                    os.system('clear')
                    sys.exit()

                if user_input.lower() == "restart":
                    print(bold(green("Restarting the assistant...")))
                    break  # Break the inner loop to restart

                if 'ted.com/talks' in user_input:
                    current_ted_talk_url = user_input
                    try:
                        current_transcript = get_ted_transcript(user_input)
                        transcript_chunks = split_transcript(current_transcript)
                        if len(transcript_chunks) > 1:
                            print(bold(green("New TED talk transcript loaded and split into chunks due to its length. You can now ask questions about this talk.")))
                        else:
                            print(bold(green("New TED talk transcript loaded. You can now ask questions about this talk.")))
                        messages = []  # Reset conversation history for new talk
                    except Exception as e:
                        print(red(f"Error loading TED talk transcript: {str(e)}"))
                        continue
                else:
                    if not current_transcript:
                        print(red("Please load a TED talk first by pasting its URL."))
                        continue
                    
                    messages.append({"role": "user", "content": user_input})
                    
                    full_query = f"Based on this transcript and our conversation so far, please respond to the latest message: {user_input}\n\nTranscript:\n{current_transcript}"
                    response = chat_with_ai(messages + [{"role": "user", "content": full_query}], personality, ai_model, current_ted_talk_url)
                    
                    print(bold(red("\nAssistant: ")) + apply_markdown_styling(response))
                    
                    messages.append({"role": "assistant", "content": response})

                    markdown_content = extract_markdown(response)
                    if markdown_content:
                        title_prompt = f"Generate a brief, concise title (5 words or less) for this content:\n\n{markdown_content[:200]}..."
                        title_response = chat_with_ai([{"role": "user", "content": title_prompt}], "concise", ai_model, current_ted_talk_url)
                        
                        file_path = generate_markdown_file(markdown_content, title_response, current_ted_talk_url)
                        print(green(f"\nMarkdown file generated: {file_path}\n"))
                    else:
                        print(blue("\nNo Markdown content detected in this response.\n"))

        except KeyboardInterrupt:
            os.system('clear')
            print("\nExiting...")
            time.sleep(1.75)
            os.system('clear')
            sys.exit()

if __name__ == "__main__":
    main()