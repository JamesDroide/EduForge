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
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

def create_synthetic_data():
    """Crea datos sintéticos basados en la estructura real del sistema"""
    np.random.seed(42)
    n_samples = 1000

    data = {
        'estudiante_id': range(1, n_samples + 1),
        'nombre': [f'Estudiante_{i}' for i in range(1, n_samples + 1)],
        'fecha': ['2025-01-01'] * n_samples,
        'nota_final': np.random.normal(14, 3, n_samples).clip(0, 20),
        'asistencia': np.random.normal(80, 15, n_samples).clip(0, 100),
        'inasistencia': np.random.normal(20, 15, n_samples).clip(0, 100),
        'conducta': np.random.choice(['positivo', 'neutral', 'agresivo'], n_samples, p=[0.4, 0.4, 0.2])
    }

    df = pd.DataFrame(data)
    df['inasistencia'] = 100 - df['asistencia'] + np.random.normal(0, 5, n_samples)
    df['inasistencia'] = df['inasistencia'].clip(0, 100)

    return df

def create_target_variable(df):
    """Crea la variable objetivo de deserción basada en reglas lógicas"""
    desercion = np.zeros(len(df))

    nota_baja = df['nota_final'] < 11
    alta_inasistencia = df['inasistencia'] > 30
    conducta_problematica = df['conducta'] == 'agresivo'

    for i in range(len(df)):
        prob_desercion = 0.1

        if nota_baja.iloc[i]:
            prob_desercion += 0.3
        if alta_inasistencia.iloc[i]:
            prob_desercion += 0.25
        if conducta_problematica.iloc[i]:
            prob_desercion += 0.2

        desercion[i] = np.random.random() < prob_desercion

    return desercion.astype(int)

def prepare_features(df):
    """Prepara las características para el modelo"""
    df_features = df.copy()

    df_features['nota_normalizada'] = df_features['nota_final'] / 20.0

    conducta_map = {'positivo': 0, 'neutral': 1, 'agresivo': 2}
    df_features['conducta_encoded'] = df_features['conducta'].map(conducta_map)

    df_features['asistencia_normalizada'] = df_features['asistencia'] / 100.0
    df_features['inasistencia_normalizada'] = df_features['inasistencia'] / 100.0

    df_features['nota_baja'] = (df_features['nota_final'] < 11).astype(int)
    df_features['alta_inasistencia'] = (df_features['inasistencia'] > 30).astype(int)
    df_features['conducta_problematica'] = (df_features['conducta'] == 'agresivo').astype(int)

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
    print("Iniciando entrenamiento del modelo para datos reales...")

    print("Generando datos sinteticos basados en estructura real...")
    df = create_synthetic_data()

    print("Creando variable objetivo...")
    y = create_target_variable(df)

    print(f"Distribucion de desercion: {np.bincount(y)}")
    print(f"  - No desercion: {np.sum(y == 0)} ({np.mean(y == 0)*100:.1f}%)")
    print(f"  - Desercion: {np.sum(y == 1)} ({np.mean(y == 1)*100:.1f}%)")

    print("Preparando caracteristicas...")
    X, feature_columns = prepare_features(df)

    print(f"Caracteristicas preparadas: {feature_columns}")
    print(f"Forma de X: {X.shape}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("Aplicando escalado...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    print("Entrenando modelo...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        class_weight='balanced'
    )

    model.fit(X_train_scaled, y_train)

    print("Evaluando modelo...")
    y_pred = model.predict(X_test_scaled)

    accuracy = accuracy_score(y_test, y_pred)
    print(f"Precision: {accuracy:.3f}")

    print("\nReporte de clasificacion:")
    print(classification_report(y_test, y_pred))

    print("Guardando modelo...")

    model_dir = "trained"
    os.makedirs(model_dir, exist_ok=True)

    joblib.dump(model, os.path.join(model_dir, "trained_model.pkl"))
    print(f"Modelo guardado en: {os.path.join(model_dir, 'trained_model.pkl')}")

    joblib.dump(scaler, os.path.join(model_dir, "scaler.pkl"))
    print(f"Scaler guardado en: {os.path.join(model_dir, 'scaler.pkl')}")

    config = {
        'feature_columns': feature_columns,
        'expected_columns': ['estudiante_id', 'nombre', 'fecha', 'nota_final', 'asistencia', 'inasistencia', 'conducta'],
        'conducta_map': {'positivo': 0, 'neutral': 1, 'agresivo': 2},
        'model_version': '2.0',
        'training_date': '2025-01-05'
    }

    joblib.dump(config, os.path.join(model_dir, "model_config.pkl"))
    print(f"Configuracion guardada en: {os.path.join(model_dir, 'model_config.pkl')}")

    print("\nImportancia de caracteristicas:")
    feature_importance = pd.DataFrame({
        'feature': feature_columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    for _, row in feature_importance.iterrows():
        print(f"  {row['feature']}: {row['importance']:.3f}")

    print("\nModelo entrenado exitosamente")
    print(f"Archivos guardados en: {os.path.abspath(model_dir)}")

    return model, scaler, config

if __name__ == "__main__":
    main()
