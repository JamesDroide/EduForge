#!/bin/bash
# Script para iniciar el frontend de EduForge

echo "🚀 Iniciando EduForge Frontend..."
echo ""

# Verificar si existen node_modules
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Instalando dependencias de npm..."
    cd frontend
    npm install
    cd ..
    echo ""
fi

echo "🔧 Iniciando servidor de desarrollo en http://localhost:5173"
cd frontend
npm run dev
