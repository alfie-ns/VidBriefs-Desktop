#!/bin/bash

# Function to print bold text ------------------------------
print_bold() {
    BOLD=$(tput bold)
    NORMAL=$(tput sgr0)
    echo -e "${BOLD}$1${NORMAL}"
}

# Function to get commit importance
get_commit_importance() {
    local importance_text
    while true; do # Indefinite loop until a valid input is received
        echo -n "Enter the importance (1-5): " >&2
        read -rsn1 importance
        echo >&2  # Print a newline after reading the input

        case $importance in
            1) importance_text="Trivial"; break;;
            2) importance_text="Minor"; break;;
            3) importance_text="Moderate"; break;;
            4) importance_text="Significant"; break;;
            5) importance_text="Milestone"; break;;
            *) echo "Invalid input. Please try again." >&2;;
        esac # end case statement
    done # end while loops
    echo "$importance_text"
}

# Main script -----------------------------------------------
git add .

print_bold "\nCommit importance:" >&2
echo "1. Trivial" >&2
echo "2. Minor" >&2
echo "3. Moderate" >&2
echo "4. Significant" >&2
echo -e "5. Milestone\n" >&2

# Capture the commit importance
importance=$(get_commit_importance)

# Use the importance directly as the commit message
git commit -m "$importance"
git push origin main

echo -e '\nLocal repo pushed to remote origin\n' >&2
print_bold "Commit message: $importance" >&2