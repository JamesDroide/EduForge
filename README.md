# EduForge - Sistema de Prediccion de Desercion Estudiantil

![EduForge Logo](https://img.shields.io/badge/EduForge-v2.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.9+-green.svg)
![React](https://img.shields.io/badge/React-18.0+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-red.svg)
![Machine Learning](https://img.shields.io/badge/ML-scikit--learn-orange.svg)

## Descripcion

**EduForge** es un sistema inteligente de prediccion de desercion estudiantil que utiliza algoritmos de Machine Learning para identificar estudiantes en riesgo academico. Desarrollado como proyecto de tesis, combina analisis predictivo con una interfaz intuitiva para instituciones educativas.

## Caracteristicas Principales

- **Prediccion Inteligente**: Modelo RandomForest entrenado para predecir desercion
- **Dashboard Interactivo**: Visualizacion de datos y metricas en tiempo real
- **Analisis Individual**: Evaluacion personalizada por estudiante
- **Reportes Completos**: Tablas detalladas con todos los resultados
- **Rendimiento Optimizado**: Sistema de cache para navegacion fluida
- **Interfaz Moderna**: Diseno responsive con Material-UI

## Arquitectura del Sistema

### Backend (FastAPI + Python)
- **API RESTful** con FastAPI
- **Modelo ML** con scikit-learn (RandomForest)
- **Servicios especializados** para cada funcionalidad
- **Base de datos** PostgreSQL / SQLite para persistencia

### Frontend (React + Material-UI)
- **Aplicacion SPA** con React 18
- **Componentes Material-UI** para UI profesional
- **Sistema de cache** para optimizacion de rendimiento
- **Navegacion fluida** entre modulos

### Machine Learning
- **Algoritmo**: RandomForest Classifier
- **Caracteristicas**: Notas, asistencia, conducta, inasistencia
- **Salida**: Riesgo de desercion (Alto, Medio, Bajo)
- **Precision**: Optimizado para datos educativos reales

## Instalacion y Configuracion

### Prerrequisitos
- Python 3.9+
- Node.js 16+
- Git

### Backend Setup
```bash
git clone https://github.com/JamesDroide/EduForge.git
cd EduForge/backend

pip install -r requirements.txt

cd src
uvicorn main:app --reload --port 8000
```

### Frontend Setup
```bash
cd EduForge/frontend
npm install

npm start
```

## Uso del Sistema

### 1. Cargar Datos
- Sube archivos CSV con informacion estudiantil
- Formato requerido: `id_estudiante`, `nombre`, `nota_final`, `asistencia`, `inasistencia`, `conducta`

### 2. Visualizar Resultados
- **Reporte General**: Dashboard con metricas globales
- **Analisis Individual**: Evaluacion detallada por estudiante
- **Resultados Completos**: Tabla con todos los datos procesados

### 3. Interpretar Predicciones
- **Alto Riesgo**: Requiere intervencion inmediata
- **Medio Riesgo**: Seguimiento recomendado
- **Bajo Riesgo**: Estudiante en condicion favorable

## Tecnologias Utilizadas

### Backend
- **FastAPI** - Framework web moderno y rapido
- **scikit-learn** - Machine Learning y analisis predictivo
- **pandas** - Manipulacion y analisis de datos
- **SQLAlchemy** - ORM para base de datos
- **uvicorn** - Servidor ASGI de alta performance

### Frontend
- **React** - Biblioteca para interfaces de usuario
- **Material-UI** - Componentes de diseno profesional
- **React Router** - Navegacion entre paginas
- **Axios** - Cliente HTTP para API calls

### Machine Learning
- **RandomForest** - Algoritmo de clasificacion
- **StandardScaler** - Normalizacion de caracteristicas
- **Joblib** - Serializacion de modelos entrenados

## Estructura del Proyecto

```
EduForge/
├── backend/                     # Backend (FastAPI + Machine Learning)
│   ├── src/                     # Codigo fuente de la API
│   │   ├── main.py              # Punto de entrada de la API
│   │   ├── config.py            # Configuracion de base de datos
│   │   ├── models/              # Modelos ORM y predictor ML
│   │   ├── services/            # Logica de negocio
│   │   ├── schemas/             # Esquemas Pydantic
│   │   ├── migrations/          # Migraciones y seeds de BD
│   │   ├── utils/               # Seguridad (JWT/bcrypt) y dependencias
│   │   └── api/routes/          # Endpoints de la API
│   ├── scripts/                 # Scripts de entrenamiento y mantenimiento
│   │   ├── check_db.py          # Diagnostico de base de datos
│   │   └── models/              # Entrenamiento y artefactos (.pkl)
│   ├── data/                    # Datasets CSV de entrenamiento y validacion
│   ├── notebooks/               # Jupyter notebooks de exploracion y evaluacion
│   ├── tests/                   # Pruebas automatizadas del backend
│   ├── .env.example             # Plantilla de variables de entorno (Backend)
│   ├── .gitignore               # Reglas Git para Python/FastAPI
│   ├── requirements.txt         # Dependencias de Python
│   └── railway.toml             # Configuracion de despliegue en Railway
├── frontend/                    # Frontend (React + Material-UI)
│   ├── public/                  # Recursos estaticos
│   ├── src/
│   │   ├── layouts/             # Modulos y vistas principales
│   │   ├── components/          # Componentes reutilizables
│   │   ├── config/              # Configuracion de cliente Axios (api.js)
│   │   └── utils/               # Utilidades y sistema de cache
│   ├── .env.example             # Plantilla de variables de entorno (Frontend)
│   ├── .gitignore               # Reglas Git para Node/React
│   ├── package.json             # Dependencias de Node.js
│   └── vercel.json              # Configuracion de despliegue en Vercel
└── README.md                    # Documentacion general
```

## Funcionalidades Clave

### Prediccion de Desercion
- Analisis de patrones estudiantiles
- Identificacion temprana de riesgos
- Recomendaciones personalizadas

### Dashboard Analitico
- Metricas en tiempo real
- Graficos interactivos
- Filtros por nivel de riesgo

### Gestion de Datos
- Carga masiva de CSV
- Validacion automatica de datos
- Procesamiento en tiempo real

## Futuras Mejoras

- [ ] Integracion con sistemas academicos existentes
- [ ] Algoritmos ML adicionales (XGBoost, Neural Networks)
- [ ] Modulo de recomendaciones personalizadas
- [ ] API para integracion externa
- [ ] Dashboard para administradores
- [ ] Notificaciones automaticas

## Autor

**James Droide**
- GitHub: [@JamesDroide](https://github.com/JamesDroide)
- Proyecto de Tesis - UPAO 2025

## Licencia

Este proyecto esta bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para mas detalles.

## Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## Soporte

Si tienes alguna pregunta o problema, por favor abre un [issue](https://github.com/JamesDroide/EduForge/issues) en GitHub.
