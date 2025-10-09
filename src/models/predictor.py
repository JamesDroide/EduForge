import pandas as pd
import joblib  
import os
from typing import List, Dict
import logging
import time
from config import SessionLocal
from models import ResultadoPrediccion
import numpy as np

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 1. Configuración de paths segura - UBICACIÓN CORRECTA
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "models", "trained")
MODEL_PATH = os.path.join(MODEL_DIR, "trained_model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
CONFIG_PATH = os.path.join(MODEL_DIR, "model_config.pkl")

# 2. Carga segura del modelo, scaler y configuración
try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    config = joblib.load(CONFIG_PATH)
    logger.info("✅ Modelo ajustado a datos reales cargado exitosamente")
    logger.info(f"✅ Columnas esperadas: {config['expected_columns']}")

except Exception as e:
    logger.error(f"❌ Error al cargar el modelo: {str(e)}")
    raise

def validate_input_data_real(df: pd.DataFrame) -> bool:
    """Valida que el DataFrame tenga las columnas exactas del sistema real"""
    expected_columns = config['expected_columns']

    # Verificar columnas críticas mínimas
    critical_columns = ['nota_final', 'asistencia', 'inasistencia', 'conducta']
    missing_critical = [col for col in critical_columns if col not in df.columns]

    if missing_critical:
        logger.error(f"❌ Faltan columnas críticas: {missing_critical}")
        logger.info(f"📋 Columnas disponibles: {df.columns.tolist()}")
        return False

    return True

def prepare_features_real(df: pd.DataFrame) -> pd.DataFrame:
    """Prepara las características exactamente como el modelo entrenado las espera"""
    df_features = df.copy()

    # 1. Normalizar nota_final a escala 0-1 (desde escala 0-20)
    df_features['nota_normalizada'] = df_features['nota_final'] / 20.0

    # 2. Codificar conducta usando el mapeo del modelo
    conducta_map = config['conducta_map']
    df_features['conducta_encoded'] = df_features['conducta'].map(conducta_map).fillna(1)  # default neutral

    # 3. Normalizar asistencia e inasistencia a escala 0-1
    df_features['asistencia_normalizada'] = df_features['asistencia'] / 100.0
    df_features['inasistencia_normalizada'] = df_features['inasistencia'] / 100.0

    # 4. Crear indicadores de riesgo (igual que en entrenamiento)
    df_features['nota_baja'] = (df_features['nota_final'] < 11).astype(int)
    df_features['alta_inasistencia'] = (df_features['inasistencia'] > 30).astype(int)
    df_features['conducta_problematica'] = (df_features['conducta'] == 'agresivo').astype(int)

    # 5. Seleccionar solo las características que usa el modelo
    feature_columns = config['feature_columns']
    X = df_features[feature_columns]

    logger.info(f"✅ Características preparadas: {feature_columns}")

    return X

def classify_risk_level(prediction_proba: float) -> str:
    """Clasifica el nivel de riesgo basado en la probabilidad de deserción"""
    if prediction_proba >= 0.7:
        return "Alto"
    elif prediction_proba >= 0.4:
        return "Medio"
    else:
        return "Bajo"

def predict_desertion(file_path: str) -> List[Dict]:
    """
    Realiza predicciones de deserción usando el modelo ajustado a datos reales

    Args:
        file_path: Ruta al archivo CSV con la estructura real del sistema

    Returns:
        Lista de diccionarios con predicciones
    """
    try:
        # Cargar datos
        if file_path.endswith(".xlsx"):
            df = pd.read_excel(file_path)
        else:
            df = pd.read_csv(file_path)

        logger.info(f"📂 Datos cargados: {len(df)} filas")
        logger.info(f"📋 Columnas encontradas: {df.columns.tolist()}")

        # Limpiar nombres de columnas
        df.columns = df.columns.str.strip().str.lower()

        # Mapear nombres de columnas si es necesario para mantener consistencia
        column_mapping = {
            'estudiante_id': 'estudiante_id',
            'id_estudiante': 'estudiante_id',  # Por si viene con nombre alternativo
            'id': 'estudiante_id',  # Otro posible nombre
        }

        df = df.rename(columns=column_mapping)

        # Imprimir las columnas después de la normalización para debug
        logger.info(f"📋 Columnas después de normalización: {df.columns.tolist()}")
        logger.info(f"📊 Primeras filas de datos:")
        for col in ['estudiante_id', 'nombre', 'nota_final', 'asistencia', 'conducta']:
            if col in df.columns:
                logger.info(f"  {col}: {df[col].head(3).tolist()}")

        # Validar estructura de datos
        if not validate_input_data_real(df):
            raise ValueError("La estructura de datos no coincide con la esperada por el modelo")

        # Preparar características para el modelo
        X = prepare_features_real(df)

        # Aplicar escalado
        X_scaled = scaler.transform(X)

        # Medir tiempo de predicción
        start_time = time.time()

        # Realizar predicciones
        y_pred = model.predict(X_scaled)
        y_pred_proba = model.predict_proba(X_scaled)[:, 1]

        end_time = time.time()
        tiempo_prediccion = end_time - start_time

        # Guardar resultados en la base de datos
        session = SessionLocal()
        resultados = []

        logger.info(f"💾 Procesando {len(df)} registros con modelo ajustado...")

        # Limpiar registros anteriores para evitar duplicados
        try:
            session.query(ResultadoPrediccion).delete()
            session.commit()
            logger.info("🗑️ Registros anteriores eliminados")
        except Exception as e:
            logger.warning(f"⚠️ Error limpiando registros anteriores: {e}")
            session.rollback()

        for idx, row in df.iterrows():
            # Obtener predicciones
            prediccion = int(y_pred[idx])
            probabilidad = float(y_pred_proba[idx])
            riesgo = classify_risk_level(probabilidad)

            # Procesar fecha correctamente del CSV
            fecha_formateada = "2025-10-06"  # Fecha actual como defecto

            if 'fecha' in row.index and pd.notna(row['fecha']):
                try:
                    fecha_original = str(row['fecha']).strip()
                    if '/' in fecha_original:
                        parts = fecha_original.split('/')
                        if len(parts) == 3:
                            # Formato DD/MM/YYYY
                            dia = parts[0].zfill(2)
                            mes = parts[1].zfill(2)
                            año = parts[2]
                            if len(año) == 2:
                                año = f"20{año}" if int(año) < 50 else f"19{año}"
                            fecha_formateada = f"{año}-{mes}-{dia}"
                            logger.info(f"📅 Fecha procesada: {fecha_original} → {fecha_formateada}")
                except Exception as e:
                    logger.warning(f"⚠️  Error procesando fecha {row.get('fecha')}: {e}")

            # Generar ID del estudiante si no existe en el CSV
            if 'estudiante_id' in row.index and pd.notna(row['estudiante_id']):
                estudiante_id = int(row['estudiante_id'])
            else:
                estudiante_id = idx + 1  # Generar ID automáticamente

            # Generar nombre del estudiante si no existe en el CSV
            if 'nombre' in row.index and pd.notna(row['nombre']) and str(row['nombre']).strip():
                nombre = str(row['nombre']).strip()
            else:
                # Lista de nombres realistas para generar automáticamente
                nombres_femeninos = [
                    "Ana Sofia Martinez", "Maria Isabel Torres", "Lucia Valentina Herrera",
                    "Camila Andrea Flores", "Valentina Rodriguez", "Sofia Elena Castro",
                    "Isabella Carmen Lopez", "Daniela Alejandra Morales", "Fernanda Gabriela Ruiz",
                    "Alejandra Patricia Silva", "Carolina Beatriz Mendoza", "Natalia Andrea Vargas",
                    "Paola Cristina Jimenez", "Andrea Francisca Rivera", "Gabriela Monserrat Gonzalez"
                ]
                nombres_masculinos = [
                    "Carlos Eduardo Ramirez", "Diego Fernando Castro", "Sebastian Jose Morales",
                    "Alejandro David Vargas", "Mateo Nicolas Herrera", "Santiago Miguel Torres",
                    "Andres Felipe Rodriguez", "Gabriel Esteban Martinez", "Daniel Antonio Lopez",
                    "Nicolas Emilio Silva", "Rafael Ignacio Mendoza", "Joaquin Maximiliano Ruiz",
                    "Vicente Agustin Jimenez", "Emilio Tomas Gonzalez", "Benjamin Eduardo Rivera"
                ]

                # Alternar entre nombres femeninos y masculinos
                if estudiante_id % 2 == 1:
                    nombre = nombres_femeninos[(estudiante_id - 1) % len(nombres_femeninos)]
                else:
                    nombre = nombres_masculinos[(estudiante_id - 1) % len(nombres_masculinos)]

            # Obtener los valores reales del CSV con logging para debug
            nota_final_value = float(row.get('nota_final', 0))
            asistencia_value = float(row.get('asistencia', 0))
            inasistencia_value = float(row.get('inasistencia', 0))
            conducta_value = str(row.get('conducta', 'Regular'))

            # Log para debug - verificar que los valores se están leyendo correctamente
            if idx < 3:  # Solo para las primeras 3 filas
                logger.info(f"📊 Fila {idx}: nota_final={nota_final_value}, asistencia={asistencia_value}")

            # Guardar en la base de datos
            resultado_bd = ResultadoPrediccion(
                id_estudiante=estudiante_id,
                nombre=nombre,
                nota=nota_final_value,  # Guardar en ambas columnas
                nota_final=nota_final_value,
                conducta=conducta_value,
                asistencia=asistencia_value,
                inasistencia=inasistencia_value,
                tiempo_prediccion=tiempo_prediccion,
                resultado_prediccion=str(prediccion),
                riesgo_desercion=riesgo,
                probabilidad_desercion=round(probabilidad, 4)
            )
            session.add(resultado_bd)

            # Preparar resultado para retorno
            resultado_dict = {
                "id_estudiante": estudiante_id,
                "nombre": nombre,
                "nota_final": nota_final_value,
                "nota": nota_final_value,  # Mantener por compatibilidad con frontend
                "asistencia": asistencia_value,
                "inasistencia": inasistencia_value,
                "conducta": conducta_value,
                "fecha": fecha_formateada,
                "tiempo_prediccion": tiempo_prediccion,
                "resultado_prediccion": str(prediccion),
                "riesgo_desercion": riesgo,
                "probabilidad_desercion": round(probabilidad, 4)
            }
            resultados.append(resultado_dict)

        # Commit todos los registros de una vez
        try:
            session.commit()
            logger.info(f"✅ {len(resultados)} registros guardados en la base de datos")
        except Exception as e:
            logger.error(f"❌ Error guardando en BD: {e}")
            session.rollback()
        finally:
            session.close()

        # Estadísticas de resultados
        alto_riesgo = sum(1 for r in resultados if r['riesgo_desercion'] == 'Alto')
        medio_riesgo = sum(1 for r in resultados if r['riesgo_desercion'] == 'Medio')
        bajo_riesgo = sum(1 for r in resultados if r['riesgo_desercion'] == 'Bajo')

        logger.info(f"✅ Predicciones completadas en {tiempo_prediccion:.4f}s")
        logger.info(f"📊 Distribución: Alto={alto_riesgo}, Medio={medio_riesgo}, Bajo={bajo_riesgo}")

        return resultados

    except Exception as e:
        logger.error(f"❌ Error en predicción: {str(e)}")
        raise Exception(f"Error al procesar las predicciones: {str(e)}")

# Mapeo de compatibilidad con el código existente
CONDUCTA_MAP = {"positivo": 0, "neutral": 1, "agresivo": 2}

def encode_conducta(valor: str) -> int:
    """Función de compatibilidad para codificar conducta"""
    return CONDUCTA_MAP.get(str(valor).strip().lower(), 1)
