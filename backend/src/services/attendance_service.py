import matplotlib.pyplot as plt
from io import BytesIO
import base64
import pandas as pd
from datetime import datetime
from config import SessionLocal
from models import ResultadoPrediccion

latest_csv_data = None

def clear_latest_csv_data():
    """Limpia la variable global de datos del CSV"""
    global latest_csv_data
    latest_csv_data = None
    print("Variable global latest_csv_data limpiada")

class AttendanceService:

    def get_attendance_data_from_csv(self):
        """
        Función para obtener datos de asistencia desde los datos globales del CSV
        """
        global latest_csv_data

        # Evitar leer de la base de datos si no se ha subido un CSV en la sesión actual
        if not latest_csv_data or len(latest_csv_data) == 0:
            print("No hay datos de asistencia cargados en esta sesion")
            return None

        df = pd.DataFrame(latest_csv_data)

        if 'fecha' not in df.columns or 'asistencia' not in df.columns:
            return None

        df['fecha_dt'] = pd.to_datetime(df['fecha'], format='%Y-%m-%d', errors='coerce')
        df = df.dropna(subset=['fecha_dt'])

        if df.empty:
            return None

        df['dia_semana'] = df['fecha_dt'].dt.day_name()
        df['mes'] = df['fecha_dt'].dt.strftime('%b')
        df['año_mes'] = df['fecha_dt'].dt.strftime('%Y-%m')

        return df

    def get_weekly_attendance_summary(self):
        """
        Devuelve la suma de asistencia por día de la semana para todos los estudiantes.
        Retorna un diccionario con labels y data para el gráfico del dashboard.
        """
        global latest_csv_data

        if not latest_csv_data or len(latest_csv_data) == 0:
            print("No hay datos de asistencia cargados en esta sesion")
            return {"labels": ["L", "M", "M", "J", "V", "S", "D"], "data": [0, 0, 0, 0, 0, 0, 0]}

        db = SessionLocal()
        try:
            results = db.query(ResultadoPrediccion).all()

            if not results:
                return {"labels": ["L", "M", "M", "J", "V", "S", "D"], "data": [0, 0, 0, 0, 0, 0, 0]}

            df = pd.DataFrame([
                {"fecha": r.fecha, "asistencia": r.asistencia}
                for r in results if r.fecha is not None
            ])

            if df.empty:
                return {"labels": ["L", "M", "M", "J", "V", "S", "D"], "data": [0, 0, 0, 0, 0, 0, 0]}

            df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
            df = df.dropna(subset=["fecha"])
            df["day_of_week"] = df["fecha"].dt.dayofweek

            summary = df.groupby("day_of_week")["asistencia"].sum().reindex(range(7), fill_value=0)

            labels = ["L", "M", "M", "J", "V", "S", "D"]
            return {"labels": labels, "data": summary.tolist()}
        finally:
            db.close()

    def generate_attendance_heatmap(self):
        """
        Genera un mapa de calor de asistencia por día de la semana (X) y mes (Y)
        """
        df = self.get_attendance_data_from_csv()

        if df is None or df.empty:
            return self._generate_empty_plot()

        dias_semana = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        meses_unicos = sorted(df['año_mes'].unique())

        matriz_asistencia = []

        for mes in meses_unicos:
            fila = []
            for dia in dias_semana:
                datos_filtrados = df[(df['año_mes'] == mes) & (df['dia_semana'] == dia)]

                if not datos_filtrados.empty:
                    asistencia_promedio = datos_filtrados['asistencia'].mean()
                else:
                    asistencia_promedio = 0

                fila.append(asistencia_promedio)
            matriz_asistencia.append(fila)

        plt.figure(figsize=(10, 8))

        etiquetas_dias = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie']
        etiquetas_meses = [datetime.strptime(mes, '%Y-%m').strftime('%b %Y') for mes in meses_unicos]

        im = plt.imshow(matriz_asistencia, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)

        plt.xticks(range(len(etiquetas_dias)), etiquetas_dias)
        plt.yticks(range(len(etiquetas_meses)), etiquetas_meses)

        for i in range(len(etiquetas_meses)):
            for j in range(len(etiquetas_dias)):
                valor = matriz_asistencia[i][j]
                color = 'white' if valor < 50 else 'black'
                plt.text(j, i, f'{valor:.0f}%', ha='center', va='center',
                        color=color, fontweight='bold', fontsize=10)

        plt.title('Reporte Por Asistencia\nGráfico por días de la semana', fontsize=14, fontweight='bold')
        plt.xlabel('Días de la Semana', fontsize=12)
        plt.ylabel('Meses', fontsize=12)

        cbar = plt.colorbar(im, fraction=0.046, pad=0.04)
        cbar.set_label('Porcentaje de Asistencia (%)', rotation=270, labelpad=20)

        plt.tight_layout()

        return self._plot_to_base64()

    def _generate_empty_plot(self):
        """
        Genera un gráfico vacío cuando no hay datos
        """
        plt.figure(figsize=(10, 8))

        dias = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie']
        meses = ['Feb 2025', 'Mar 2025', 'Abr 2025']

        matriz_vacia = [[0 for _ in dias] for _ in meses]

        plt.imshow(matriz_vacia, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)
        plt.xticks(range(len(dias)), dias)
        plt.yticks(range(len(meses)), meses)

        plt.title('Reporte Por Asistencia\nNo hay datos disponibles', fontsize=14, fontweight='bold')
        plt.xlabel('Días de la Semana', fontsize=12)
        plt.ylabel('Meses', fontsize=12)

        plt.text(len(dias)/2-0.5, len(meses)/2-0.5, 'Sube un archivo CSV\npara ver los datos',
                ha='center', va='center', fontsize=12,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

        plt.tight_layout()
        return self._plot_to_base64()

    def _plot_to_base64(self):
        """
        Convierte el plot actual a base64
        """
        img_io = BytesIO()
        plt.savefig(img_io, format='png', dpi=300, bbox_inches='tight')
        img_io.seek(0)

        img_base64 = base64.b64encode(img_io.read()).decode('utf-8')
        plt.close()

        return img_base64

    def get_attendance_from_db(self, student_id: int):
        """
        Función para obtener la asistencia e inasistencia de la base de datos
        """
        db = SessionLocal()
        try:
            student_data = db.query(ResultadoPrediccion).filter(ResultadoPrediccion.id_estudiante == student_id).all()

            if not student_data:
                return [], []

            attendance = [data.asistencia for data in student_data]
            dates = [data.fecha.strftime("%b %Y") if data.fecha else "2025" for data in student_data]
            return attendance, dates
        finally:
            db.close()

    def generate_attendance_plot(self, student_id: int):
        return self.generate_attendance_heatmap()

def update_attendance_data(csv_data):
    """Actualiza los datos globales del CSV para el servicio de asistencia"""
    global latest_csv_data
    latest_csv_data = csv_data
