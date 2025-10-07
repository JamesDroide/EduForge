#!/bin/bash
# Script para iniciar el backend de EduForge

echo "🚀 Iniciando EduForge Backend..."
echo ""

# Verificar si existe el modelo
if [ ! -f "backend/models/dropout_model.pkl" ]; then
    echo "⚠️  Modelo no encontrado. Entrenando modelo..."
    cd backend
    python train_model.py
    cd ..
    echo ""
fi

echo "🔧 Iniciando servidor FastAPI en http://localhost:8000"
cd backend/app
python main.py
