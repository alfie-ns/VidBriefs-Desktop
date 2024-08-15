#!/bin/bash
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Not inside a virtual environment. Exiting with failure." && exit 1
fi
pip install -r requirements.txt
# -r requirements text file
pip install --upgrade pip
printf '\n%s\n' "$(tput bold)Requirements installed successfully$(tput sgr0)"

