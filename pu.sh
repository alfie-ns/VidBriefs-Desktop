#!/bin/bash

# Function to handle Ctrl+C
ctrl_c() {
    echo
    echo "Ctrl+C detected. Exiting script..."
    exit 0
}

# Set up the trap for Ctrl+C
trap ctrl_c INT

# Git operations
git add .
git commit -m "update"
git push origin main

# Wait for 5 seconds
echo "Waiting for 5 seconds before clearing. Press Ctrl+C to exit..."
sleep 5

# Clear the screen
clear