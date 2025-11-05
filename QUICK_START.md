# 🚀 GUÍA DE INICIO RÁPIDO - EduForge

Esta guía te ayudará a tener EduForge funcionando en menos de 10 minutos.

## ⚡ Instalación Rápida

### 1️⃣ Prerrequisitos

Asegúrate de tener instalado:
- ✅ Python 3.12+
- ✅ Node.js 16+
- ✅ PostgreSQL 18+
- ✅ Git

### 2️⃣ Clonar el Proyecto

```bash
git clone https://github.com/JamesDroide/EduForge.git
cd EduForge
```

### 3️⃣ Configurar Base de Datos

```bash
# Crear base de datos en PostgreSQL
createdb eduforge

# O usando psql:
psql -U postgres
CREATE DATABASE eduforge;
\q
```

### 4️⃣ Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus configuraciones:
# DATABASE_URL=postgresql://postgres:tu_password@localhost:5432/eduforge
# SECRET_KEY=tu-clave-secreta
```

### 5️⃣ Iniciar Backend

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Iniciar servidor (desde la carpeta src)
cd src
uvicorn main:app --reload
```

✅ Backend corriendo en: http://localhost:8000

📚 Documentación API: http://localhost:8000/docs

### 6️⃣ Iniciar Frontend

```bash
# En una nueva terminal
cd frontend

# Instalar dependencias
npm install

# Iniciar aplicación
npm start
```

✅ Frontend corriendo en: http://localhost:3000

## 🎯 Primeros Pasos

### 1. Acceder al Sistema

- Abre tu navegador en: http://localhost:3000
- Usa las credenciales por defecto:
  - **Usuario:** admin
  - **Password:** admin123

### 2. Cargar Datos de Prueba

1. Ve a **"Cargar CSV"** en el menú
2. Usa el archivo de ejemplo: `data/student_data.csv`
3. Haz clic en **"Cargar y Predecir"**

### 3. Ver Resultados

- **Dashboard**: Métricas y gráficos generales
- **Resultados Completos**: Tabla detallada con todos los estudiantes
- **Análisis Individual**: Buscar por estudiante específico
- **Historial**: Ver todas las cargas anteriores

## 🔍 Verificar Instalación

### Backend
```bash
# Verificar que el servidor está funcionando
curl http://localhost:8000/health

# Debería retornar:
# {"status":"healthy","version":"2.0.0","architecture":"Clean Architecture"}
```

### Frontend
- Abre http://localhost:3000
- Deberías ver la página de login

## 🐛 Solución de Problemas Comunes

### Error de conexión a PostgreSQL
```bash
# Verificar que PostgreSQL está corriendo
# Windows:
pg_ctl status

# Linux/Mac:
sudo service postgresql status
```

### Puerto 8000 en uso
```bash
# Usar otro puerto
uvicorn main:app --reload --port 8001
```

### Módulos Python faltantes
```bash
pip install -r requirements.txt --upgrade
```

### Error en frontend
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## 📊 Estructura del CSV

Tu archivo CSV debe tener estas columnas:

```csv
estudiante_id,nombre,fecha,nota_final,asistencia,inasistencia,conducta
1,Juan Pérez,2024-01-15,14.5,85,5,Buena
2,María García,2024-01-15,9.0,60,15,Regular
3,Carlos López,2024-01-15,16.0,95,2,Excelente
```

### Columnas Requeridas:
- `estudiante_id`: ID único del estudiante
- `nombre`: Nombre completo
- `fecha`: Fecha de registro (YYYY-MM-DD)
- `nota_final`: Nota de 0-20
- `asistencia`: Porcentaje 0-100
- `inasistencia`: Número de inasistencias
- `conducta`: Buena, Regular, Mala

## 🎓 Siguiente Paso

Una vez que todo esté funcionando:

1. Lee la documentación completa en `README.md`
2. Explora la API en http://localhost:8000/docs
3. Revisa los documentos de arquitectura en la carpeta raíz

## 📞 Ayuda

Si tienes problemas:
- Revisa la documentación completa: `README.md`
- Abre un issue en GitHub
- Revisa los logs del backend y frontend

---

¡Listo! Ahora tienes EduForge funcionando. 🎉

