#!/bin/bash

# Build script for Render deployment
# This ensures all dependencies are installed correctly

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Backend build completed successfully!"
