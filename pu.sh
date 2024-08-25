#!/bin/bash

# Function to print bold text -----------------------------
print_bold() {
  BOLD=$(tput bold)
  NORMAL=$(tput sgr0)
  echo -e "${BOLD}$1${NORMAL}"
}

# Function to get commit importance
get_commit_importance() { # read user input into importance variable
    read -p "Enter the number (1-5): " importance
    case $importance in # importance cases
        1) echo "Trivial: Typos, formatting, or very minor changes";;
        2) echo "Minor: Small changes, fixes, or updates";;
        3) echo "Moderate: Notable improvements or additions";;
        4) echo "Significant: Major features or important fixes";;
        5) echo "Critical: Crucial updates or milestone achievements";;
        *) echo "Invalid choice. Using 'Minor' as default."; echo "Minor: Small changes, fixes, or updates";;
    esac # end case
}

# Main script -----------------------------------------------
git add .

print_bold "\nCommit importance:"
echo "1. Trivial: Typos, formatting, or very minor changes"
echo "2. Minor: Small changes, fixes, or updates"
echo "3. Moderate: Notable improvements or additions"
echo "4. Significant: Major features or important fixes"
echo -e "5. Critical: Crucial updates or milestone achievements\n"

commit_message=$(get_commit_importance) # call function
git commit -m "$commit_message"

git push origin main
echo -e '\nLocal repo pushed to remote origin\n'
print_bold "Commit message: $commit_message"