#!/usr/bin/env python

# Dependencies:
from openai import OpenAI
import argparse
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv
import sys, os, re
import textwrap
import datetime
import tiktoken

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

# chat_with_gpt function
def chat_with_gpt(messages, personality):
    messages.append({"role": "system", "content": f"You are a helpful assistant with a {personality} personality."})
    # init the conversation specifying the personality
    try: # try to get a response from GPT-4o
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e: # if there is an error, return the error message
        return f"Error communicating with GPT-4o: {str(e)}"
    
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
    
    # Write the content to the file
    with open(file_path, 'w') as f:
        f.write(f"# {title}\n\n")
        f.write(content)
    
    return file_path

def process_transcript(chunks, query, personality):
    """Process the transcript, either as a whole or in chunks."""
    if len(chunks) == 1:
        # Process the entire transcript at once
        full_query = f"Based on this transcript, {query}\n\nTranscript:\n{chunks[0]}"
        return chat_with_gpt([{"role": "user", "content": full_query}], personality)
    else:
        # Process in chunks
        combined_response = ""
        for i, chunk in enumerate(chunks):
            chunk_query = f"Based on this part of the transcript, {query}\n\nTranscript part {i+1}:\n{chunk}"
            chunk_response = chat_with_gpt([{"role": "user", "content": chunk_query}], personality)
            combined_response += f"\n\nInsights from part {i+1}:\n{chunk_response}"
        return combined_response   

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
                    transcript_chunks = split_transcript(current_transcript)
                    if len(transcript_chunks) > 1:
                        print(bold(green("New video transcript loaded and split into chunks due to its length. You can now ask questions about this video.")))
                    else:
                        print(bold(green("New video transcript loaded. You can now ask questions about this video.")))
                except Exception as e:
                    print(red(f"Error loading video transcript: {str(e)}"))
                    continue
            else:
                if not current_transcript:
                    print(red("Please load a YouTube video first by pasting its URL."))
                    continue
                
                response = process_transcript(transcript_chunks, user_input, args.personality)
                print(bold(red("\nAssistant: ")) + apply_markdown_styling(response))

                # Check for markdown content in the response
                markdown_content = extract_markdown(response)
                if markdown_content:
                    # Generate a title for the markdown file
                    title_prompt = f"Generate a brief, concise title (5 words or less) for this content:\n\n{markdown_content[:200]}..."
                    title_response = chat_with_gpt([{"role": "user", "content": title_prompt}], "concise")
                    
                    # Generate the markdown file
                    file_path = generate_markdown_file(markdown_content, title_response)
                    print(green(f"\nMarkdown file generated: {file_path}\n"))
                else:
                    print(blue("\nNo Markdown content detected in this response.\n"))

    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()