#!/bin/bash

clear

# Function to display the menu
display_menu() {
    echo "========================================="
    echo "       VidBriefs-Desktop Launcher        "
    echo "========================================="
    echo "1. YouTube Transcript AI Assistant"
    echo "2. Enhanced AI Chatbot Assistant"
    echo "3. TED Talk Analysis Assistant"
    echo "4. Exit"
    echo "========================================="
    echo "Enter your choice (1-4): "
}

# Main loop -------------------------------------
while true; do
    display_menu
    read choice # read user input

    case $choice in # if-else ladder
        1) # ';;' marks the end of the case
            echo -e "\nLaunching YouTube Transcript AI Assistant...\n"
            python3 AI-Scripts/youtube.py
            ;;
        2)
            echo -e "\nLaunching Enhanced AI Chatbot Assistant...\n"
            python3 AI-Scripts/chatbot.py
            ;;
        3)
            echo -e "\nLaunching TED Talk Analysis Assistant...\n"
            python3 AI-Scripts/tedbriefs.py
            ;;
        4)
            echo -e "\nExiting...\n"
            exit 0
            ;;
        *)
            echo "Invalid choice. Please try again."
            ;;
    esac # end case

    # Pause before clearing the screen and showing the menu again
    echo
    echo "Press Enter to continue..."
    read # waits for input
    clear
done