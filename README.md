# 🎓 EduForge - Sistema de Predicción de Deserción Estudiantil

![EduForge Logo](https://img.shields.io/badge/EduForge-v2.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.9+-green.svg)
![React](https://img.shields.io/badge/React-18.0+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-red.svg)
![Machine Learning](https://img.shields.io/badge/ML-scikit--learn-orange.svg)

## 📋 Descripción

**EduForge** es un sistema inteligente de predicción de deserción estudiantil que utiliza algoritmos de Machine Learning para identificar estudiantes en riesgo académico. Desarrollado como proyecto de tesis, combina análisis predictivo con una interfaz intuitiva para instituciones educativas.

## ✨ Características Principales

- 🤖 **Predicción Inteligente**: Modelo RandomForest entrenado para predecir deserción
- 📊 **Dashboard Interactivo**: Visualización de datos y métricas en tiempo real
- 👤 **Análisis Individual**: Evaluación personalizada por estudiante
- 📈 **Reportes Completos**: Tablas detalladas con todos los resultados
- ⚡ **Rendimiento Optimizado**: Sistema de cache para navegación fluida
- 📱 **Interfaz Moderna**: Diseño responsive con Material-UI

## 🏗️ Arquitectura del Sistema

### Backend (FastAPI + Python)
- **API RESTful** con FastAPI
- **Modelo ML** con scikit-learn (RandomForest)
- **Servicios especializados** para cada funcionalidad
- **Base de datos** SQLite para persistencia

### Frontend (React + Material-UI)
- **Aplicación SPA** con React 18
- **Componentes Material-UI** para UI profesional
- **Sistema de cache** para optimización de rendimiento
- **Navegación fluida** entre módulos

### Machine Learning
- **Algoritmo**: RandomForest Classifier
- **Características**: Notas, asistencia, conducta, inasistencia
- **Salida**: Riesgo de deserción (Alto, Medio, Bajo)
- **Precisión**: Optimizado para datos educativos reales

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.9+
- Node.js 16+
- Git

### Backend Setup
```bash
# Clonar repositorio
git clone https://github.com/JamesDroide/EduForge.git
cd EduForge/backend

# Instalar dependencias Python
pip install -r requirements.txt

# Ejecutar servidor
cd src
uvicorn main:app --reload --port 8000
```

### Frontend Setup
```bash
# Instalar dependencias Node.js
cd EduForge/frontend
npm install

# Ejecutar aplicación
npm start
```

## 📊 Uso del Sistema

### 1. Cargar Datos
- Sube archivos CSV con información estudiantil
- Formato requerido: `id_estudiante`, `nombre`, `nota_final`, `asistencia`, `inasistencia`, `conducta`

### 2. Visualizar Resultados
- **Reporte General**: Dashboard con métricas globales
- **Análisis Individual**: Evaluación detallada por estudiante
- **Resultados Completos**: Tabla con todos los datos procesados

### 3. Interpretar Predicciones
- 🔴 **Alto Riesgo**: Requiere intervención inmediata
- 🟡 **Medio Riesgo**: Seguimiento recomendado
- 🟢 **Bajo Riesgo**: Estudiante en condición favorable

## 🛠️ Tecnologías Utilizadas

### Backend
- **FastAPI** - Framework web moderno y rápido
- **scikit-learn** - Machine Learning y análisis predictivo
- **pandas** - Manipulación y análisis de datos
- **SQLAlchemy** - ORM para base de datos
- **uvicorn** - Servidor ASGI de alta performance

### Frontend
- **React** - Biblioteca para interfaces de usuario
- **Material-UI** - Componentes de diseño profesional
- **React Router** - Navegación entre páginas
- **Axios** - Cliente HTTP para API calls

### Machine Learning
- **RandomForest** - Algoritmo de clasificación
- **StandardScaler** - Normalización de características
- **Joblib** - Serialización de modelos entrenados

## 📁 Estructura del Proyecto

```
EduForge/
├── backend/                     # Backend (FastAPI + Machine Learning)
│   ├── src/                     # Código fuente de la API
│   │   ├── main.py              # Punto de entrada de la API
│   │   ├── config.py            # Configuración de base de datos
│   │   ├── models/              # Modelos ORM y predictor ML
│   │   ├── services/            # Lógica de negocio
│   │   ├── schemas/             # Esquemas Pydantic
│   │   ├── migrations/          # Migraciones y seeds de BD
│   │   ├── utils/               # Seguridad (JWT/bcrypt) y dependencias
│   │   └── api/routes/          # Endpoints de la API
│   ├── scripts/                 # Scripts de entrenamiento y mantenimiento
│   │   ├── check_db.py          # Diagnóstico de base de datos
│   │   └── models/              # Entrenamiento y artefactos (.pkl)
│   ├── data/                    # Datasets CSV de entrenamiento y validación
│   ├── notebooks/               # Jupyter notebooks de exploración y evaluación
│   ├── tests/                   # Pruebas automatizadas del backend
│   ├── .env.example             # Plantilla de variables de entorno (Backend)
│   ├── .gitignore               # Reglas Git para Python/FastAPI
│   ├── requirements.txt         # Dependencias de Python
│   └── railway.toml             # Configuración de despliegue en Railway
├── frontend/                    # Frontend (React + Material-UI)
│   ├── public/                  # Recursos estáticos
│   ├── src/
│   │   ├── layouts/             # Módulos y vistas principales
│   │   ├── components/          # Componentes reutilizables
│   │   ├── config/              # Configuración de cliente Axios (api.js)
│   │   └── utils/               # Utilidades y sistema de caché
│   ├── .env.example             # Plantilla de variables de entorno (Frontend)
│   ├── .gitignore               # Reglas Git para Node/React
│   ├── package.json             # Dependencias de Node.js
│   └── vercel.json              # Configuración de despliegue en Vercel
└── README.md                    # Documentación general
```

## 🎯 Funcionalidades Clave

### Predicción de Deserción
- Análisis de patrones estudiantiles
- Identificación temprana de riesgos
- Recomendaciones personalizadas

### Dashboard Analítico
- Métricas en tiempo real
- Gráficos interactivos
- Filtros por nivel de riesgo

### Gestión de Datos
- Carga masiva de CSV
- Validación automática de datos
- Procesamiento en tiempo real

## 🔮 Futuras Mejoras

- [ ] Integración con sistemas académicos existentes
- [ ] Algoritmos ML adicionales (XGBoost, Neural Networks)
- [ ] Módulo de recomendaciones personalizadas
- [ ] API para integración externa
- [ ] Dashboard para administradores
- [ ] Notificaciones automáticas

## 👨‍💻 Autor

**James Droide**
- GitHub: [@JamesDroide](https://github.com/JamesDroide)
- Proyecto de Tesis - UPAO 2025

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📞 Soporte

Si tienes alguna pregunta o problema, por favor abre un [issue](https://github.com/JamesDroide/EduForge/issues) en GitHub.

---

⭐ **¡Dale una estrella al proyecto si te parece útil!** ⭐
