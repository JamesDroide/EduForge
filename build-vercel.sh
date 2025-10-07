#!/bin/bash
# Build script para Vercel
echo "🚀 Building EduForge frontend for Vercel..."

# Navegar al directorio del frontend
cd frontend

# Instalar dependencias
echo "📦 Installing dependencies..."
npm install

# Build del proyecto React
echo "🔨 Building React app..."
npm run build

echo "✅ Build completed successfully!"
