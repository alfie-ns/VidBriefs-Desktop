#!/bin/bash

# Function to get commit importance
get_commit_importance() {
    echo "How important is this commit?"
    echo "1. Minor: Small changes, fixes, or updates"
    echo "2. Significant: New features, major improvements, or important fixes"
    echo "3. Working: Newest fully-working version"
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
cd ..
git add .

commit_message=$(get_commit_importance)
git commit -m "$commit_message"

git push origin main
echo -e '\nLocal repo pushed to remote origin\n'
echo "Commit message: $commit_message"