#!/bin/bash
# Build script para Vercel (desde frontend/)
echo "🚀 Building EduForge frontend for Vercel..."

# Instalar dependencias
echo "📦 Installing dependencies..."
npm install

# Build del proyecto React
echo "🔨 Building React app..."
npm run build

echo "✅ Build completed successfully!"
