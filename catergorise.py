#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Constants
CATEGORIES = [
    "CompSci", 
    "AI & Machine Learning",
    "Gaming",
    "Health & Medicine",
    "Fitness & Nutrition",
    "Neuroscience",
    "Sports",
    "Technology",
    "Politics & Current Events",
    "Economics & Finance",
    "History",
    "Investing",
    "Military & Defense",
    "Entertainment",
    "Science",
    "Mental Health",
    "Cybersecurity",
    "Environmental Science",
    "Social Issues",
    "Business & Entrepreneurship",
    "Education",
    "Travel",
    "Other"
]
MARKDOWN_DIR = "Markdown"
CATEGORIES_DIR = "Categories"

def categorise_with_ai(content):
    prompt = f"Categorize the following content into one of these categories: {', '.join(CATEGORIES)}. Respond with just the category name.\n\nContent: {content[:500]}..."
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Updated to a more recent model
            messages=[
                {"role": "system", "content": "You are a helpful assistant that categorises content into their respective categories."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10
        )
        category = response.choices[0].message.content.strip()
        return category if category in CATEGORIES else "Other"
    except Exception as e:
        print(f"Error in AI categorization: {e}")
        return "Other"

def get_markdown_files():
    return [f for f in os.listdir(MARKDOWN_DIR) if f.endswith('.md')]

def read_markdown_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def move_file(source, destination):
    shutil.move(source, destination)

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    markdown_files = get_markdown_files()
    
    for file in markdown_files: # for each markdown file
        file_path = os.path.join(script_dir, MARKDOWN_DIR, file) # file path = 
        content = read_markdown_content(file_path) # read the content of the file
        
        category = categorise_with_ai(content) # categorise file into respective category
        
        destination_folder = os.path.join(script_dir, CATEGORIES_DIR, category)
        destination_path = os.path.join(destination_folder, file)
        
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
            print(f"\nCreated category folder: {destination_folder}\n")
        
        try: # try to move into respective category, catch error and print if exception
            move_file(file_path, destination_path)
            print(f"Moved {file} to {os.path.relpath(destination_path, script_dir)}")
        except Exception as e:
            print(f"Error moving {file}: {e}")

if __name__ == "__main__":
    main()