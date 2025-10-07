# src/api/routes/dashboard_attendance.py

from fastapi import APIRouter, Depends
from services.attendance_service import AttendanceService
from pydantic import BaseModel
from typing import List

router = APIRouter()

class AttendanceData(BaseModel):
    student_id: int
    attendance: list  # Lista de asistencia
    dates: list  # Lista de fechas correspondientes a la asistencia

class AttendanceSummaryResponse(BaseModel):
    labels: List[str]
    data: List[float]

def get_attendance_service():
    return AttendanceService()

@router.post("/attendance_trend")
async def get_attendance_trend(data: AttendanceData, attendance_service: AttendanceService = Depends(get_attendance_service)):
    # Usar la nueva función de mapa de calor
    plot_base64 = attendance_service.generate_attendance_heatmap()
    return {"plot_url": f"data:image/png;base64,{plot_base64}"}

@router.get("/attendance_heatmap")
async def get_attendance_heatmap(attendance_service: AttendanceService = Depends(get_attendance_service)):
    """
    Endpoint para obtener el mapa de calor de asistencia basado en datos del CSV
    """
    plot_base64 = attendance_service.generate_attendance_heatmap()
    return {"plot_url": f"data:image/png;base64,{plot_base64}"}

@router.get("/attendance_summary", response_model=AttendanceSummaryResponse)
async def get_attendance_summary():
    """
    Endpoint para devolver datos de asistencia por día de la semana
    """
    attendance_service = AttendanceService()
    return attendance_service.get_weekly_attendance_summary()

@router.get("/attendance_heatmap_chart")
async def get_attendance_heatmap_chart():
    """
    Endpoint para obtener datos estructurados del mapa de calor para el gráfico del frontend
    """
    attendance_service = AttendanceService()

    # Intentar obtener datos del CSV
    df = attendance_service.get_attendance_data_from_csv()

    if df is None or df.empty:
        # Si no hay datos del CSV, devolver estructura con datasets vacíos
        return {
            "labels": ["Lun", "Mar", "Mié", "Jue", "Vie"],
            "datasets": [
                {
                    "label": "Sin datos del CSV",
                    "data": [0, 0, 0, 0, 0],
                    "backgroundColor": "#ff4444",
                }
            ]
        }

    # Procesar datos del CSV para el mapa de calor
    dias_semana = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    etiquetas_dias = ["Lun", "Mar", "Mié", "Jue", "Vie"]

    # Agrupar por mes
    meses_unicos = sorted(df['año_mes'].unique()) if 'año_mes' in df.columns else []

    if not meses_unicos:
        return {
            "labels": etiquetas_dias,
            "datasets": [
                {
                    "label": "Sin datos válidos",
                    "data": [0, 0, 0, 0, 0],
                    "backgroundColor": "#ff4444",
                }
            ]
        }

    # Crear datasets para cada mes
    datasets = []
    colors = ["#4CAF50", "#2196F3", "#FF9800", "#9C27B0", "#F44336", "#00BCD4", "#8BC34A", "#FFC107", "#E91E63", "#3F51B5", "#009688", "#795548"]

    for index, mes in enumerate(meses_unicos):
        fila_datos = []

        # Convertir mes a etiqueta legible
        try:
            from datetime import datetime
            fecha_mes = datetime.strptime(mes, '%Y-%m')
            etiqueta_mes = fecha_mes.strftime('%b %Y')
        except:
            etiqueta_mes = mes

        for dia in dias_semana:
            # Filtrar datos por mes y día
            datos_filtrados = df[(df['año_mes'] == mes) & (df['dia_semana'] == dia)]

            if not datos_filtrados.empty:
                asistencia_promedio = datos_filtrados['asistencia'].mean()
            else:
                asistencia_promedio = 0

            fila_datos.append(round(asistencia_promedio, 1))

        # Crear dataset para este mes
        color = colors[index % len(colors)]
        datasets.append({
            "label": etiqueta_mes,
            "data": fila_datos,
            "backgroundColor": color,
            "borderColor": color,
            "borderWidth": 1
        })

    return {
        "labels": etiquetas_dias,
        "datasets": datasets
    }

@router.get("/attendance_chart_real")
async def get_attendance_chart_real():
    """
    Endpoint NUEVO que garantiza usar datos reales del CSV
    """
    # Obtener instancia del servicio
    attendance_service = AttendanceService()

    # Obtener datos del CSV
    df = attendance_service.get_attendance_data_from_csv()

    if df is None or df.empty:
        print("⚠️ No hay datos del CSV disponibles")
        return {
            "labels": ["Lun", "Mar", "Mié", "Jue", "Vie"],
            "datasets": [{
                "label": "Sin datos del CSV",
                "data": [0, 0, 0, 0, 0],
                "backgroundColor": "#cccccc"
            }]
        }

    print(f"✅ Datos del CSV encontrados: {len(df)} registros")
    print(f"📅 Fechas disponibles: {df['fecha'].unique()[:5]}...")
    print(f"🗓️ Días de semana encontrados: {df['dia_semana'].unique()}")

    # Obtener días de semana únicos que realmente están en el CSV
    dias_encontrados = df['dia_semana'].unique()

    # Mapear días a etiquetas en español
    day_mapping = {
        'Monday': 'Lun', 'Tuesday': 'Mar', 'Wednesday': 'Mié',
        'Thursday': 'Jue', 'Friday': 'Vie', 'Saturday': 'Sáb', 'Sunday': 'Dom'
    }

    # Si solo hay domingos, cambiar la estrategia del gráfico
    if len(dias_encontrados) == 1 and 'Sunday' in dias_encontrados:
        print("📊 Detectado: Solo domingos en el CSV. Cambiando a vista por fechas...")

        # Agrupar por fechas específicas en lugar de días de semana
        meses_unicos = sorted(df['año_mes'].unique())

        # Obtener fechas únicas para usar como etiquetas
        fechas_unicas = sorted(df['fecha_dt'].dt.strftime('%d/%m').unique())[:10]  # Máximo 10 fechas

        datasets = []
        colors = ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40", "#4CAF50", "#FF9F9F"]

        for idx, mes in enumerate(meses_unicos):
            datos_mes = []

            for fecha_str in fechas_unicas:
                # Filtrar datos por mes y fecha específica
                datos_filtrados = df[
                    (df['año_mes'] == mes) &
                    (df['fecha_dt'].dt.strftime('%d/%m') == fecha_str)
                ]

                if not datos_filtrados.empty:
                    asistencia_promedio = round(datos_filtrados['asistencia'].mean(), 1)
                else:
                    asistencia_promedio = 0

                datos_mes.append(asistencia_promedio)

            # Crear etiqueta del mes
            from datetime import datetime
            etiqueta_mes = datetime.strptime(mes, '%Y-%m').strftime('%b %Y')

            datasets.append({
                "label": etiqueta_mes,
                "data": datos_mes,
                "backgroundColor": colors[idx % len(colors)],
                "borderColor": colors[idx % len(colors)],
                "borderWidth": 2
            })

            print(f"✅ Dataset creado para {etiqueta_mes}: {datos_mes}")

        return {
            "labels": fechas_unicas,  # Fechas como etiquetas
            "datasets": datasets
        }

    else:
        # Estrategia original para días laborables
        dias_semana = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        etiquetas_dias = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        meses_unicos = sorted(df['año_mes'].unique())

        print(f"📊 Meses encontrados: {meses_unicos}")

        colors = ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40", "#4CAF50", "#FF9F9F"]
        datasets = []

        for idx, mes in enumerate(meses_unicos):
            print(f"🔄 Procesando mes: {mes}")
            datos_mes = []

            for i, dia in enumerate(dias_semana):
                datos_filtrados = df[(df['año_mes'] == mes) & (df['dia_semana'] == dia)]

                if not datos_filtrados.empty:
                    asistencia_promedio = round(datos_filtrados['asistencia'].mean(), 1)
                    print(f"  📈 {dia} ({etiquetas_dias[i]}): {asistencia_promedio}% asistencia ({len(datos_filtrados)} registros)")
                else:
                    asistencia_promedio = 0

                # Incluir todos los días, no solo lunes a viernes
                datos_mes.append(asistencia_promedio)

            from datetime import datetime
            etiqueta_mes = datetime.strptime(mes, '%Y-%m').strftime('%b %Y')

            datasets.append({
                "label": etiqueta_mes,
                "data": datos_mes,
                "backgroundColor": colors[idx % len(colors)],
                "borderColor": colors[idx % len(colors)],
                "borderWidth": 2
            })

            print(f"✅ Dataset creado para {etiqueta_mes}: {datos_mes}")

        return {
            "labels": etiquetas_dias,  # Todos los días de la semana
            "datasets": datasets
        }
