#!/bin/bash
set -e

# Print Node and npm versions
echo "Node version: $(node -v)"
echo "NPM version: $(npm -v)"

# Clean the cache and remove existing modules
echo "Cleaning npm cache and removing existing modules..."
npm cache clean --force
rm -rf node_modules package-lock.json

# Install dependencies and generate package-lock.json
echo "Installing dependencies..."
npm install

# Build the application
echo "Building the application..."
NODE_ENV=production npm run build

# Verify build
if [ -d "dist" ]; then
    echo "Build successful!"
    exit 0
else
    echo "Build failed - dist directory not found"
    exit 1
fi 