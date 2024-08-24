#!/bin/bash

# Function to print bold text
print_bold() {
  BOLD=$(tput bold)
  NORMAL=$(tput sgr0)
  echo -e "${BOLD}$1${NORMAL}"
}

# Function to get commit importance
get_commit_importance() {
    read -p "Enter the number (1-3): " importance
    # read input as importance variable used in case statement
    case $importance in
        1) echo "Minor: Small changes, fixes, or updates";;
        2) echo "Significant: New features, major improvements, or important fixes";;
        3) echo "Working: Most recent fully-working version";;
        *) echo "Invalid choice. Using 'Minor' as default."; echo "Minor: Small changes, fixes, or updates";;
    esac
}

# Main script --------------------------------------------
cd .. # backtrack to main directory
git add .

print_bold "\nCommit importance:"
echo "1. Minor: Small changes, fixes, or updates"
echo "2. Significant: New features, major improvements, or important fixes"
echo -e "3. Working: Newest fully-working version\n"

commit_message=$(get_commit_importance) # call function
git commit -m "$commit_message"

git push origin main
echo -e '\nLocal repo pushed to remote origin\n'
print_bold "Commit message: $commit_message"