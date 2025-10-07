# src/services/risk_service.py

from sqlalchemy.orm import Session
from config import SessionLocal
from models import ResultadoPrediccion

# Variable global para almacenar los últimos resultados de predicción del CSV
latest_predictions = []

class RiskService:

    def __init__(self):
        # Cargar el modelo de predicción
        # self.model = PredictionModel(model_path="path_to_your_model.pkl")  # Ajusta la ruta de tu modelo
        # Comentado porque PredictionModel no está definido
        pass

    def get_students_at_risk(self):
        """
        Función para obtener TODOS los estudiantes con sus niveles de riesgo (incluyendo Bajo, Medio y Alto)
        """
        global latest_predictions

        print(f"🔍 DEBUG: get_students_at_risk llamado")
        print(f"🔍 DEBUG: latest_predictions tiene {len(latest_predictions)} elementos")

        if len(latest_predictions) > 0:
            print(f"🔍 DEBUG: Primeros 3 elementos de latest_predictions:")
            for i, pred in enumerate(latest_predictions[:3]):
                print(f"  {i}: {pred}")

        # Si tenemos datos frescos del CSV, usarlos
        if latest_predictions:
            all_students = []
            for prediction in latest_predictions:
                # INCLUIR TODOS LOS ESTUDIANTES independientemente del nivel de riesgo
                risk_level = prediction.get("riesgo_desercion", "Bajo")

                # Extraer los valores correctos con múltiples nombres posibles
                nota_value = prediction.get("nota_final", prediction.get("nota", 0))
                asistencia_value = prediction.get("asistencia", 0)

                print(f"🔍 DEBUG: Procesando estudiante {prediction.get('nombre', 'N/A')}: nota={nota_value}, asistencia={asistencia_value}")

                all_students.append({
                    "student_id": prediction.get("id_estudiante"),
                    "name": prediction.get("nombre", f"Estudiante {prediction.get('id_estudiante')}"),
                    "grade": "Primaria" if prediction.get("id_estudiante", 0) < 1000 else "Secundaria",
                    "risk_level": risk_level,
                    "nota": float(nota_value),  # Asegurar que sea float
                    "nota_final": float(nota_value),  # Para compatibilidad
                    "asistencia": float(asistencia_value),  # Asegurar que sea float
                    "conducta": prediction.get("conducta", "Regular"),
                    "inasistencia": prediction.get("inasistencia", 0)
                })

            print(f"🔍 DEBUG: Devolviendo {len(all_students)} estudiantes")
            if len(all_students) > 0:
                print(f"🔍 DEBUG: Primer estudiante a devolver: {all_students[0]}")

            return all_students

        # Si no hay datos del CSV, intentar usar la base de datos (fallback)
        db = SessionLocal()
        try:
            # Obtener todos los resultados de predicción
            results = db.query(ResultadoPrediccion).all()

            # Si no hay datos, devolver lista vacía
            if not results:
                return []

            all_students = []

            for result in results:
                # Determinar el nivel de riesgo basado en la predicción
                risk_level = "Alto" if int(result.resultado_prediccion) == 1 else "Bajo"

                # INCLUIR TODOS LOS ESTUDIANTES (no solo los de alto riesgo)
                all_students.append({
                    "student_id": result.id_estudiante,
                    "name": f"Estudiante {result.id_estudiante}",  # Placeholder para el nombre
                    "grade": "Primaria" if result.id_estudiante < 1000 else "Secundaria",
                    "risk_level": risk_level,
                    "nota": result.nota,
                    "asistencia": result.asistencia,
                    "conducta": "Regular"  # Valor por defecto
                })
            return all_students
        finally:
            db.close()

    def get_monthly_dropout_risk_summary(self):
        """
        Devuelve el riesgo de deserción por mes con cantidades y porcentajes basado en datos del CSV.
        """
        global latest_predictions

        if not latest_predictions:
            # Si no hay datos del CSV, devolver datos vacíos
            return {
                "labels": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
                "data": [0]*12,
                "counts": [0]*12  # Cantidades de estudiantes
            }

        try:
            import pandas as pd

            # Convertir a DataFrame
            df = pd.DataFrame(latest_predictions)

            # Convertir fechas
            df['fecha_dt'] = pd.to_datetime(df['fecha'], format='%Y-%m-%d', errors='coerce')
            df = df.dropna(subset=['fecha_dt'])

            if df.empty:
                return {
                    "labels": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
                    "data": [0]*12,
                    "counts": [0]*12
                }

            # Obtener el mes de cada fecha
            df["month"] = df["fecha_dt"].dt.month

            # Calcular tanto porcentajes como cantidades por mes
            df["en_riesgo"] = (df["riesgo_desercion"] == "Alto").astype(int)

            # Agrupar por mes
            monthly_stats = df.groupby("month").agg({
                'en_riesgo': ['sum', 'count', 'mean']  # suma, total, promedio
            }).reindex(range(1,13), fill_value=0)

            # Extraer datos
            counts = monthly_stats[('en_riesgo', 'sum')].tolist()  # Cantidad de estudiantes en riesgo
            totals = monthly_stats[('en_riesgo', 'count')].tolist()  # Total de estudiantes por mes
            percentages = [
                round((counts[i] / totals[i] * 100) if totals[i] > 0 else 0, 1)
                for i in range(12)
            ]

            labels = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

            return {
                "labels": labels,
                "data": percentages,  # Porcentajes para el gráfico
                "counts": counts,     # Cantidades para mostrar en tooltips
                "totals": totals      # Totales para contexto
            }

        except Exception as e:
            print(f"Error calculando resumen de riesgo: {e}")
            return {
                "labels": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
                "data": [0]*12,
                "counts": [0]*12,
                "totals": [0]*12
            }

# Función para actualizar los datos más recientes del CSV
def update_latest_predictions(predictions):
    """Actualiza la variable global con los últimos resultados de predicción"""
    global latest_predictions

    print(f"🔍 DEBUG: update_latest_predictions llamado con {len(predictions)} predicciones")
    if len(predictions) > 0:
        print(f"🔍 DEBUG: Primera predicción: {predictions[0]}")
        # Verificar que las notas estén correctas
        primera = predictions[0]
        print(f"🔍 DEBUG: Nota en primera predicción: {primera.get('nota_final', 'NO ENCONTRADA')}")
        print(f"🔍 DEBUG: Asistencia en primera predicción: {primera.get('asistencia', 'NO ENCONTRADA')}")

    latest_predictions = predictions
    print(f"🔍 DEBUG: Variable global actualizada. Ahora tiene {len(latest_predictions)} elementos")
