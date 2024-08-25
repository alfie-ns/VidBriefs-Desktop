#!/bin/bash

# Function to print bold text ------------------------------
print_bold() {
    BOLD=$(tput bold)
    NORMAL=$(tput sgr0)
    echo -e "${BOLD}$1${NORMAL}"
}

# Function to get commit importance
get_commit_importance() {
    while true; do
        echo -n "Enter the importance (1-5): "
        read -rsn1 importance
        echo  # Print a newline after reading the input

        case $importance in
            1) echo "Trivial"; return;;
            2) echo "Minor"; return;;
            3) echo "Moderate"; return;;
            4) echo "Significant"; return;;
            5) echo "Milestone"; return;;
            *) echo "Invalid input. Please try again.";;
        esac
    done
}

# Main script -----------------------------------------------
git add .

print_bold "\nCommit importance:"
echo "1. Trivial"
echo "2. Minor"
echo "3. Moderate"
echo "4. Significant"
echo -e "5. Milestone\n"

# Capture the commit importance
importance=$(get_commit_importance)

# Use the importance directly as the commit message
git commit -m "$importance"
git push origin main

echo -e '\nLocal repo pushed to remote origin\n'
print_bold "Commit message: $importance"