import os, re
import openai
import argparse
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set the API key from the environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Debug: Print the API key to verify it's loaded correctly
print("API Key:", openai.api_key)

def bold(text):
    return "\033[1m" + text + "\033[0m"

def blue(text):
    return "\033[34m" + text + "\033[0m"

def red(text):
    return "\033[31m" + text + "\033[0m"

def bold(text):
    return re.sub(r'\*\*(.*?)\*\*', r'\033[1m\1\033[0m', text)

def summarise_transcript(user_prompt ,transcript, personality):
    # Generate the initial prompt with the transcript
    initial_prompt = (
        f"You are GPT-4o, a powerful model with a {personality} personality. "
        f"Here is the transcript of a YouTube video: \"{transcript}\". Traverse the transcript then answer this question:{user_prompt}"
    )
    messages = [{"role": "system", "content": initial_prompt}]
    
    # Make the API call with the initial message
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=messages,
    )
    
    # Extract and return the assistant's response
    return response['choices'][0]['message']['content']

def main():
    parser = argparse.ArgumentParser(description="Simple command line YouTube helper with GPT-4o and the respective video transcript.")
    parser.add_argument("--personality", type=str, help="A brief summary of the chatbot's personality", default="friendly and helpful")
    args = parser.parse_args()

    try:
        while True:  # Loop to handle user inputs continuously
            try:
                # Prompt the user for a YouTube URL
                print('\nPaste in the YouTube URL (or type "exit" to quit):')
                url = input().strip()

                if url.lower() == "exit":
                    print("Exiting...")
                    break

                # Extract the video ID from the URL
                video_id = url.split('/')[-1] if 'youtu.be' in url else parse_qs(urlparse(url).query).get('v', [None])[0]

                # Ensure that a video ID was found
                if not video_id:
                    raise ValueError("No video ID found in URL")

                # Get the transcript for the video
                transcript = YouTubeTranscriptApi.get_transcript(video_id)

                # Extract the sentences from the transcript
                sentences = [entry['text'] for entry in transcript]

                # Join the sentences into a single string (transcript)
                entire_transcript = " ".join(sentences)

                # get user_prompt
                user_prompt = input('What would you like to know about the video?: ')

                # Summarise the transcript
                summary = summarise_transcript(user_prompt, entire_transcript, args.personality)

                # Print the summary
                print(bold(red("\nSummary: ")), bold(summary))

            except Exception as e:
                print("An error occurred:", e)

    except KeyboardInterrupt:
        print("Exiting...")

if __name__ == "__main__":
    main()