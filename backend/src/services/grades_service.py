import matplotlib.pyplot as plt
from io import BytesIO
import base64
from src.config import SessionLocal
from src.models import StudentData


class GradesService:

    def get_grades_from_db(self, student_id: int):
        """
        Función para obtener las calificaciones, asistencia y conducta de la base de datos
        """
        db = SessionLocal()
        try:
            student_data = db.query(StudentData).filter(StudentData.id_estudiante == student_id).all()
            grades = [data.nota_final for data in student_data]
            attendance = [data.asistencia for data in student_data]
            behavior = [data.conducta for data in student_data]
            months = [data.created_at.strftime("%b %Y") for data in student_data]
            return grades, attendance, behavior, months
        finally:
            db.close()

    def generate_grades_plot(self, student_id: int):
        """
        Función para generar el gráfico de calificaciones acumuladas, asistencia y conducta
        """
        grades, attendance, behavior, months = self.get_grades_from_db(student_id)

        approved = [grade for grade in grades if grade >= 11]
        failed = [grade for grade in grades if grade < 11]

        approved_months = [months[i] for i in range(len(grades)) if grades[i] >= 11]
        failed_months = [months[i] for i in range(len(grades)) if grades[i] < 11]

        plt.figure(figsize=(10, 6))

        plt.plot(approved_months, approved, label="Aprobados", color="green", marker="o")
        plt.plot(failed_months, failed, label="Desaprobados", color="red", marker="o")
        plt.plot(months, attendance, label="Asistencia (%)", color="blue", linestyle="--")

        conduct_positive = [1 if cond == 'Buena' else 0 for cond in behavior]
        conduct_negative = [1 if cond == 'Mala' else 0 for cond in behavior]
        plt.scatter(months, conduct_positive, color="yellow", label="Buena Conducta", marker="x")
        plt.scatter(months, conduct_negative, color="orange", label="Mala Conducta", marker="x")

        plt.title("Evolución de Calificaciones Acumuladas, Asistencia y Conducta")
        plt.xlabel("Meses")
        plt.ylabel("Valor")
        plt.legend()

        img_io = BytesIO()
        plt.savefig(img_io, format='png')
        img_io.seek(0)
        img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
        plt.close()

        return f"data:image/png;base64,{img_base64}"
