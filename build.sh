#!/usr/bin/env bash
# Build script for Render

# Install Python dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p src/uploads
mkdir -p scripts/models/trained

echo "Build completed successfully!"
