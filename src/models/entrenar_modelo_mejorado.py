"""
Modelo Mejorado Simplificado - Predicción de Deserción
======================================================
Versión optimizada y práctica del modelo mejorado
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.preprocessing import StandardScaler
import joblib
import os
import warnings
warnings.filterwarnings('ignore')

def crear_modelo_mejorado():
    """Crea un modelo Random Forest mejorado con mejores hiperparámetros"""
    return RandomForestClassifier(
        n_estimators=300,          # Más árboles para mejor precisión
        max_depth=12,              # Mayor profundidad 
        min_samples_split=3,       # Menos división mínima
        min_samples_leaf=1,        # Hojas más pequeñas
        max_features='sqrt',       # Características óptimas
        bootstrap=True,            # Bootstrap sampling
        oob_score=True,           # Out-of-bag score
        class_weight='balanced',   # Balance de clases
        random_state=42,
        n_jobs=-1                 # Usar todos los cores
    )

def cargar_y_procesar_datos():
    """Carga y procesa los datos de manera optimizada"""
    # Ruta a los datos
    data_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "student_data_preprocesado.csv")
    
    if not os.path.exists(data_path):
        print(f"Error: No se encontró el archivo {data_path}")
        return None, None
        
    # Cargar datos
    df = pd.read_csv(data_path)
    print(f"Datos cargados: {df.shape[0]} filas, {df.shape[1]} columnas")
    
    # Crear variable objetivo mejorada
    # Combinar nota_final baja Y otros factores de riesgo
    df['deserta'] = 0
    
    # Criterios múltiples para deserción
    conditions = []
    
    # 1. Nota final muy baja (< 0.35 equivale a menos de 7/20)
    if 'nota_final' in df.columns:
        conditions.append(df['nota_final'] < 0.35)
    
    # 2. Alto ausentismo (más del percentil 80)
    if 'ausencias' in df.columns:
        high_absence_threshold = df['ausencias'].quantile(0.8)
        conditions.append(df['ausencias'] > high_absence_threshold)
    
    # 3. Combinación de nota baja + factores de riesgo
    if 'nota_final' in df.columns and 'fracasos_anteriores' in df.columns:
        conditions.append((df['nota_final'] < 0.45) & (df['fracasos_anteriores'] > 0))
    
    # Aplicar condiciones OR
    if conditions:
        df['deserta'] = np.where(
            np.logical_or.reduce(conditions), 1, 0
        )
    
    # Feature Engineering Mejorado
    df = feature_engineering_avanzado(df)
    
    # Eliminar columnas no numéricas para simplificar
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df_numeric = df[numeric_cols].copy()
    
    # Manejo de valores faltantes
    df_numeric = df_numeric.fillna(df_numeric.median())
    
    print(f"Distribución de deserción: {df_numeric['deserta'].value_counts().to_dict()}")
    
    return df_numeric, df_numeric['deserta']

def feature_engineering_avanzado(df):
    """Crea características derivadas más inteligentes"""
    print("Aplicando feature engineering avanzado...")
    
    # 1. Progreso entre períodos
    if 'nota_periodo_1' in df.columns and 'nota_periodo_2' in df.columns:
        df['progreso_notas'] = df['nota_periodo_2'] - df['nota_periodo_1']
        df['tendencia_negativa'] = (df['progreso_notas'] < -0.1).astype(int)
        df['mejora_significativa'] = (df['progreso_notas'] > 0.15).astype(int)
    
    # 2. Indicadores de riesgo combinados
    if 'ausencias' in df.columns:
        df['ausentismo_critico'] = (df['ausencias'] > df['ausencias'].quantile(0.85)).astype(int)
    
    # 3. Rendimiento académico general
    nota_cols = [col for col in df.columns if 'nota' in col.lower()]
    if len(nota_cols) > 1:
        df['promedio_general'] = df[nota_cols].mean(axis=1)
        df['consistencia_notas'] = df[nota_cols].std(axis=1)
        df['bajo_rendimiento'] = (df['promedio_general'] < 0.4).astype(int)
    
    # 4. Factores socioeconómicos
    if 'nivel_educativo_madre' in df.columns and 'nivel_educativo_padre' in df.columns:
        df['educacion_padres_promedio'] = (df['nivel_educativo_madre'] + df['nivel_educativo_padre']) / 2
        df['educacion_padres_baja'] = (df['educacion_padres_promedio'] < 0.3).astype(int)
    
    # 5. Tiempo y dedicación
    tiempo_cols = [col for col in df.columns if 'tiempo' in col.lower()]
    if len(tiempo_cols) > 0:
        df['tiempo_total'] = df[tiempo_cols].sum(axis=1)
        df['baja_dedicacion'] = (df['tiempo_total'] < df['tiempo_total'].quantile(0.25)).astype(int)
    
    return df

def entrenar_modelo_mejorado():
    """Entrena el modelo con todas las mejoras"""
    print("="*50)
    print("ENTRENANDO MODELO MEJORADO DE DESERCIÓN")
    print("="*50)
    
    # Cargar datos
    df, y = cargar_y_procesar_datos()
    if df is None:
        return
    
    # Preparar características
    X = df.drop(columns=['deserta'])
    
    print(f"Características utilizadas: {X.shape[1]}")
    print(f"Muestras totales: {X.shape[0]}")
    
    # División estratificada
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    
    # Escalado de características
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print("Entrenando modelo Random Forest mejorado...")
    
    # Crear y entrenar modelo mejorado
    modelo_mejorado = crear_modelo_mejorado()
    modelo_mejorado.fit(X_train_scaled, y_train)
    
    print(f"OOB Score: {modelo_mejorado.oob_score_:.4f}")
    
    # Evaluación
    print("\nEvaluando modelo...")
    
    # Predicciones
    y_pred_train = modelo_mejorado.predict(X_train_scaled)
    y_pred_test = modelo_mejorado.predict(X_test_scaled)
    
    # Métricas de entrenamiento
    train_accuracy = accuracy_score(y_train, y_pred_train)
    test_accuracy = accuracy_score(y_test, y_pred_test)
    
    print(f"\nExactitud Entrenamiento: {train_accuracy:.4f}")
    print(f"Exactitud Prueba: {test_accuracy:.4f}")
    print(f"Diferencia (Overfitting): {train_accuracy - test_accuracy:.4f}")
    
    # Validación cruzada
    cv_scores = cross_val_score(modelo_mejorado, X_train_scaled, y_train, cv=5, scoring='accuracy')
    print(f"\nValidación Cruzada: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    # Reporte detallado
    print("\nReporte de Clasificación (Conjunto de Prueba):")
    print(classification_report(y_test, y_pred_test))
    
    print("\nMatriz de Confusión:")
    cm = confusion_matrix(y_test, y_pred_test)
    print(cm)
    
    # Importancia de características
    print("\nTOP 10 CARACTERÍSTICAS MÁS IMPORTANTES:")
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': modelo_mejorado.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(feature_importance.head(10).to_string(index=False))
    
    # Guardar modelo mejorado
    print("\nGuardando modelo mejorado...")
    
    model_path = os.path.join(os.path.dirname(__file__), "trained_model.pkl")
    scaler_path = os.path.join(os.path.dirname(__file__), "scaler.pkl")
    
    joblib.dump(modelo_mejorado, model_path)
    joblib.dump(scaler, scaler_path)
    
    print(f"Modelo guardado en: {model_path}")
    print(f"Scaler guardado en: {scaler_path}")
    
    # Crear modelo de comparación (modelo anterior simple)
    print("\n" + "="*50)
    print("COMPARACIÓN CON MODELO ANTERIOR")
    print("="*50)
    
    # Modelo simple para comparar
    modelo_simple = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight='balanced'
    )
    
    modelo_simple.fit(X_train_scaled, y_train)
    y_pred_simple = modelo_simple.predict(X_test_scaled)
    simple_accuracy = accuracy_score(y_test, y_pred_simple)
    
    mejora = ((test_accuracy - simple_accuracy) / simple_accuracy) * 100
    
    print(f"Modelo Anterior (Simple): {simple_accuracy:.4f}")
    print(f"Modelo Mejorado:         {test_accuracy:.4f}")
    print(f"Mejora:                  {mejora:+.2f}%")
    
    print("\n🎉 ¡MODELO MEJORADO ENTRENADO EXITOSAMENTE!")
    print("El modelo está listo para hacer predicciones más precisas.")
    
    return modelo_mejorado, scaler

def evaluar_modelo_actual():
    """Evalúa el modelo actualmente guardado"""
    try:
        model_path = os.path.join(os.path.dirname(__file__), "trained_model.pkl")
        scaler_path = os.path.join(os.path.dirname(__file__), "scaler.pkl")
        
        if os.path.exists(model_path):
            model = joblib.load(model_path)
            scaler = joblib.load(scaler_path) if os.path.exists(scaler_path) else None
            
            print("✅ Modelo mejorado cargado exitosamente")
            print(f"Tipo de modelo: {type(model).__name__}")
            
            if hasattr(model, 'n_estimators'):
                print(f"Número de árboles: {model.n_estimators}")
            if hasattr(model, 'oob_score_'):
                print(f"OOB Score: {model.oob_score_:.4f}")
                
            return True
        else:
            print("❌ No se encontró modelo entrenado")
            return False
            
    except Exception as e:
        print(f"❌ Error al cargar modelo: {e}")
        return False

if __name__ == "__main__":
    # Verificar si ya existe un modelo entrenado
    if evaluar_modelo_actual():
        respuesta = input("\n¿Quieres re-entrenar el modelo? (s/n): ")
        if respuesta.lower() not in ['s', 'si', 'yes', 'y']:
            print("Manteniendo modelo actual.")
            exit()
    
    # Entrenar modelo mejorado
    entrenar_modelo_mejorado()
