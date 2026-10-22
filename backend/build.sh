#!/usr/bin/env bash
# Build script para preparar el proyecto para despliegue

echo "🚀 Preparando EduForge para despliegue..."

# Instalar dependencias del backend
echo "📦 Instalando dependencias del backend..."
pip install -r requirements.txt

# Verificar que los modelos entrenados existan
echo "🤖 Verificando modelos de ML..."
if [ ! -f "scripts/models/trained/dropout_model.pkl" ]; then
    echo "⚠️  Modelo no encontrado, entrenando..."
    cd scripts && python train_and_evaluate_model.py && cd ..
fi

# Crear directorios necesarios
echo "📁 Creando directorios necesarios..."
mkdir -p uploads
mkdir -p src/models/trained

echo "✅ Preparación completada!"
