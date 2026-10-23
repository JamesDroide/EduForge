from config import SessionLocal
from models import ResultadoPrediccion

latest_predictions = []

def clear_latest_predictions():
    """Limpia la variable global de predicciones"""
    global latest_predictions
    latest_predictions = []
    print("Variable global latest_predictions limpiada")

class RiskService:

    def __init__(self):
        pass

    def get_students_at_risk(self):
        """
        Función para obtener TODOS los estudiantes con sus niveles de riesgo desde la BASE DE DATOS
        """
        global latest_predictions

        # Evitar mostrar registros de sesiones anteriores hasta que se cargue un CSV en la sesión actual
        if not latest_predictions or len(latest_predictions) == 0:
            print("No hay predicciones cargadas en esta sesion")
            return []

        db = SessionLocal()
        try:
            results = db.query(ResultadoPrediccion).all()

            print(f"DEBUG: get_students_at_risk - {len(results)} registros encontrados en BD")

            if not results:
                print("No hay datos en la base de datos")
                return []

            all_students = []

            for result in results:
                nota_value = result.nota_final if result.nota_final is not None else 0.0
                asistencia_value = result.asistencia if result.asistencia is not None else 0
                conducta_value = result.conducta if result.conducta is not None else "Regular"
                risk_level = result.riesgo_desercion if result.riesgo_desercion else "Bajo"

                print(f"DEBUG: Procesando estudiante {result.nombre}: nota={nota_value}, asistencia={asistencia_value}, riesgo={result.riesgo_desercion}")

                all_students.append({
                    "student_id": result.id_estudiante,
                    "name": result.nombre if result.nombre else f"Estudiante {result.id_estudiante}",
                    "grade": "Primaria" if result.id_estudiante < 1000 else "Secundaria",
                    "risk_level": risk_level,
                    "riesgo_desercion": risk_level,
                    "nota": float(nota_value),
                    "nota_final": float(nota_value),
                    "asistencia": float(asistencia_value),
                    "conducta": conducta_value,
                    "inasistencia": float(result.inasistencia) if result.inasistencia else 0,
                    "probabilidad_desercion": float(result.probabilidad_desercion) if result.probabilidad_desercion else 0,
                    "resultado_prediccion": result.resultado_prediccion,
                    "tiempo_prediccion": float(result.tiempo_prediccion) if result.tiempo_prediccion is not None else None
                })

            print(f"DEBUG: Devolviendo {len(all_students)} estudiantes desde BD")
            if len(all_students) > 0:
                print(f"DEBUG: Primer estudiante: {all_students[0]}")

            return all_students

        except Exception as e:
            print(f"Error leyendo desde BD: {e}")
            return []
        finally:
            db.close()

    def get_monthly_dropout_risk_summary(self):
        """
        Devuelve el riesgo de deserción por mes con cantidades y porcentajes basado en datos del CSV.
        """
        global latest_predictions

        if not latest_predictions:
            return {
                "labels": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
                "data": [0]*12,
                "counts": [0]*12
            }

        try:
            import pandas as pd

            df = pd.DataFrame(latest_predictions)

            df['fecha_dt'] = pd.to_datetime(df['fecha'], format='%Y-%m-%d', errors='coerce')
            df = df.dropna(subset=['fecha_dt'])

            if df.empty:
                return {
                    "labels": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
                    "data": [0]*12,
                    "counts": [0]*12
                }

            df["month"] = df["fecha_dt"].dt.month
            df["en_riesgo"] = (df["riesgo_desercion"] == "Alto").astype(int)

            monthly_stats = df.groupby("month").agg({
                'en_riesgo': ['sum', 'count', 'mean']
            }).reindex(range(1, 13), fill_value=0)

            counts = monthly_stats[('en_riesgo', 'sum')].tolist()
            totals = monthly_stats[('en_riesgo', 'count')].tolist()
            percentages = [
                round((counts[i] / totals[i] * 100) if totals[i] > 0 else 0, 1)
                for i in range(12)
            ]

            labels = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

            return {
                "labels": labels,
                "data": percentages,
                "counts": counts,
                "totals": totals
            }

        except Exception as e:
            print(f"Error calculando resumen de riesgo: {e}")
            return {
                "labels": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
                "data": [0]*12,
                "counts": [0]*12,
                "totals": [0]*12
            }

def update_latest_predictions(predictions):
    """Actualiza la variable global con los últimos resultados de predicción"""
    global latest_predictions

    print(f"DEBUG: update_latest_predictions llamado con {len(predictions)} predicciones")
    if len(predictions) > 0:
        print(f"DEBUG: Primera prediccion: {predictions[0]}")
        primera = predictions[0]
        print(f"DEBUG: Nota en primera prediccion: {primera.get('nota_final', 'NO ENCONTRADA')}")
        print(f"DEBUG: Asistencia en primera prediccion: {primera.get('asistencia', 'NO ENCONTRADA')}")

    latest_predictions = predictions
    print(f"DEBUG: Variable global actualizada. Ahora tiene {len(latest_predictions)} elementos")
