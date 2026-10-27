import pandas as pd
import joblib
import os
from typing import List, Dict
import logging
import time
from config import SessionLocal
from models import ResultadoPrediccion
import numpy as np
from datetime import datetime, date

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "models", "trained")
MODEL_PATH = os.path.join(MODEL_DIR, "trained_model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
CONFIG_PATH = os.path.join(MODEL_DIR, "model_config.pkl")

try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    config = joblib.load(CONFIG_PATH)
    logger.info("Modelo ajustado a datos reales cargado exitosamente")
    logger.info(f"Columnas esperadas: {config['expected_columns']}")
except Exception as e:
    logger.warning(f"No se pudo cargar el modelo preentrenado ({e}). Reentrenando automaticamente...")
    try:
        import subprocess
        import sys
        trainer_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "models"))
        subprocess.run([sys.executable, "model_trainer.py"], cwd=trainer_dir, check=True)
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        config = joblib.load(CONFIG_PATH)
        logger.info("Modelo reentrenado y cargado exitosamente")
    except Exception as retrain_error:
        logger.error(f"Error al cargar o reentrenar el modelo: {retrain_error}")
        raise

def validate_input_data_real(df: pd.DataFrame) -> bool:
    """Valida que el DataFrame tenga las columnas exactas del sistema real"""
    critical_columns = ['nota_final', 'asistencia', 'inasistencia', 'conducta']
    missing_critical = [col for col in critical_columns if col not in df.columns]

    if missing_critical:
        logger.error(f"Faltan columnas criticas: {missing_critical}")
        logger.info(f"Columnas disponibles: {df.columns.tolist()}")
        return False

    return True

def prepare_features_real(df: pd.DataFrame, model_config: Dict = None) -> pd.DataFrame:
    """Prepara las características exactamente como el modelo entrenado las espera"""
    cfg = model_config if model_config is not None else config
    df_features = df.copy()

    df_features['nota_final'] = pd.to_numeric(df_features['nota_final'], errors='coerce').fillna(0.0)
    df_features['inasistencia'] = pd.to_numeric(df_features['inasistencia'], errors='coerce').fillna(0.0)
    df_features['asistencia'] = pd.to_numeric(df_features['asistencia'], errors='coerce').fillna(
        100.0 - df_features['inasistencia']
    )

    df_features['nota_normalizada'] = df_features['nota_final'] / 20.0

    # Soportar sinónimos de conducta provenientes de distintas plantillas CSV institucionales
    conducta_clean = df_features['conducta'].fillna('neutral').astype(str).str.strip().str.lower()
    conducta_map = {
        **cfg.get('conducta_map', {}),
        'positivo': 0,
        'buena': 0,
        'bueno': 0,
        'neutral': 1,
        'regular': 1,
        'agresivo': 2,
        'mala': 2,
        'malo': 2,
        'deficiente': 2,
    }
    df_features['conducta_encoded'] = conducta_clean.map(conducta_map).fillna(1).astype(int)

    df_features['asistencia_normalizada'] = df_features['asistencia'] / 100.0
    df_features['inasistencia_normalizada'] = df_features['inasistencia'] / 100.0

    df_features['nota_baja'] = (df_features['nota_final'] < 11).astype(int)
    df_features['alta_inasistencia'] = (df_features['inasistencia'] > 30).astype(int)
    df_features['conducta_problematica'] = conducta_clean.isin(['agresivo', 'mala', 'malo', 'deficiente']).astype(int)

    feature_columns = cfg['feature_columns']
    X = df_features[feature_columns]

    logger.info(f"Caracteristicas preparadas: {feature_columns}")

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
        file_path: Ruta al archivo CSV o Excel con la estructura real del sistema

    Returns:
        Lista de diccionarios con predicciones
    """
    try:
        if file_path.lower().endswith((".xlsx", ".xls")):
            df = pd.read_excel(file_path)
        else:
            df = pd.read_csv(file_path)

        logger.info(f"Datos cargados: {len(df)} filas")
        logger.info(f"Columnas encontradas: {df.columns.tolist()}")

        df.columns = df.columns.str.strip().str.lower()

        column_mapping = {
            'estudiante_id': 'estudiante_id',
            'id_estudiante': 'estudiante_id',
            'id': 'estudiante_id',
        }
        if 'nota_final' not in df.columns:
            if 'calificacion' in df.columns:
                column_mapping['calificacion'] = 'nota_final'
            elif 'nota' in df.columns:
                column_mapping['nota'] = 'nota_final'

        df = df.rename(columns=column_mapping)

        if 'inasistencia' not in df.columns and 'asistencia' in df.columns:
            df['inasistencia'] = (
                100.0 - pd.to_numeric(df['asistencia'], errors='coerce').fillna(0.0)
            ).clip(lower=0.0, upper=100.0)
        elif 'asistencia' not in df.columns and 'inasistencia' in df.columns:
            df['asistencia'] = (
                100.0 - pd.to_numeric(df['inasistencia'], errors='coerce').fillna(0.0)
            ).clip(lower=0.0, upper=100.0)

        logger.info(f"Columnas despues de normalizacion: {df.columns.tolist()}")
        logger.info("Primeras filas de datos:")
        for col in ['estudiante_id', 'nombre', 'nota_final', 'asistencia', 'conducta']:
            if col in df.columns:
                logger.info(f"  {col}: {df[col].head(3).tolist()}")

        if not validate_input_data_real(df):
            raise ValueError("La estructura de datos no coincide con la esperada por el modelo")

        X = prepare_features_real(df, config)
        X_scaled = scaler.transform(X)

        start_time = time.time()

        y_pred = model.predict(X_scaled)
        y_pred_proba = model.predict_proba(X_scaled)[:, 1]

        end_time = time.time()
        tiempo_prediccion = end_time - start_time

        session = SessionLocal()
        resultados = []

        logger.info(f"Procesando {len(df)} registros con modelo ajustado...")

        try:
            session.query(ResultadoPrediccion).delete()
            session.commit()
            logger.info("Registros anteriores eliminados")
        except Exception as e:
            logger.warning(f"Error limpiando registros anteriores: {e}")
            session.rollback()

        for pos_idx, (_, row) in enumerate(df.iterrows()):
            prediccion = int(y_pred[pos_idx])
            probabilidad = float(y_pred_proba[pos_idx])
            if np.isnan(probabilidad):
                probabilidad = 0.0
            riesgo = classify_risk_level(probabilidad)

            fecha_obj = date(2025, 10, 6)

            if 'fecha' in row.index and pd.notna(row['fecha']):
                try:
                    fecha_original = str(row['fecha']).strip()
                    if '/' in fecha_original:
                        parts = fecha_original.split('/')
                        if len(parts) == 3:
                            dia = int(parts[0])
                            mes = int(parts[1])
                            año = int(parts[2])
                            if año < 100:
                                año = 2000 + año if año < 50 else 1900 + año
                            fecha_obj = date(año, mes, dia)
                            logger.info(f"Fecha procesada: {fecha_original} -> {fecha_obj}")
                    elif '-' in fecha_original:
                        fecha_obj = datetime.strptime(fecha_original[:10], '%Y-%m-%d').date()
                except Exception as e:
                    logger.warning(f"Error procesando fecha {row.get('fecha')}: {e}")

            raw_id = row.get('estudiante_id')
            if pd.notna(raw_id):
                try:
                    estudiante_id = int(float(raw_id))
                except (ValueError, TypeError):
                    estudiante_id = pos_idx + 1
            else:
                estudiante_id = pos_idx + 1

            if 'nombre' in row.index and pd.notna(row['nombre']) and str(row['nombre']).strip() and str(row['nombre']).strip().lower() != 'nan':
                nombre = str(row['nombre']).strip()
            else:
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

                if estudiante_id % 2 == 1:
                    nombre = nombres_femeninos[(estudiante_id - 1) % len(nombres_femeninos)]
                else:
                    nombre = nombres_masculinos[(estudiante_id - 1) % len(nombres_masculinos)]

            raw_nota = pd.to_numeric(row.get('nota_final'), errors='coerce')
            nota_final_value = float(0.0 if pd.isna(raw_nota) else raw_nota)

            raw_inasistencia = pd.to_numeric(row.get('inasistencia'), errors='coerce')
            inasistencia_value = float(0.0 if pd.isna(raw_inasistencia) else raw_inasistencia)

            raw_asistencia = pd.to_numeric(row.get('asistencia'), errors='coerce')
            asistencia_value = float(
                max(0.0, min(100.0, 100.0 - inasistencia_value))
                if pd.isna(raw_asistencia)
                else raw_asistencia
            )

            raw_conducta = row.get('conducta')
            if pd.isna(raw_conducta) or not str(raw_conducta).strip() or str(raw_conducta).strip().lower() == 'nan':
                conducta_value = 'neutral'
            else:
                conducta_value = str(raw_conducta).strip()

            if pos_idx < 3:
                logger.info(f"Fila {pos_idx}: nota_final={nota_final_value}, asistencia={asistencia_value}")

            resultado_bd = ResultadoPrediccion(
                id_estudiante=estudiante_id,
                nombre=nombre,
                nota=nota_final_value,
                nota_final=nota_final_value,
                conducta=conducta_value,
                asistencia=asistencia_value,
                inasistencia=inasistencia_value,
                tiempo_prediccion=tiempo_prediccion,
                resultado_prediccion=str(prediccion),
                riesgo_desercion=riesgo,
                probabilidad_desercion=round(probabilidad, 4),
                fecha=fecha_obj
            )
            session.add(resultado_bd)

            resultado_dict = {
                "id_estudiante": estudiante_id,
                "nombre": nombre,
                "nota_final": nota_final_value,
                "nota": nota_final_value,  # Se mantiene por compatibilidad con el frontend
                "asistencia": asistencia_value,
                "inasistencia": inasistencia_value,
                "conducta": conducta_value,
                "fecha": fecha_obj.strftime('%Y-%m-%d'),
                "tiempo_prediccion": tiempo_prediccion,
                "resultado_prediccion": str(prediccion),
                "riesgo_desercion": riesgo,
                "probabilidad_desercion": round(probabilidad, 4)
            }
            resultados.append(resultado_dict)

        try:
            session.commit()
            logger.info(f"{len(resultados)} registros guardados en la base de datos")
        except Exception as e:
            logger.error(f"Error guardando en BD: {e}")
            session.rollback()
        finally:
            session.close()

        alto_riesgo = sum(1 for r in resultados if r['riesgo_desercion'] == 'Alto')
        medio_riesgo = sum(1 for r in resultados if r['riesgo_desercion'] == 'Medio')
        bajo_riesgo = sum(1 for r in resultados if r['riesgo_desercion'] == 'Bajo')

        logger.info(f"Predicciones completadas en {tiempo_prediccion:.4f}s")
        logger.info(f"Distribucion: Alto={alto_riesgo}, Medio={medio_riesgo}, Bajo={bajo_riesgo}")

        return resultados

    except Exception as e:
        logger.error(f"Error en prediccion: {str(e)}")
        raise Exception(f"Error al procesar las predicciones: {str(e)}")

CONDUCTA_MAP = {
    "positivo": 0, "buena": 0, "bueno": 0,
    "neutral": 1, "regular": 1,
    "agresivo": 2, "mala": 2, "malo": 2, "deficiente": 2
}

def encode_conducta(valor: str) -> int:
    """Función de compatibilidad para codificar conducta"""
    return CONDUCTA_MAP.get(str(valor).strip().lower(), 1)
