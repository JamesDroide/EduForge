#!/bin/bash
echo "Building EduForge frontend for Vercel..."

echo "Installing dependencies..."
npm install

echo "Building React app..."
npm run build

echo "Build completed successfully."
