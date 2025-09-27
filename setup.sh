#!/bin/bash

# Kinky.nl Scraper Setup Script

echo "Setting up Kinky.nl Web Scraper..."

# Create necessary directories
echo "Creating directories..."
mkdir -p /workspace/imgs
mkdir -p /workspace/vids
mkdir -p /workspace/data
mkdir -p /workspace/logs

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Make scripts executable
echo "Making scripts executable..."
chmod +x kinky_scraper.py
chmod +x run_scraper.py

echo "Setup completed!"
echo ""
echo "To run the scraper:"
echo "  python run_scraper.py --mode once      # Run once"
echo "  python run_scraper.py --mode scheduled # Run every hour"
echo ""
echo "Or run directly:"
echo "  python kinky_scraper.py"