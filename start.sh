#!/bin/bash

# Install Chromium
apt-get update && apt-get install -y chromium

# Export path for undetected_chromedriver
export CHROME_BINARY="/usr/bin/chromium"

# Run your bot
python3 main.py
