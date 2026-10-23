# EduForge - Guia de Despliegue Profesional

## Configuracion Profesional Recomendada

**Frontend:** Vercel (React) - CDN global, SSL automatico  
**Backend:** Railway (FastAPI/Python) - Base de datos incluida

## Pasos para Despliegue

### 1. Backend en Railway 

1. Ve a [railway.app](https://railway.app)
2. Conecta tu repositorio GitHub
3. Selecciona "Deploy from GitHub repo" y define **`backend`** como **Root Directory**
4. Railway detectara automaticamente `backend/railway.toml`
5. Copia la URL generada (ej: `https://eduforge-backend.up.railway.app`)

### 2. Frontend en Vercel 

1. Ve a [vercel.com](https://vercel.com)
2. Conecta tu repositorio GitHub y define **`frontend`** como **Root Directory**
3. **IMPORTANTE:** Configura estas variables de entorno:
   ```
   REACT_APP_API_URL = https://tu-app-railway.up.railway.app
   REACT_APP_NODE_ENV = production
   ```
4. Deploy automatico desde la carpeta `frontend`

## Caracteristicas Profesionales Incluidas

- CDN global automatico (Vercel)
- Certificados SSL automaticos
- Deploy automatico desde GitHub
- Dominios personalizados
- Metricas de rendimiento
- Logs profesionales
- Base de datos PostgreSQL (Railway)

## Configuraciones Tecnicas

- `frontend/vercel.json` - Configuracion de Vercel
- `backend/railway.toml` - Configuracion de Railway  
- `frontend/netlify.toml` - Alternativa con Netlify
- Variables de entorno separadas en `backend/.env` y `frontend/.env.*`

## Resultado Final

Tu aplicacion estara disponible en:
- **Frontend:** `https://tu-app.vercel.app`
- **Backend:** `https://tu-app.up.railway.app`
- **Dominio personalizado:** Configurable gratis
