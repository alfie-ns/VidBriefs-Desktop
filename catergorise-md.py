#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Dependencies:
import os
import shutil
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Constants
CATEGORIES = ["CompSci", "Gaming", "Health"]
MARKDOWN_DIR = "Markdown"

# AI Communication Function --------------------------------------------------
def categorise_with_ai(content):
    """Use AI to categorize the content into CompSci, Gaming, or Health."""
    prompt = f"Categorize the following content into one of these categories: {', '.join(CATEGORIES)}. Respond with just the category name.\n\nContent: {content[:500]}..."  # Limit content to 500 chars
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # You can change this to a different model if needed
            messages=[
                {"role": "system", "content": "You are a helpful assistant that categorises content."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10 # limit response to 10 tokens because we only need the category name
        )
        category = response.choices[0].message.content.strip()
        return category if category in CATEGORIES else "Uncategorized"
    except Exception as e:
        print(f"Error in AI categorization: {e}")
        return "Uncategorized"

# File Processing Functions --------------------------------------------------
def get_markdown_files():
    """Get all Markdown files in the Markdown directory."""
    return [f for f in os.listdir(MARKDOWN_DIR) if f.endswith('.md')]

def read_markdown_content(file_path):
    """Read the content of a Markdown file."""
    with open(file_path, 'r') as file:
        return file.read()

def create_category_folders():
    """Create folders for each category if they don't exist."""
    for category in CATEGORIES + ["Uncategorized"]:
        os.makedirs(os.path.join(os.path.dirname(MARKDOWN_DIR), category), exist_ok=True)

def move_file(source, destination):
    """Move a file from source to destination."""
    shutil.move(source, destination)

# Main function --------------------------------------------------------------
def main():
    create_category_folders()
    markdown_files = get_markdown_files() # Get all Markdown files in the Markdown directory
    
    for file in markdown_files: # for (const auto& entry : std::filesystem::directory_iterator(MARKDOWN_DIR)) {
        file_path = os.path.join(MARKDOWN_DIR, file)
        content = read_markdown_content(file_path) # Read the content of the Markdown file
        
        category = categorise_with_ai(content) # Categorise the content using gp-4o-mini
        
        destination_folder = os.path.join(os.path.dirname(MARKDOWN_DIR), category)
        destination_path = os.path.join(destination_folder, file)
        
        move_file(file_path, destination_path)
        print(f"Moved {file} to {category}")

if __name__ == "__main__":
    main()