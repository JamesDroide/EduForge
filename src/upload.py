import os
from fastapi import UploadFile
import pandas as pd
from models import StudentData, ResultadoPrediccion
from config import SessionLocal
from datetime import datetime

# Usar la misma ruta que en main.py para consistencia
UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "uploads"))
os.makedirs(UPLOAD_DIR, exist_ok=True)

def excel_date_to_str(excel_date):
    # Excel date serial number to datetime
    try:
        if isinstance(excel_date, str):
            # Si ya es string, verificar si es una fecha válida
            try:
                datetime.strptime(excel_date, '%Y-%m-%d')
                return excel_date
            except:
                try:
                    datetime.strptime(excel_date, '%d/%m/%Y')
                    # Convertir formato DD/MM/YYYY a YYYY-MM-DD
                    dt = datetime.strptime(excel_date, '%d/%m/%Y')
                    return dt.strftime('%Y-%m-%d')
                except:
                    return '2025-01-01'

        # Si es número (formato Excel)
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
        # Eliminar todos los registros de predicciones anteriores
        deleted_predictions = session.query(ResultadoPrediccion).delete()

        # Eliminar todos los datos de estudiantes anteriores
        deleted_students = session.query(StudentData).delete()

        session.commit()
        print(f"✅ Datos limpiados: {deleted_predictions} predicciones, {deleted_students} estudiantes")

    except Exception as e:
        session.rollback()
        print(f"❌ Error limpiando datos anteriores: {str(e)}")
        raise e
    finally:
        session.close()

async def save_uploaded_file(file: UploadFile):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    # Procesar el CSV y guardar los datos en la base de datos
    if file.filename.endswith('.csv'):
        df = pd.read_csv(file_path)
        session = SessionLocal()
        try:
            for _, row in df.iterrows():
                student = StudentData(
                    id_estudiante=int(row.get('estudiante_id', row.get('id', 0))),
                    nombre=str(row.get('nombre', '')),
                    nota_final=float(row.get('nota_final', 0)),
                    asistencia=float(row.get('asistencia', 0)),
                    inasistencia=float(row.get('inasistencia', 0)),
                    conducta=str(row.get('conducta', ''))
                )
                session.add(student)
            session.commit()
            print(f"✅ Se guardaron {len(df)} estudiantes en la base de datos")
        except Exception as e:
            session.rollback()
            print(f"❌ Error guardando estudiantes: {str(e)}")
            raise e
        finally:
            session.close()

    return file_path
