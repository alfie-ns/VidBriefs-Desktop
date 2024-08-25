#!/bin/bash

# Function to print bold text ------------------------------
print_bold() {
  BOLD=$(tput bold)
  NORMAL=$(tput sgr0)
  echo -e "${BOLD}$1${NORMAL}"
}

# Function to get commit importance
get_commit_importance() {
    echo -n "Enter the importance (1-5): "  # Prompt for input, -n: no newline
    read -rsn1 importance  # Read a single character into 'importance' 
    case $importance in # importance cases
        1) print_bold "Trivial";;
        2) print_bold "Minor";;
        3) print_bold "Moderate";;
        4) print_bold "Significant";;
        5) print_bold "Milestone";;
        *) print_bold "Invalid choice. Using 'Minor' as default."; echo "Minor: Small changes, fixes, or updates";;
    esac # end case
}

# Main script -----------------------------------------------
git add .

print_bold "\nCommit importance:"
echo "1. Trivial"
echo "2. Minor"
echo "3. Moderate"
echo "4. Significant"
echo -e "5. Milestone\n"

commit_message=$(get_commit_importance) # run 'get_commit_importance' function; store output in 'commit_message'
git commit -m "$commit_message"

git push origin main
echo -e '\nLocal repo pushed to remote origin\n'
print_bold "Commit message: $commit_message"

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