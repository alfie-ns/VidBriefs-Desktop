#!/usr/bin/env python
# -*- coding: utf-8 -*-

# sight.py

import os
import random
import datetime
from dotenv import load_dotenv
from openai import OpenAI
import anthropic

# Load environment variables
load_dotenv()

# Initialize AI clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
claude_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def fetch_data(directory):
    """Fetch all files from a given directory."""
    full_path = os.path.join("sight-repo", "data", directory)
    return [f for f in os.listdir(full_path) if os.path.isfile(os.path.join(full_path, f))]

def fetch_transcripts():
    """Fetch transcripts from sight-repo/data/transcripts/"""
    return fetch_data("transcripts")

def fetch_metadata():
    """Fetch metadata files."""
    return fetch_data("metadata")

def fetch_annotations():
    """Fetch annotation files."""
    return fetch_data("annotations")

def fetch_comments():
    """Fetch comment files."""
    return fetch_data("comments")

def choose_random_data():
    """Randomly select a data point and its corresponding files."""
    transcripts = fetch_transcripts()
    metadata = fetch_metadata()
    annotations = fetch_annotations()
    comments = fetch_comments()
    
    # Choose a random transcript
    transcript = random.choice(transcripts)
    base_name = transcript.split('.')[0]
    
    # Find corresponding files
    corresponding_metadata = next((m for m in metadata if m.startswith(base_name)), None)
    corresponding_annotation = next((a for a in annotations if a.startswith(base_name)), None)
    corresponding_comment = next((c for c in comments if c.startswith(base_name)), None)
    
    return transcript, corresponding_metadata, corresponding_annotation, corresponding_comment

def read_file_content(filepath):
    """Read and return the content of a file."""
    full_path = os.path.join("sight-repo", "data", filepath)
    with open(full_path, 'r') as file:
        return file.read()

def chat_with_ai(messages, ai_model):
    """Interact with the chosen AI model."""
    if ai_model == "gpt":
        try:
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
                messages=claude_messages
            )
            return response.content[0].text
        except Exception as e:
            return f"Error communicating with Claude: {str(e)}"
    else:
        return "Invalid AI model selected."

def generate_markdown_file(content, title):
    """Generate a Markdown file with the given content and title."""
    folder_name = "Markdown"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{title}_{timestamp}.md"
    file_path = os.path.join(folder_name, filename)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n\n")
        f.write(content)
    
    return file_path

def main():
    print("\033[1m\033[34mWelcome to the Sight AI Assistant!\033[0m")
    
    ai_model = input("\033[1mChoose your AI model (gpt/claude): \033[0m").strip().lower()
    while ai_model not in ["gpt", "claude"]:
        print("\033[31mInvalid choice. Please enter 'gpt' or 'claude'.\033[0m")
        ai_model = input("\033[1mChoose your AI model (gpt/claude): \033[0m").strip().lower()

    while True: # [ ] Expensive, change to only search for what it needs to
        transcript, metadata_file, annotation_file, comment_file = choose_random_data()
        
        transcript_content = read_file_content(os.path.join("transcripts", transcript))
        metadata_content = read_file_content(os.path.join("metadata", metadata_file)) if metadata_file else "No metadata available."
        annotation_content = read_file_content(os.path.join("annotations", annotation_file)) if annotation_file else "No annotations available."
        comment_content = read_file_content(os.path.join("comments", comment_file)) if comment_file else "No comments available."

        prompt = f"""Analyze the following data:

            Transcript:
            {transcript_content}

            Metadata:
            {metadata_content}

            Annotations:
            {annotation_content}

            Comments:
            {comment_content}

            Provide insights and analysis based on this information, then 
            begin conversatiting with the user regarding the insights.
        """

        response = chat_with_ai([{"role": "user", "content": prompt}], ai_model)
        print("\033[1m\033[32m\nAI Analysis:\033[0m")
        print(response)

        # Save the response to a markdown file
        file_path = generate_markdown_file(response, f"AI_Analysis_{ai_model}")
        print(f"\033[34m\nExtensive response saved to: {file_path}\033[0m")

        user_input = input("\033[1m\nEnter your question about the analysis (or 'exit' to quit): \033[0m")
        if user_input.lower() == 'exit':
            break

        follow_up_prompt = f"Based on the previous analysis, answer the following question: {user_input}"
        follow_up_response = chat_with_ai([{"role": "user", "content": follow_up_prompt}], ai_model)
        print("\033[1m\033[32m\nAI Response:\033[0m")
        print(follow_up_response)

        # Save the follow-up response to a markdown file
        follow_up_file_path = generate_markdown_file(follow_up_response, f"Follow_Up_Response_{ai_model}")
        print(f"\033[34m\nFollow-up response saved to: {follow_up_file_path}\033[0m")

if __name__ == "__main__":
    main()