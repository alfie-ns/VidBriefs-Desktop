#!/bin/bash

# OPENAI_API_KEY=(api-key)
touch .env
echo "# https://platform.openai.com/api-keys" >> .env
echo "" >> .env
echo "OPENAI_API_KEY=" >> .env

# Remember to get openai credits