#!/bin/bash

# Function to print bold text ------------------------------
print_bold() {
  BOLD=$(tput bold)
  NORMAL=$(tput sgr0)
  echo -e "${BOLD}$1${NORMAL}"
}

# Function to get commit importance
get_commit_importance() {
    echo -n "Enter the importance (1-5): "  # Prompt for input
    read -rsn1 importance  # Read a single character into 'importance'
    case $importance in
        1) echo "Trivial";;
        2) echo "Minor";;
        3) echo "Moderate";;
        4) echo "Significant";;
        5) echo "Milestone";;
        *) echo "Minor";;  # Default to "Minor" if input is invalid
    esac
}

# Main script -----------------------------------------------
git add .

print_bold "\nCommit importance:"
echo "1. Trivial"
echo "2. Minor"
echo "3. Moderate"
echo "4. Significant"
echo -e "5. Milestone\n"

# Capture the commit importance separately from the prompt
importance=$(get_commit_importance)

# Use the importance directly as the commit message
git commit -m "$importance"

git push origin main
echo -e '\nLocal repo pushed to remote origin\n'
print_bold "Commit message: $importance"

: <<'-rsnl?'

The function reads first character typed immediately; and stores 
it in 'importance' variable.
---------------------------------------------------------
-rsnl means:
-r: Raw input (disables interpretation of backslash escapes)
-s: Silent mode (don't echo characters back to the terminal)
-n: Take in one character before returning/accepting input
This allows for immediate, single-character input without pressing Enter.

-rsnl?