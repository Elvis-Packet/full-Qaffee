#!/bin/bash
set -e

# Print Node and npm versions
echo "Node version: $(node -v)"
echo "NPM version: $(npm -v)"

# Clean install dependencies
echo "Installing dependencies..."
npm install

# Build the application
echo "Building the application..."
npm run build

# Verify build
if [ -d "dist" ]; then
    echo "Build successful!"
    exit 0
else
    echo "Build failed - dist directory not found"
    exit 1
fi 