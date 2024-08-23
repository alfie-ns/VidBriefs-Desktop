#!/bin/bash

#Vidbriefs/vidbriefs-desktop/cp-desktop.sh

# Temporary file to store combined output
temp_file=$(mktemp)

# Find all Python files in ai-scripts/ and copy their contents
find ai-scripts/ -name "*.py" -type f -exec echo "File: {}" \; -exec cat {} \; -exec echo \; >> "$temp_file"

# Add a separator between the two sections
echo -e "\n--- run-desktop.sh ---\n" >> "$temp_file"

# Find run-desktop.sh and copy its contents
find run-desktop.sh -type f -exec echo "File: {}" \; -exec cat {} \; -exec echo \; >> "$temp_file"

# Copy the combined contents to clipboard
cat "$temp_file" | pbcopy

# Clean up
rm "$temp_file"

echo "Contents of Python files in ai-scripts/ and run-desktop.sh have been copied to clipboard."