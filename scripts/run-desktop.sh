#!/bin/bash

# Function to handle the exit command
exit_script() {
    clear
    echo "Exiting..."
    sleep 0.5 # wait for half a second
    clear
    exit 0 # exit successfully
}

# Trap the SIGINT signal (Ctrl+C) and call the exit_script function
trap exit_script SIGINT

clear

# Check if the user is in a virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    printf '\n%s\n' "$(tput bold)ERROR: Not in a virtual environment$(tput sgr0)"
    echo ""
    echo "Please follow these steps to set up and activate a virtual environment:"
    echo ""
    echo "1. Create a virtual environment:"
    echo "   python3 -m venv venv"
    echo ""
    echo "2. Activate the virtual environment:"
    echo "   source venv/bin/activate"
    echo ""
    echo "3. Install required packages:"
    echo "   cd setup"
    echo "   ./install-requirements.sh"
    echo ""
    echo "After completing these steps, please run this script again."
    exit 1
fi

# Function to display the menu
display_menu() {
    echo "╔══════════════════════════════════════════════╗"
    echo "║              VidBriefs-Desktop               ║"
    echo "╠══════════════════════════════════════════════╣"
    echo "║ 1. 🌟 Enhanced AI Assistant (Nexus)          ║"
    echo "╠══════════════════════════════════════════════╣"
    echo "║ 2. YouTube Transcript AI Assistant           ║"
    echo "║ 3. TED Talk Analysis Assistant               ║"
    echo "║ 4. Sight Repo Assistant                      ║"
    echo "║ 5. Huberman.py                               ║"
    echo "╠══════════════════════════════════════════════╣"
    echo "║ 6. YouTube Transcript Printer                ║"
    echo "║ 7. Categorise your insights                  ║"
    echo "╚══════════════════════════════════════════════╝"
    echo "Enter your choice (1-6) or press Ctrl+C to exit:"
}
# Main loop -------------------------------------
while true; do
    display_menu
    read -rsn1 input # read a single character immediately without waiting for Enter

    if [[ $input == $'\x1B' ]]; then # detect escape sequence
        read -rsn2 input # read the next two characters
        if [[ $input == "[C" ]]; then # detect Shift+C (right arrow key)
            exit_script
        fi

    elif [[ $input =~ ^[1-7]$ ]]; then
        echo $input # echo the input so the user can see what they've chosen
        case $input in
            1)  
                echo -e "\nLaunching Nexus (Enhanced AI Chatbot Assistant)...\n"
                python3 AI-Scripts/nexus.py
                ;;
            2)
                echo -e "\nLaunching YouTube Transcripts AI Assistant...\n"
                python3 AI-Scripts/youtube.py
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
                echo -e "\nLaunching Huberman.py...\n"
                python3 AI-Scripts/huberman.py
                ;;
            6)
                echo -e "\nLaunching YouTube Transcript Printer...\n"
                python3 config/Lex-Huberman/Youtube-Transcript-Printer.py
                ;;

            7) 
                echo -e "\nCategorising the .md files...\n"
                python3 catergorise.py
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