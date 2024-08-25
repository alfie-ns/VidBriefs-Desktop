#!/usr/bin/env python3

import os
import sys
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import textwrap
import requests
from datetime import datetime

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_video_id(url):
    """Extract video ID from YouTube URL"""
    if 'youtu.be' in url:
        return url.split('/')[-1]
    else:
        return parse_qs(urlparse(url).query).get('v', [None])[0]

def get_transcript(video_id):
    """Get the transcript for the video"""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return ' '.join([entry['text'] for entry in transcript])
    except Exception as e:
        return f"Error: {str(e)}"

def print_transcript(transcript):
    """Print the transcript with word wrapping"""
    print("\nTranscript:")
    print("-----------")
    print(textwrap.fill(transcript, width=80))
    print("\n")

def get_video_title(video_id):
    """Get the title of the YouTube video"""
    url = f"https://www.youtube.com/watch?v={video_id}"
    response = requests.get(url)
    if response.status_code == 200:
        title = response.text.split('<title>')[1].split('</title>')[0]
        return title.replace(' - YouTube', '').strip()
    return "Untitled Video"

def write_markdown(video_id, transcript):
    """Write the transcript to a Markdown file"""
    title = get_video_title(video_id)
    filename = f"{title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    folder_name = "config/Lex-Huberman/"
    
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    file_path = os.path.join(folder_name, filename)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(f"# {title}\n\n")
        f.write(f"Video ID: {video_id}\n\n")
        f.write("## Transcript\n\n")
        f.write(textwrap.fill(transcript, width=80))
        f.write(f"\n\n[Watch Video](https://www.youtube.com/watch?v={video_id})")
    
    return file_path

def process_multiple_videos(urls, save_to_file=False):
    """Process multiple YouTube videos"""
    results = []
    for url in urls:
        video_id = get_video_id(url)
        if video_id:
            transcript = get_transcript(video_id)
            if save_to_file:
                file_path = write_markdown(video_id, transcript)
                results.append((url, file_path))
            else:
                results.append((url, transcript))
        else:
            results.append((url, "Invalid YouTube URL"))
    return results

def youtube_transcript_assistant():
    while True:
        clear_screen()
        print("╔══════════════════════════════════════════════╗")
        print("║        YouTube Transcript AI Assistant       ║")
        print("╠══════════════════════════════════════════════╣")
        print("║ 1. Print transcripts                         ║")
        print("║ 2. Save transcripts to Markdown files        ║")
        print("║ 3. Return to main menu                       ║")
        print("╚══════════════════════════════════════════════╝")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice in ['1', '2']:
            print("\nEnter YouTube URLs (one per line). Press Enter twice when done:")
            urls = []
            while True:
                url = input().strip()
                if url:
                    urls.append(url)
                else:
                    break
            
            if urls:
                results = process_multiple_videos(urls, save_to_file=(choice == '2'))
                for url, result in results:
                    if choice == '1':
                        print(f"\nTranscript for {url}:")
                        print_transcript(result)
                    else:
                        print(f"\nTranscript for {url} saved to: {result}")
            else:
                print("No URLs entered.")
            input("Press Enter to continue...")
        elif choice == '3':
            print("Returning to main menu...")
            break
        else:
            print("Invalid choice. Please try again.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    youtube_transcript_assistant()
else:
    # This allows the script to be imported and run from the main menu script
    youtube_transcript_assistant()