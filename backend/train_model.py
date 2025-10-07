"""
Script para entrenar el modelo de predicción de deserción estudiantil
Genera datos sintéticos para demostración y entrena un modelo Random Forest
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import os

def generate_synthetic_data(n_samples=1000):
    """Genera datos sintéticos de estudiantes para entrenamiento"""
    np.random.seed(42)
    
    # Generar características
    attendance_rate = np.random.uniform(50, 100, n_samples)
    average_grade = np.random.uniform(3, 10, n_samples)
    study_hours = np.random.uniform(0, 30, n_samples)
    family_income = np.random.uniform(500, 5000, n_samples)
    parent_education = np.random.randint(1, 6, n_samples)
    extracurricular = np.random.randint(0, 6, n_samples)
    failed_subjects = np.random.randint(0, 8, n_samples)
    age = np.random.randint(15, 26, n_samples)
    
    # Crear DataFrame
    data = pd.DataFrame({
        'attendance_rate': attendance_rate,
        'average_grade': average_grade,
        'study_hours_per_week': study_hours,
        'family_income': family_income,
        'parent_education_level': parent_education,
        'extracurricular_activities': extracurricular,
        'failed_subjects': failed_subjects,
        'age': age
    })
    
    # Generar etiquetas con lógica realista
    # Mayor probabilidad de deserción con:
    # - Baja asistencia, bajo promedio, pocas horas de estudio, materias reprobadas
    dropout_probability = (
        (100 - attendance_rate) / 100 * 0.25 +
        (10 - average_grade) / 10 * 0.25 +
        (30 - study_hours) / 30 * 0.15 +
        (failed_subjects / 8) * 0.20 +
        (6 - parent_education) / 5 * 0.10 +
        (1 - extracurricular / 5) * 0.05
    )
    
    # Añadir algo de aleatoriedad
    dropout_probability += np.random.normal(0, 0.1, n_samples)
    dropout_probability = np.clip(dropout_probability, 0, 1)
    
    # Crear etiquetas binarias
    data['dropout'] = (dropout_probability > 0.5).astype(int)
    
    return data

def train_model():
    """Entrena el modelo de predicción de deserción"""
    print("Generando datos sintéticos...")
    data = generate_synthetic_data(1000)
    
    # Separar características y etiquetas
    X = data.drop('dropout', axis=1)
    y = data['dropout']
    
    print(f"Total de muestras: {len(data)}")
    print(f"Deserción: {y.sum()} ({y.sum()/len(y)*100:.2f}%)")
    print(f"No deserción: {(1-y).sum()} ({(1-y).sum()/len(y)*100:.2f}%)")
    
    # Dividir en entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print("\nEntrenando modelo Random Forest...")
    # Entrenar modelo
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        class_weight='balanced'
    )
    
    model.fit(X_train, y_train)
    
    # Evaluar modelo
    print("\nEvaluando modelo...")
    y_pred = model.predict(X_test)
    
    print(f"\nAccuracy: {accuracy_score(y_test, y_pred):.4f}")
    print("\nReporte de clasificación:")
    print(classification_report(y_test, y_pred, target_names=['No deserción', 'Deserción']))
    
    print("\nMatriz de confusión:")
    print(confusion_matrix(y_test, y_pred))
    
    # Importancia de características
    print("\nImportancia de características:")
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    print(feature_importance)
    
    # Guardar modelo
    model_dir = os.path.join(os.path.dirname(__file__), 'models')
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, 'dropout_model.pkl')
    
    joblib.dump(model, model_path)
    print(f"\nModelo guardado en: {model_path}")
    
    return model

if __name__ == "__main__":
    train_model()
