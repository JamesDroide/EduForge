# EduForge 🎓

Sistema inteligente de predicción de deserción estudiantil usando Machine Learning. Desarrollado con FastAPI + React + scikit-learn para análisis predictivo educativo.

## 🚀 Características

- **Backend FastAPI**: API REST robusta para predicciones de ML
- **Frontend React**: Dashboard interactivo con visualizaciones en tiempo real
- **Machine Learning**: Modelo Random Forest para predicción de riesgo de deserción
- **Análisis Predictivo**: Probabilidad de deserción con múltiples factores
- **Dashboard Interactivo**: Visualización de estadísticas y distribución de riesgo
- **Análisis Individual**: Evaluación detallada de estudiantes con recomendaciones personalizadas

## 📊 Funcionalidades

### Dashboard
- Estadísticas generales de estudiantes
- Distribución de niveles de riesgo (Bajo, Medio, Alto)
- Gráficos interactivos con Recharts
- Tabla de estudiantes con indicadores clave

### Análisis Individual
- Formulario completo de datos del estudiante
- Predicción de probabilidad de deserción
- Análisis de factores (académicos, asistencia, hábitos de estudio, socioeconómicos)
- Visualización radar del perfil del estudiante
- Recomendaciones personalizadas

## 🛠️ Tecnologías

### Backend
- **FastAPI**: Framework web moderno y rápido
- **scikit-learn**: Modelo de Machine Learning
- **pandas**: Procesamiento de datos
- **joblib**: Serialización del modelo
- **Pydantic**: Validación de datos

### Frontend
- **React**: Biblioteca de UI
- **Vite**: Build tool rápido
- **Recharts**: Gráficos interactivos
- **Axios**: Cliente HTTP

## 📦 Instalación

### Requisitos Previos
- Python 3.8+
- Node.js 16+
- npm o yarn

### Backend

```bash
# Instalar dependencias
pip install -r requirements.txt

# Entrenar el modelo de ML
cd backend
python train_model.py

# Iniciar servidor FastAPI
cd backend/app
python main.py
```

El backend estará disponible en `http://localhost:8000`

### Frontend

```bash
# Navegar al directorio frontend
cd frontend

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev
```

El frontend estará disponible en `http://localhost:5173`

## 🔬 Modelo de Machine Learning

El sistema utiliza un modelo **Random Forest Classifier** entrenado con datos sintéticos que incluyen:

### Características de entrada:
- Tasa de asistencia (%)
- Promedio de calificaciones (0-10)
- Horas de estudio por semana
- Ingreso familiar
- Nivel educativo de padres (1-5)
- Actividades extracurriculares
- Materias reprobadas
- Edad

### Salida:
- Probabilidad de deserción (0-100%)
- Nivel de riesgo (Bajo, Medio, Alto)
- Recomendaciones personalizadas

## 📡 API Endpoints

### `GET /`
Información general de la API

### `POST /predict`
Predicción de deserción para un estudiante
```json
{
  "attendance_rate": 85,
  "average_grade": 7.5,
  "study_hours_per_week": 15,
  "family_income": 2500,
  "parent_education_level": 3,
  "extracurricular_activities": 2,
  "failed_subjects": 0,
  "age": 18
}
```

### `POST /analyze?student_id={id}`
Análisis detallado de un estudiante

### `GET /health`
Health check de la API

## 📈 Visualizaciones

- **Gráfico de Pastel**: Distribución de riesgo de deserción
- **Gráfico de Barras**: Comparación de promedio vs asistencia
- **Gráfico Radar**: Perfil multidimensional del estudiante
- **Tabla Interactiva**: Lista completa de estudiantes con indicadores

## 🎯 Casos de Uso

1. **Instituciones Educativas**: Identificación temprana de estudiantes en riesgo
2. **Orientadores Académicos**: Generación de estrategias de intervención personalizadas
3. **Administradores**: Dashboard para toma de decisiones basada en datos
4. **Investigadores**: Análisis de factores que influyen en la deserción estudiantil

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👨‍💻 Autor

**JamesDroide**

---

⭐ Si este proyecto te resultó útil, considera darle una estrella en GitHub!
