import os
from fastapi import UploadFile
import pandas as pd
from models import StudentData, ResultadoPrediccion
from config import SessionLocal
from services.risk_service import clear_latest_predictions
from services.attendance_service import clear_latest_csv_data
from datetime import datetime

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

def excel_date_to_str(excel_date):
    try:
        if isinstance(excel_date, str):
            try:
                datetime.strptime(excel_date, '%Y-%m-%d')
                return excel_date
            except Exception:
                try:
                    dt = datetime.strptime(excel_date, '%d/%m/%Y')
                    return dt.strftime('%Y-%m-%d')
                except Exception:
                    return '2025-01-01'

        # Base de serie temporal de Excel (30 de diciembre de 1899)
        base_date = datetime(1899, 12, 30)
        date = base_date + pd.to_timedelta(float(excel_date), unit='D')
        return date.strftime('%Y-%m-%d')
    except Exception:
        return '2025-01-01'

def clear_previous_data():
    """
    Función para limpiar todos los datos anteriores del dashboard
    """
    session = SessionLocal()
    try:
        deleted_predictions = session.query(ResultadoPrediccion).delete()
        deleted_students = session.query(StudentData).delete()

        session.commit()
        clear_latest_predictions()
        clear_latest_csv_data()
        print(f"Datos limpiados: {deleted_predictions} predicciones, {deleted_students} estudiantes")

    except Exception as e:
        session.rollback()
        print(f"Error limpiando datos anteriores: {str(e)}")
        raise e
    finally:
        session.close()

async def save_uploaded_file(file: UploadFile):
    safe_filename = os.path.basename(file.filename)
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    if safe_filename.lower().endswith(('.csv', '.xlsx', '.xls')):
        if safe_filename.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            df = pd.read_csv(file_path)

        df.columns = df.columns.str.strip().str.lower()

        session = SessionLocal()
        try:
            for _, row in df.iterrows():
                fecha_val = row.get('fecha', '2025-01-01')
                if pd.isna(fecha_val):
                    fecha_dt = datetime(2025, 1, 1)
                elif isinstance(fecha_val, datetime):
                    fecha_dt = fecha_val
                elif isinstance(fecha_val, (float, int)) or (isinstance(fecha_val, str) and fecha_val.replace('.', '', 1).isdigit()):
                    fecha_str = excel_date_to_str(fecha_val)
                    parsed_dt = pd.to_datetime(fecha_str, errors='coerce')
                    fecha_dt = parsed_dt.to_pydatetime() if not pd.isna(parsed_dt) else datetime(2025, 1, 1)
                else:
                    fecha_str = str(fecha_val).strip()
                    parsed_dt = pd.to_datetime(fecha_str, format='%Y-%m-%d', errors='coerce')
                    if pd.isna(parsed_dt):
                        parsed_dt = pd.to_datetime(fecha_str, dayfirst=True, errors='coerce')
                    fecha_dt = parsed_dt.to_pydatetime() if not pd.isna(parsed_dt) else datetime(2025, 1, 1)

                est_id_raw = row.get('estudiante_id', row.get('id', 0))
                id_estudiante = 0 if pd.isna(est_id_raw) else int(float(est_id_raw))

                nombre_raw = row.get('nombre', '')
                nombre = '' if pd.isna(nombre_raw) else str(nombre_raw).strip()

                nota_raw = row.get('nota_final', row.get('nota', 0))
                nota_final = 0.0 if pd.isna(nota_raw) else float(nota_raw)

                asistencia_raw = row.get('asistencia', 0)
                asistencia = 0.0 if pd.isna(asistencia_raw) else float(asistencia_raw)

                inasistencia_raw = row.get('inasistencia', 0)
                inasistencia = 0.0 if pd.isna(inasistencia_raw) else float(inasistencia_raw)

                conducta_raw = row.get('conducta', 'Regular')
                conducta = 'Regular' if pd.isna(conducta_raw) or not str(conducta_raw).strip() else str(conducta_raw).strip()

                student = StudentData(
                    id_estudiante=id_estudiante,
                    nombre=nombre,
                    nota_final=nota_final,
                    asistencia=asistencia,
                    inasistencia=inasistencia,
                    conducta=conducta,
                    fecha=fecha_dt.date()
                )
                session.add(student)
            session.commit()
        finally:
            session.close()

    return file_path
