#!/bin/bash

# Function to print bold text ------------------------------
print_bold() {
  BOLD=$(tput bold)
  NORMAL=$(tput sgr0)
  echo -e "${BOLD}$1${NORMAL}"
}

# Function to get commit importance
get_commit_importance() { # read user input into importance variable, -p frag to specify that string as a prompt
    read -rsn1 "Enter the importance (1-5): " importance 
    case $importance in # importance cases
        1) echo "Trivial";;
        2) echo "Minor";;
        3) echo "Moderate";;
        4) echo "Significant";;
        5) echo "Milestone";;
        *) echo "Invalid choice. Using 'Minor' as default."; echo "Minor: Small changes, fixes, or updates";;
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