"""
Script para entrenar el modelo de deserción con datos reales del sistema
Ajustado específicamente para trabajar con la estructura:
- estudiante_id, nombre, fecha, nota_final, asistencia, inasistencia, conducta
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

def create_synthetic_data():
    """Crea datos sintéticos basados en la estructura real del sistema"""
    np.random.seed(42)
    n_samples = 1000

    # Generar datos con la estructura exacta del CSV real
    data = {
        'estudiante_id': range(1, n_samples + 1),
        'nombre': [f'Estudiante_{i}' for i in range(1, n_samples + 1)],
        'fecha': ['2025-01-01'] * n_samples,  # Fecha fija por simplicidad
        'nota_final': np.random.normal(14, 3, n_samples).clip(0, 20),
        'asistencia': np.random.normal(80, 15, n_samples).clip(0, 100),
        'inasistencia': np.random.normal(20, 15, n_samples).clip(0, 100),
        'conducta': np.random.choice(['positivo', 'neutral', 'agresivo'], n_samples, p=[0.4, 0.4, 0.2])
    }

    df = pd.DataFrame(data)

    # Ajustar asistencia e inasistencia para que sumen aproximadamente 100
    df['inasistencia'] = 100 - df['asistencia'] + np.random.normal(0, 5, n_samples)
    df['inasistencia'] = df['inasistencia'].clip(0, 100)

    return df

def create_target_variable(df):
    """Crea la variable objetivo de deserción basada en reglas lógicas"""
    # Reglas para determinar deserción (más realistas)
    desercion = np.zeros(len(df))

    # Factores de riesgo
    nota_baja = df['nota_final'] < 11
    alta_inasistencia = df['inasistencia'] > 30
    conducta_problematica = df['conducta'] == 'agresivo'

    # Probabilidades de deserción según combinación de factores
    for i in range(len(df)):
        prob_desercion = 0.1  # probabilidad base

        if nota_baja.iloc[i]:
            prob_desercion += 0.3
        if alta_inasistencia.iloc[i]:
            prob_desercion += 0.25
        if conducta_problematica.iloc[i]:
            prob_desercion += 0.2

        # Agregar algo de aleatoriedad
        desercion[i] = np.random.random() < prob_desercion

    return desercion.astype(int)

def prepare_features(df):
    """Prepara las características para el modelo"""
    df_features = df.copy()

    # 1. Normalizar nota_final a escala 0-1
    df_features['nota_normalizada'] = df_features['nota_final'] / 20.0

    # 2. Codificar conducta
    conducta_map = {'positivo': 0, 'neutral': 1, 'agresivo': 2}
    df_features['conducta_encoded'] = df_features['conducta'].map(conducta_map)

    # 3. Normalizar asistencia e inasistencia
    df_features['asistencia_normalizada'] = df_features['asistencia'] / 100.0
    df_features['inasistencia_normalizada'] = df_features['inasistencia'] / 100.0

    # 4. Crear indicadores de riesgo
    df_features['nota_baja'] = (df_features['nota_final'] < 11).astype(int)
    df_features['alta_inasistencia'] = (df_features['inasistencia'] > 30).astype(int)
    df_features['conducta_problematica'] = (df_features['conducta'] == 'agresivo').astype(int)

    # 5. Seleccionar características para el modelo
    feature_columns = [
        'nota_normalizada',
        'conducta_encoded',
        'asistencia_normalizada',
        'inasistencia_normalizada',
        'nota_baja',
        'alta_inasistencia',
        'conducta_problematica'
    ]

    return df_features[feature_columns], feature_columns

def main():
    print("🚀 Iniciando entrenamiento del modelo para datos reales...")

    # 1. Crear o cargar datos
    print("📊 Generando datos sintéticos basados en estructura real...")
    df = create_synthetic_data()

    # 2. Crear variable objetivo
    print("🎯 Creando variable objetivo...")
    y = create_target_variable(df)

    print(f"📈 Distribución de deserción: {np.bincount(y)}")
    print(f"   - No deserción: {np.sum(y == 0)} ({np.mean(y == 0)*100:.1f}%)")
    print(f"   - Deserción: {np.sum(y == 1)} ({np.mean(y == 1)*100:.1f}%)")

    # 3. Preparar características
    print("⚙️  Preparando características...")
    X, feature_columns = prepare_features(df)

    print(f"✅ Características preparadas: {feature_columns}")
    print(f"📐 Forma de X: {X.shape}")

    # 4. División de datos
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 5. Escalado de características
    print("📏 Aplicando escalado...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 6. Entrenamiento del modelo
    print("🧠 Entrenando modelo...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        class_weight='balanced'
    )

    model.fit(X_train_scaled, y_train)

    # 7. Evaluación
    print("📊 Evaluando modelo...")
    y_pred = model.predict(X_test_scaled)
    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)
    print(f"✅ Precisión: {accuracy:.3f}")

    print("\n📈 Reporte de clasificación:")
    print(classification_report(y_test, y_pred))

    # 8. Guardar modelo y configuración
    print("💾 Guardando modelo...")

    # Crear directorio si no existe
    model_dir = "trained"
    os.makedirs(model_dir, exist_ok=True)

    # Guardar modelo
    joblib.dump(model, os.path.join(model_dir, "trained_model.pkl"))
    print(f"✅ Modelo guardado en: {os.path.join(model_dir, 'trained_model.pkl')}")

    # Guardar scaler
    joblib.dump(scaler, os.path.join(model_dir, "scaler.pkl"))
    print(f"✅ Scaler guardado en: {os.path.join(model_dir, 'scaler.pkl')}")

    # Guardar configuración
    config = {
        'feature_columns': feature_columns,
        'expected_columns': ['estudiante_id', 'nombre', 'fecha', 'nota_final', 'asistencia', 'inasistencia', 'conducta'],
        'conducta_map': {'positivo': 0, 'neutral': 1, 'agresivo': 2},
        'model_version': '2.0',
        'training_date': '2025-01-05'
    }

    joblib.dump(config, os.path.join(model_dir, "model_config.pkl"))
    print(f"✅ Configuración guardada en: {os.path.join(model_dir, 'model_config.pkl')}")

    # 9. Importancia de características
    print("\n🔍 Importancia de características:")
    feature_importance = pd.DataFrame({
        'feature': feature_columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    for _, row in feature_importance.iterrows():
        print(f"   {row['feature']}: {row['importance']:.3f}")

    print(f"\n🎉 Modelo entrenado exitosamente!")
    print(f"📁 Archivos guardados en: {os.path.abspath(model_dir)}")

    return model, scaler, config

if __name__ == "__main__":
    main()
