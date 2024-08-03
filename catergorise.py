#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Dependencies:
import os, time
import shutil
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Constants
CATEGORIES = ["CompSci", "Gaming", "Health", "Other", "Sports"]
MARKDOWN_DIR = "Markdown"
CATEGORIES_DIR = "Categories"  # The directory containing all category folders

# AI Communication Function --------------------------------------------------
def categorise_with_ai(content):
    """Use AI to categorize the content into CompSci, Gaming, Health, Sports, or Other."""
    prompt = f"Categorize the following content into one of these categories: {', '.join(CATEGORIES)}. Respond with just the category name.\n\nContent: {content[:500]}..."  # Limit content to 500 chars
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that categorises content."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10 # limit response to 10 tokens because we only need the category name
        )
        category = response.choices[0].message.content.strip()
        return category if category in CATEGORIES else "Other"
    except Exception as e:
        print(f"Error in AI categorization: {e}")
        return "Other"

# File Processing Functions --------------------------------------------------
def get_markdown_files():
    """Get all Markdown files in the Markdown directory."""
    return [f for f in os.listdir(MARKDOWN_DIR) if f.endswith('.md')] # If file in markdown ends with .md, include​​​​​​​​​​​​​​​​

def read_markdown_content(file_path):
    """Read the content of a Markdown file."""
    with open(file_path, 'r') as file:
        return file.read()

def move_file(source, destination):
    """Move a file from source to destination."""
    shutil.move(source, destination)

# Main function --------------------------------------------------------------
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    markdown_files = get_markdown_files()
    
    for file in markdown_files:
        file_path = os.path.join(script_dir, MARKDOWN_DIR, file)
        content = read_markdown_content(file_path)
        
        category = categorise_with_ai(content)
        
        destination_folder = os.path.join(script_dir, CATEGORIES_DIR, category)
        destination_path = os.path.join(destination_folder, file)
        
        if os.path.exists(destination_folder):
            move_file(file_path, destination_path)
            print(f"Moved {file} to {CATEGORIES_DIR}/{category}")
        else:
            print(f"Category folder {CATEGORIES_DIR}/{category} does not exist. Keeping {file} in Markdown folder.")
    time.sleep(5.75)
    os.system('clear')

if __name__ == "__main__":
    main()