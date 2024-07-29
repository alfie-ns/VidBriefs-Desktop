#!/bin/bash
pip install -r requirements.txt
# -r requirements text file
pip install --upgrade pip
printf '\n%s\n' "$(tput bold)Requirements installed successfully$(tput sgr0)"
