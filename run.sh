#!/bin/bash

echo "Setting up Report Generator App..."

# Install system packages first
apt update && apt install -y python3-venv python3-full

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p uploads templates

echo "Starting the application..."
echo "Access the app at: http://localhost:5000"

# Run the application
python app.py
