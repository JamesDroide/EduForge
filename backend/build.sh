#!/usr/bin/env bash

echo "Preparando EduForge para despliegue..."

echo "Instalando dependencias del backend..."
pip install -r requirements.txt

echo "Verificando modelos de ML..."
if [ ! -f "scripts/models/trained/trained_model.pkl" ]; then
    echo "Modelo no encontrado, entrenando..."
    (cd scripts/models && python model_trainer.py)
fi

echo "Creando directorios necesarios..."
mkdir -p uploads
mkdir -p scripts/models/trained

echo "Preparacion completada."
