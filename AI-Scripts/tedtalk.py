#!/usr/bin/env python
# -*- coding: utf-8 -*- 

# VidBriefs-Desktop/AI-Scripts/tedtalk.py

# Dependencies ------------------------------------------------------------------
import sys, os, re, time, random, textwrap # system operations, regular expressions, time, and random selection
from dotenv import load_dotenv # for loading environment variables from .env file
from functools import partial # for creating partial functions [ ]
from datetime import datetime # for timestamping files

# --------------AI APIS----------------

from openai import OpenAI
import anthropic

# --------------TED Talk Data----------------

import pandas as pd # for reading CSV files if needed

# --------------formatting dependencies----------------

import textwrap # for text formatting
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
def chat_with_ai(messages, personality, ai_model, ted_talk_title, talk_number=None):
    system_message = generate_system_message(personality)
    instruction = f"You will assist the user regarding their questions about the TED talk titled '{ted_talk_title}'. "
    if talk_number:
        instruction += f"This talk was number {talk_number} in the list of recommendations. "
    instruction += "Provide insightful analysis and relate the talk's content to real-world applications when appropriate. Always stay focused on this specific talk unless explicitly told otherwise."

    if ai_model == "gpt":
        try:
            messages.insert(0, {"role": "system", "content": system_message + " " + instruction})
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
                model="claude-3-5-sonnet-20240620",
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
def generate_system_message(personality):
    base_message = "You are an AI assistant helping with TED talk analysis."
    personality_traits = parse_personality(personality)
    
    instructions = []
    for trait, intensity in personality_traits.items():
        if trait == "ANALYTICAL":
            instructions.append(f"{intensity} Provide detailed, logical breakdowns of concepts.")
        elif trait == "CREATIVE":
            instructions.append(f"{intensity} Offer unique perspectives and unconventional ideas.")
        elif trait == "SOCRATIC":
            instructions.append(f"{intensity} Ask thought-provoking questions to deepen the discussion.")
        elif trait == "MULTIDISCIPLINARY":
            instructions.append(f"{intensity} Draw connections between different fields and contexts.")
        elif trait == "ACADEMIC":
            instructions.append(f"{intensity} Use scholarly language and cite relevant research.")
        elif trait == "EMPATHETIC":
            instructions.append(f"{intensity} Show understanding and relate to the human experience.")
        elif trait == "INNOVATIVE":
            instructions.append(f"{intensity} Propose novel solutions and cutting-edge applications.")
        elif trait == "DATA-DRIVEN":
            instructions.append(f"{intensity} Base arguments on quantitative evidence and statistics.")
        elif trait == "PROBLEM-SOLVING":
            instructions.append(f"{intensity} Focus on practical applications and solutions.")
    
    examples = get_personality_examples(personality_traits)
    
    return f"{base_message}\n\nPersonality Instructions:\n" + "\n".join(instructions) + "\n\nExamples:\n" + examples

def get_personality_examples(traits):
    examples = {
        "ANALYTICAL": "User: 'Summarize the talk'\nAI: 'The talk can be broken down into three main arguments: 1)..., 2)..., 3)...'",
        "CREATIVE": "User: 'What's interesting about this?'\nAI: 'Imagine if we applied the speaker's idea to deep-sea exploration. We might discover...'",
        "SOCRATIC": "User: 'Tell me about the talk'\nAI: 'Before I do, what aspect of the talk intrigued you most? This will help me tailor my explanation.'",
        "MULTIDISCIPLINARY": "User: 'How is this relevant?'\nAI: 'This concept intersects with fields such as psychology, economics, and environmental science. For instance,...'",
        "ACADEMIC": "User: 'What's the significance?'\nAI: 'According to a study by Smith et al. (2020), this approach has shown a 40% increase in efficiency...'",
        "EMPATHETIC": "User: 'Why should I care?'\nAI: 'Consider how this might affect your daily life. For many, this concept resonates with the challenge of...'",
        "INNOVATIVE": "User: 'What's next?'\nAI: 'Building on this idea, we could develop a novel system that combines AI and biotechnology to...'",
        "DATA-DRIVEN": "User: 'Is this effective?'\nAI: 'Data from 50 countries shows a strong correlation (r=0.85) between this approach and improved outcomes...'",
        "PROBLEM-SOLVING": "User: 'How can we apply this?'\nAI: 'Let's break this down into actionable steps: 1) Identify the core issue, 2) Adapt the speaker's method to...'"
    }
    return "\n\n".join(examples[trait] for trait, intensity in traits.items() if trait in examples)

def parse_personality(personality_string):
    traits = {}
    pattern = r'(LOW|MEDIUM|HIGH|BALANCED)?\s*([🧠🎨🗣️🌐📚🤔🤝💡📊🧩]\s*)?(\w+)'
    matches = re.findall(pattern, personality_string, re.IGNORECASE)
    
    for intensity, emoji, trait in matches:
        intensity = intensity.upper() if intensity else "MEDIUM"
        trait = trait.upper()
        traits[trait] = intensity
    
    return traits

def optimized_recommend_ted_talks(user_interests, all_talks, num_initial_filter=10, num_final_recommendations=3, ai_model="gpt", personality="BALANCED 🧠 ANALYTICAL-🎨 CREATIVE with HIGH 🌐 MULTIDISCIPLINARY focus"):
    # Step 1: Initial filtering based on keyword matching
    filtered_talks = initial_filter_talks(user_interests, all_talks, num_initial_filter)
    
    # Step 2: AI review of filtered talks
    ai_recommended_talks = ai_review_talks(filtered_talks, user_interests, num_final_recommendations, ai_model, personality)
    
    return ai_recommended_talks

def initial_filter_talks(user_interests, all_talks, num_filter):
    """Filter talks based on keyword matching with user interests."""
    relevant_talks = []
    for talk in all_talks:
        content = get_talk_preview(talk, max_length=500)  # Get a longer preview for initial filtering
        relevance_score = calculate_relevance_score(content, user_interests, talk)
        if relevance_score > 0:
            relevant_talks.append((talk, relevance_score))
    
    relevant_talks.sort(key=lambda x: x[1], reverse=True)
    return [talk for talk, _ in relevant_talks[:num_filter]]

def calculate_relevance_score(content, interests, talk_title):
    """Calculate relevance score based on content matching and position of matches."""
    score = 0
    content_lower = content.lower()
    title_lower = talk_title.lower()
    
    for interest in interests:
        interest_lower = interest.lower()
        if interest_lower in title_lower:
            score += 5  # Higher score for title matches
        if interest_lower in content_lower:
            score += 1
            # Check if interest is in the first paragraph (assuming paragraphs are separated by double newlines)
            if interest_lower in content_lower.split('\n\n')[0]:
                score += 2
    
    return score

def ai_review_talks(filtered_talks, user_interests, num_recommendations, ai_model, personality):
    """Use AI to review filtered talks and make final recommendations."""
    previews = []
    for talk in filtered_talks:
        preview = get_talk_preview(talk, max_length=300)
        previews.append(f"Talk: {talk}\nPreview: {preview}\n")
    
    interests_str = ", ".join(user_interests)
    query = f"Given the following TED talk previews and the user's interests ({interests_str}), select the {num_recommendations} most relevant and insightful talks. For each selected talk, provide a brief explanation of why it's relevant to the user's interests. Format your response as a list of tuples, each containing the talk title and the explanation."
    
    full_content = "TED Talk Previews:\n\n" + "\n".join(previews)
    
    ai_response = chat_with_ai([{"role": "user", "content": full_content + "\n\n" + query}], personality, ai_model, "TED Talk Selection")
    
    # Parse AI response to extract recommendations
    recommendations = parse_ai_recommendations(ai_response)
    
    return recommendations[:num_recommendations]

def parse_ai_recommendations(ai_response):
    """Parse the AI's response to extract recommendations."""
    # This is a simple parser and might need to be adjusted based on the actual AI output format
    recommendations = []
    lines = ai_response.split('\n')
    current_talk = ""
    current_explanation = ""
    for line in lines:
        if line.startswith("Talk:"):
            if current_talk:
                recommendations.append((current_talk, current_explanation.strip()))
            current_talk = line[5:].strip()
            current_explanation = ""
        else:
            current_explanation += line + " "
    if current_talk:
        recommendations.append((current_talk, current_explanation.strip()))
    return recommendations

def get_ted_talk_content(talk_title): # --Systematic Traversal--
    """Fetch and return the content of a TED talk given its title."""
    for root, dirs, files in os.walk("config/TED-talks"): # Recursively walk through the TED-talks directory
        for file in files: # For each file in the current directory
            if file.endswith(".md") and talk_title in file: # If the file is a Markdown file and its name contains the talk title
                with open(os.path.join(root, file), 'r') as f: # Open the file for reading
                    return f.read() # Read and return the entire content of the file
    return "Talk content not found." # If no matching file is found, return this message

def get_all_talk_titles(): # --Breadth-First Processing of Depth-First Traversal--
    """
    Grabs all TED talk titles from local folders. It's a mix:
    1. os.walk() goes through directories depth-first.
    2. We process all files in each directory before moving on.
    
    So it checks all files in a folder before diving into subfolders.

    Breadth-first essentially means in the traversal it will first check siblings
    before the next group.

    Example: If TED-talks has A, B, C folders, and A has 1.md, 2.md:
    It'll process 1.md and 2.md in A before moving to folder B.
    """
    titles = []
    for root, dirs, files in os.walk("config/TED-talks"):
        for file in files:
            if file.endswith(".md"):
                titles.append(file[:-3])  # Remove .md extension
    return titles

def recommend_ted_talks(user_interests, all_talks, num_recommendations=3):
    """Recommend multiple TED talks based on user interests by examining talk content."""
    relevant_talks = []
    
    for talk in all_talks:
        content = get_ted_talk_content(talk)
        
        # Convert content and interests to lowercase for case-insensitive matching
        content_lower = content.lower()
        interests_lower = [interest.lower() for interest in user_interests]
        
        # Calculate relevance score based on number of matches and their positions
        relevance_score = 0
        for interest in interests_lower:
            if interest in content_lower:
                relevance_score += 1
                # Give higher score if interest is found in the title or first paragraph
                if interest in talk.lower() or interest in content_lower.split('\n')[0]:
                    relevance_score += 2
        
        if relevance_score > 0:
            relevant_talks.append((talk, relevance_score))
    
    # Sort relevant talks by relevance score, highest first
    relevant_talks.sort(key=lambda x: x[1], reverse=True)
    
    # Select top recommendations
    recommendations = [talk for talk, score in relevant_talks[:num_recommendations]]
    
    # If we don't have enough relevant talks, add random selections
    if len(recommendations) < num_recommendations:
        remaining_talks = [talk for talk in all_talks if talk not in recommendations]
        recommendations.extend(random.sample(remaining_talks, num_recommendations - len(recommendations)))
    
    return recommendations

# Helper function to get a preview of the talk content
def get_talk_preview(talk_title, max_length=300):
    """Get a preview of the talk content."""
    content = get_ted_talk_content(talk_title)
    paragraphs = content.split('\n\n')
    
    preview = ""
    for para in paragraphs:
        if len(preview) + len(para) <= max_length:
            preview += para + "\n\n"
        else:
            remaining = max_length - len(preview)
            preview += para[:remaining] + "..."
            break
    
    return preview.strip()

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
    
    #folder_name = "../Markdown" would have to do this if this is ran inside the AI-Scripts folder
    folder_name ="Markdown"
    
    # Create the folder if it doesn't exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    # Generate a slug for the filename
    slug = slugify(title)
    
    # Create a unique filename with a timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
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

    if not all_talks:
        print(red("Error: No TED talks found. Please check the 'TED-talks' directory."))
        print("Make sure you have .md files in the TED-talks directory or its subdirectories.")
        return

    while True:  # Outer loop for restart functionality
        os.system('clear')
        print(bold(blue("\nTED Talk Analysis Assistant\n")))
        
        ai_model = input(bold("Choose your AI model (gpt/claude): ")).strip().lower()
        while ai_model not in ["gpt", "claude"]:
            print(red("Invalid choice. Please enter 'gpt' or 'claude'."))
            ai_model = input(bold("Choose your AI model (gpt/claude): ")).strip().lower()

        # Personalise assistant with detailed prompt
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
        parsed_personality = parse_personality(personality)
        
        print(f"\nGreat! Your {ai_model.upper()} assistant will have the following traits:")
        for trait, intensity in parsed_personality.items():
            print(f"- {intensity} {trait}")

        user_interests = input(bold("\nEnter your interests (comma-separated) for TED talk recommendations, or press Enter for random recommendations: ")).split(',')
        user_interests = [interest.strip() for interest in user_interests if interest.strip()]

        if user_interests:
            recommended_talks = recommend_ted_talks(user_interests, all_talks)
            if recommended_talks:
                print(green("\nRecommended TED Talks based on your interests:"))
            else:
                #print(yellow("\nNo talks matched your interests. Here are some random selections:"))
                recommended_talks = random.sample(all_talks, min(3, len(all_talks)))
        else:
            recommended_talks = random.sample(all_talks, min(3, len(all_talks)))
            print(green("\nRandomly selected TED Talks:"))

        for i, talk in enumerate(recommended_talks, 1):
            preview = get_talk_preview(talk)
            print(f"{i}. {talk}")
            print(f"   Preview: {preview}\n")

        print("\nYou can start discussing any of these talks or choose another one.")
        print("Type a number to select a talk, 'list' to see all available talks, 'recommend' for new recommendations,")
        print("'exit' to quit the program, or 'restart' to start over.")

        messages = []
        current_talk = recommended_talks[0]
        current_talk_number = 1

        try:  # Inner loop for conversation functionality
            while True:
                user_input = input(bold("\nEnter your message, a number to select a talk, 'list', 'recommend', 'restart', or 'exit': ")).strip()

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
                    recommended_talks = recommend_ted_talks(user_interests, all_talks)
                    print(green("\nRecommended TED Talks:"))
                    for i, talk in enumerate(recommended_talks, 1):
                        print(f"{i}. {talk}")
                    current_talk = recommended_talks[0]
                    current_talk_number = 1
                    messages = []  # Reset conversation for new talk
                    continue

                if user_input.isdigit() and 1 <= int(user_input) <= len(recommended_talks):
                    current_talk_number = int(user_input)
                    current_talk = recommended_talks[current_talk_number - 1]
                    print(green(f"\nSwitched to TED talk: {current_talk}"))
                    messages = []
                    continue

                if user_input in all_talks:
                    current_talk = user_input
                    current_talk_number = None
                    print(green(f"\nSwitched to TED talk: {current_talk}"))
                    messages = []
                    continue

                # Process user input and get AI response
                messages.append({"role": "user", "content": user_input})

                full_query = f"Based on the TED talk '{current_talk}' (which was number {current_talk_number} in the list of recommendations), please respond to: {user_input}"
                response = chat_with_ai(messages + [{"role": "user", "content": full_query}], personality, ai_model, current_talk, current_talk_number)

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

        except KeyboardInterrupt:
            os.system('clear')
            print("\nExiting...")
            time.sleep(.5)
            os.system('clear')
            sys.exit()

if __name__ == "__main__":
    main()