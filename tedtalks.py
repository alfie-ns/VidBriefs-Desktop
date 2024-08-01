#!/usr/bin/env python
# -*- coding: utf-8 -*- 

# Dependencies ------------------------------------------------------------------
import sys, os, re, time, random # system operations, regular expressions, time, and random selection
from dotenv import load_dotenv # for loading environment variables from .env file

# --------------AI APIS----------------

from openai import OpenAI
import anthropic

# --------------TED Talk Data----------------

import pandas as pd # for reading CSV files if needed

# --------------formatting dependencies----------------

import textwrap # for text formatting
import datetime # for timestamping files
import tiktoken # for tokenizing text
import argparse # for command-line arguments

# ------------------------------------------------------------------------------
# tedbriefs.py 🟣 -------------------------------------------------------
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
def chat_with_ai(messages, personality, ai_model, ted_talk_title):
    system_message = f"You are a helpful assistant with a ({personality}) personality, you will provide the user markdown formatting for the users learning experience."
    instruction = f"You will assist the user regarding their questions about the TED talk titled '{ted_talk_title}'. Provide insightful analysis and relate the talk's content to real-world applications when appropriate."
    
    if ai_model == "gpt": # if user chooses gpt-4o-mini
        try:
            messages.insert(0, {"role": "system", "content": system_message + " " + instruction})
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini", #£0.460 / 1M output tokens
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error communicating with GPT: {str(e)}"
    elif ai_model == "claude":
        try:  
                                      # Claude is 5x more expensive
            claude_messages = [
                {"role": "user", "content": messages[-1]['content']}
            ]
            response = claude_client.messages.create( # -- EXPENSIVE --
                model="claude-3-5-sonnet-20240620", #Input: £2.30 per million tokens
	 	                                            #Output: £11.60 per million tokens
                max_tokens=1000,
                system=system_message + " " + instruction,
                messages=claude_messages
            )
            return response.content[0].text
        except Exception as e:
            return f"Error communicating with Claude: {str(e)}"
    else:
        return "Invalid AI model selected."

# TED Talk Processing Functions -------------------------------------------------

def get_ted_talk_content(talk_title): # --Systematic Traversal--
    """Fetch and return the content of a TED talk given its title."""
    for root, dirs, files in os.walk("TED-talks"): # Recursively walk through the TED-talks directory
        for file in files: # For each file in the current directory
            if file.endswith(".md") and talk_title in file: # If the file is a Markdown file and its name contains the talk title
                with open(os.path.join(root, file), 'r') as f: # Open the file for reading
                    return f.read() # Read and return the entire content of the file
    return "Talk content not found." # If no matching file is found, return this message

def get_all_talk_titles(): # --Breadth-First Processing of Depth-First Traversal--
    """Get all available TED talk titles from the local directory.
    """
    titles = []
    for root, dirs, files in os.walk("TED-talks"):
        for file in files:
            if file.endswith(".md"):
                titles.append(file[:-3])  # Remove .md extension
    return titles

def recommend_ted_talk(user_interests, all_talks): # ???
    """Recommend a TED talk based on user interests."""
    relevant_talks = [talk for talk in all_talks if any(interest.lower() in talk.lower() for interest in user_interests)]
    return random.choice(relevant_talks) if relevant_talks else random.choice(all_talks)

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
    '''
    The slugify function converts a string into a simplified, URL-friendly format:
    slug = clean string suitable for filenames or URLs.
    For example: "Hello, World!" becomes "hello-world".
    '''
    # Convert to lowercase
    text = text.lower()
    # Remove non-word characters (everything except numbers and letters)
    text = re.sub(r'[^\w\s-]', '', text)
    # Replace all spaces with hyphens
    text = re.sub(r'\s+', '-', text)
    return text

def generate_markdown_file(content, title): # NEED TO GET WORKING
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
# Main 🟥 ---------------------------------------------------------------------- 
# ------------------------------------------------------------------------------
def main():
    all_talks = get_all_talk_titles()

    while True:  # Outer loop for restart 'break' functionality
        os.system('clear')
        # ----------------- Main Program -----------------
        print(bold(blue("\nTED Talk Analysis Assistant\n")))
        
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
        
        user_interests = input(bold("Enter your interests (comma-separated) for TED talk recommendations: ")).split(',')
        recommended_talk = recommend_ted_talk(user_interests, all_talks)
        print(green(f"\nRecommended TED Talk: {recommended_talk}"))
        print("You can start discussing this talk or choose another one.")
        print("Type 'list' to see all available talks, 'recommend' for a new recommendation,")
        print("'exit' to quit the program, or 'restart' to start over.")

        messages = []
        current_talk = recommended_talk

        try:  # Inner loop for conversation functionality
            while True:
                user_input = input(bold("\nEnter your message, 'list', 'recommend', 'restart', or 'exit': ")).strip()

                if user_input.lower() == 'exit':
                    os.system('clear')
                    print("\nExiting...")
                    time.sleep(1.5)
                    os.system('clear')
                    sys.exit()

                if user_input.lower() == "restart":
                    print(bold(green("Restarting the assistant...")))
                    break  # Break the inner loop to restart

                if user_input.lower() == 'list':
                    print("\nAvailable TED Talks:")
                    for talk in all_talks:
                        print(talk)
                    continue

                if user_input.lower() == 'recommend':
                    recommended_talk = recommend_ted_talk(user_interests, all_talks)
                    print(green(f"\nRecommended TED Talk: {recommended_talk}"))
                    current_talk = recommended_talk
                    messages = []  # Reset conversation for new talk
                    continue

                if user_input in all_talks:
                    current_talk = user_input
                    print(green(f"\nSwitched to TED talk: {current_talk}"))
                    messages = []  # Reset conversation for new talk
                    continue
                
                # Process user input and get AI response
                messages.append({"role": "user", "content": user_input})
                
                full_query = f"Based on the TED talk '{current_talk}', please respond to: {user_input}"
                response = chat_with_ai(messages + [{"role": "user", "content": full_query}], personality, ai_model, current_talk)
                
                print(bold(red("\nAssistant: ")) + apply_markdown_styling(response))
                
                messages.append({"role": "assistant", "content": response})

                # Check for markdown content in the response
                markdown_content = extract_markdown(response)
                if markdown_content:
                    title_prompt = f"Generate a brief, concise title (5 words or less) for this content:\n\n{markdown_content[:200]}..."
                    title_response = chat_with_ai([{"role": "user", "content": title_prompt}], "concise", ai_model, current_talk)
                    
                    file_path = generate_markdown_file(markdown_content, title_response)
                    print(green(f"\nMarkdown file generated: {file_path}\n"))
                else:
                    print(blue("\nNo Markdown content detected in this response.\n"))

        except KeyboardInterrupt:  # Handle Ctrl+C to exit the program
            os.system('clear')
            print("\nExiting...")
            time.sleep(1.75)
            os.system('clear')
            sys.exit()

if __name__ == "__main__":  # Run the main function if the script is executed directly
    main()