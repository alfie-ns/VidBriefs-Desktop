#!/bin/bash

# Function to handle the exit command
exit_script() {
    clear
    echo "Exiting..."
    sleep 2
    clear
    exit 0
}

# Trap the SIGINT signal (Ctrl+C) and call the exit_script function
trap exit_script SIGINT

clear

# if user not in a venv, exit with failure; 'z' checks if the string is empty
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Not inside a virtual environment. Exiting with failure."
    echo ""
    echo "To set up a virtual environment, do 'python -m venv venv'"
    echo "Then, to activate the venv, do 'source venv/bin/activate'"
    echo "Finally, run 'cd setup; ./install-requirements.sh' to install the necessary packages into the venv."
    exit 1
fi

# Function to display the menu
display_menu() {
    echo "========================================="
    echo "                VidBriefs-Desktop        "
    echo "========================================="
    echo "1. YouTube Transcript AI Assistant"
    echo "2. Enhanced AI Chatbot Assistant"
    echo "3. TED Talk Analysis Assistant"
    echo "4. Sight Repo Assistant"
    echo "5. News Assistant"
    echo "6. Exit"
    echo "========================================="
    echo "Enter your choice (1-6) or press Shift+C to exit: "
}

# Main loop -------------------------------------
while true; do
    display_menu
    read -rsn1 input # read a single character without echoing to the terminal

    if [[ $input == $'\x1B' ]]; then # detect escape sequence
        read -rsn2 input # read the next two characters
        if [[ $input == "[C" ]]; then # detect Shift+C (right arrow key)
            exit_script
        fi
    elif [[ $input =~ ^[1-6]$ ]]; then
        echo $input # echo the input so the user can see what they chose
        case $input in
            1)
                echo -e "\nLaunching YouTube Transcript AI Assistant...\n"
                python3 AI-Scripts/youtube.py
                ;;
            2)
                echo -e "\nLaunching Enhanced AI Chatbot Assistant...\n"
                python3 AI-Scripts/chatbot.py
                ;;
            3)
                echo -e "\nLaunching TED Talk Analysis Assistant...\n"
                python3 AI-Scripts/tedtalk.py
                ;;
            4)
                echo -e "Launching Sight Repo Assistant...\n"
                python3 AI-Scripts/sight.py
                ;;
            5)
                echo -e "\nLaunching AI-Scripts/news.py...\n"
                python3 AI-Scripts/news.py
                ;;
            6)
                exit_script
                ;;
        esac

        # Pause before clearing the screen and showing the menu again
        echo
        echo "Press Enter to continue..."
        read # waits for input
        clear
    else
        echo "Invalid choice. Please try again."
    fi
done