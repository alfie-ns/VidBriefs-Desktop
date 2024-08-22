#!/bin/bash
if [[ -z "$VIRTUAL_ENV" ]]; then # if virtual environment is not set/empty
    echo "Not inside a virtual environment. Exiting with failure." && exit 1
else
    pip install -r requirements.txt # -r requirements text file
    pip install --upgrade pip
    printf '\n%s\n' "$(tput bold)Requirements installed successfully$(tput sgr0)"
fi


