#!/bin/bash

# Find all Python files in ai-scripts/ and copy them to the current directory
#find ai-scripts/ -name "*.py" -type f -print0 | xargs -0 -I {} cp {} .
#find ai-scripts/ -name "*.py" -type f -exec echo "File: {}" \; -exec cat {} \; -exec echo \;

find ai-scripts/ -name "*.py" -type f -exec echo "File: {}" \; -exec cat {} \; -exec echo \; | pbcopy

# Optional: If you want to see what files are being copied, add the -v flag to cp
# find ai-scripts/ -name "*.py" -type f -print0 | xargs -0 -I {} cp -v {} .