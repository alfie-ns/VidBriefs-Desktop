#!/bin/bash

# Find the next available number
base_name="vidbriefs-desktop"
I=1
while [ -d "${base_name}-${I}" ]; do
  I=$((I + 1))
done
new_name="${base_name}-${I}"

# Clone the repository into the new directory, init into new_name variable
git clone "https://github.com/alfie-ns/vidbriefs-desktop" #$new_name"

# Change directory to the cloned repository
#cd "$new_name"
cd vidbriefs-desktop

# Copy the .env from parent directory into current directory
cp ../.env .

echo "Repository cloned as $new_name and .env file copied."