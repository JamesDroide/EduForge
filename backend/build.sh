#!/usr/bin/env bash

echo "Preparando EduForge para despliegue..."

echo "Instalando dependencias del backend..."
pip install -r requirements.txt

echo "Verificando modelos de ML..."
if [ ! -f "scripts/models/trained/dropout_model.pkl" ]; then
    echo "Modelo no encontrado, entrenando..."
    cd scripts && python train_and_evaluate_model.py && cd ..
fi

echo "Creando directorios necesarios..."
mkdir -p uploads
mkdir -p src/models/trained

echo "Preparacion completada."
