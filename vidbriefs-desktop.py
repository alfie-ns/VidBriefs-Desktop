#!/usr/bin/env python
# -*- coding: utf-8 -*- 
# Dependencies::
import sys, os, re, time
from openai import OpenAI
import anthropic

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
import textwrap
import datetime
import tiktoken
import argparse

# Load environment variables from .env file
load_dotenv()

# Get OpenAI API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
claude_api_key = os.getenv("ANTHROPIC_API_KEY")
# || api_key = "sk-...J

# Initialise OpenAI client
openai_client = OpenAI(api_key=openai_api_key)
claude_client = anthropic.Anthropic(api_key=claude_api_key)

# Check if running in a terminal that supports formatting
def supports_formatting():
    return sys.stdout.isatty()
           #sys.stdout.isatty() returns True if the file descriptor

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

# ------------------------------------------------------------------------------
# Functions 📼|-------------------------------------------------------------------
# ------------------------------------------------------------------------------

# AI Communication Functions -
def chat_with_ai(messages, personality, ai_model):
    system_message = f"You are a helpful assistant with a {personality} personality."
    
    if ai_model == "gpt":
        try: # try to communicate with GPT-4o-mini
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
            claude_messages = [
                {"role": "user", "content": messages[-1]['content']}
            ]
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

def get_transcript(url):
    video_id = url.split('/')[-1] if 'youtu.be' in url else parse_qs(urlparse(url).query).get('v', [None])[0]
    
    if not video_id:
        raise ValueError("No video ID found in URL")
    
    transcript = YouTubeTranscriptApi.get_transcript(video_id) # Get the transcript for the video
    sentences = [entry['text'] for entry in transcript] # Extract the text into a list of sentences
    return " ".join(sentences) # Join the sentences into a single string

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

def generate_markdown_file(content, title):
    """Generate a Markdown file with the given content and title in a 'Markdown' folder."""
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
    
    return file_path

# ------------------------------------------------------------------------------
# Main Program: 

def main():
    while True:  # Outer loop for restart 'break' functionality
        os.system('clear')
        # ----------------- Main Program -----------------

        print(bold(blue("\nYoutube Transcript AI Assistant\n")))
        
        ai_model = input(bold("Choose your AI model (gpt/claude): ")).strip().lower() # Ask user to choose AI model, strip whitespace and convert to lowercase
        while ai_model not in ["gpt", "claude"]:
            print(red("Invalid choice. Please enter 'gpt' or 'claude'."))
            ai_model = input(bold("Choose your AI model (gpt/claude): ")).strip().lower()

        # Personalise assistant ------------------------------------------------

        personality_choice = input(bold(textwrap.dedent("""
        How would you like to personalise the assistant?
        (Feel free to describe the personality in your own words, or use the suggestions below)

        You can specify intensity levels (LOW, MEDIUM, HIGH) and combine traits as you wish.
        
        Examples: ----------------------------------------------------------------
        - 'FRIENDLY and HELPFUL with a touch of HUMOR'
        - 'PROFESSIONAL and INFORMATIVE with a hint of SARCASM'
        - 'CASUAL and ENGAGING with a focus on PRACTICALITY'                                                                                                     
        - 'HIGH summarizer and MEDIUM explainer'
        - 'LOW questioner with HIGH practical focus'
        - 'MEDIUM friendly and HIGH professional'
        - 'mentor with a focus on practical applications'

        Learning trait suggestions (feel free to use your own):
        ---------------------------------------------------------------------------
        Communication:
        - informative    - engaging       - persuasive     - critical
        - concise        - analytical     - descriptive    - eloquent

        Style:
        - creative       - technical      - casual         - formal
        - friendly       - professional   - humorous       - serious

        Approach:
        - teaching       - mentoring      - motivational   - skeptical
        - empathetic     - logical        - practical      - academic

        Focus:
        - summarizing    - explaining     - contextualizing - questioning
        - comparing      - historical     - visual         - socratic
        - analogical     - fact-checking  - multidisciplinary
        ----------------------------------------------------------------------------

        (BE AS CREATIVE AS YOU LIKE TO ENSURE OPTIMAL LEARNING EFFICACY) 
        
        Your choice:                                                       
                                                        
        """)))

        personality = personality_choice or "friendly and helpful" # Default personality

        print(f"\nGreat! Your {ai_model.upper()} assistant will be", bold(personality))
        print("Paste a YouTube URL to start chatting about videos of your interest.")
        print("Type 'exit' to quit the program or 'restart' to start over.")

        messages = [] # init as empty list
        current_transcript = "" # init as empty string
        transcript_chunks = [] # init as empty list

        try: # Inner loop for conversation functionality
            while True:
                user_input = input(bold("\nEnter a YouTube URL, your message, 'restart', or 'exit': ")).strip()

                if user_input.lower() == 'exit':
                    print("Exiting...")
                    sys.exit()

                if user_input.lower() == "restart":
                    print(bold(green("Restarting the assistant...")))
                    break  # Break the inner loop to restart

                if 'youtube.com' in user_input or 'youtu.be' in user_input:
                    try:
                        current_transcript = get_transcript(user_input)
                        transcript_chunks = split_transcript(current_transcript)
                        if len(transcript_chunks) > 1:
                            print(bold(green("New video transcript loaded and split into chunks due to its length. You can now ask questions about this video.")))
                        else:
                            print(bold(green("New video transcript loaded. You can now ask questions about this video.")))
                        messages = []  # Reset conversation history for new video
                    except Exception as e:
                        print(red(f"Error loading video transcript: {str(e)}"))
                        continue
                else:
                    if not current_transcript:
                        print(red("Please load a YouTube video first by pasting its URL."))
                        continue
                    
                    # Add user message to conversation history
                    messages.append({"role": "user", "content": user_input})
                    
                    # Process the transcript with the entire conversation history
                    full_query = f"Based on this transcript and our conversation so far, please respond to the latest message: {user_input}\n\nTranscript:\n{current_transcript}"
                    response = chat_with_ai(messages + [{"role": "user", "content": full_query}], personality, ai_model)
                    
                    print(bold(red("\nAssistant: ")) + apply_markdown_styling(response))
                    
                    # Add assistant's response to conversation history
                    messages.append({"role": "assistant", "content": response})

                    # Check for markdown content in the response
                    markdown_content = extract_markdown(response)
                    if markdown_content:
                        title_prompt = f"Generate a brief, concise title (5 words or less) for this content:\n\n{markdown_content[:200]}..."
                        title_response = chat_with_ai([{"role": "user", "content": title_prompt}], "concise", ai_model)
                        
                        file_path = generate_markdown_file(markdown_content, title_response)
                        print(green(f"\nMarkdown file generated: {file_path}\n"))
                    else:
                        print(blue("\nNo Markdown content detected in this response.\n"))

        except KeyboardInterrupt:
            print("\nExiting...")
            os.system('clear')
            sys.exit()
            

if __name__ == "__main__":
    main()