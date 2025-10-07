# 🚀 EduForge - Guía de Despliegue Profesional

## Configuración Profesional Recomendada

**Frontend:** Vercel (React) - CDN global, SSL automático  
**Backend:** Railway (FastAPI/Python) - Base de datos incluida

## 📋 Pasos para Despliegue

### 1. Backend en Railway 

1. Ve a [railway.app](https://railway.app)
2. Conecta tu repositorio GitHub
3. Selecciona "Deploy from GitHub repo"
4. Railway detectará automáticamente el `railway.toml`
5. Copia la URL generada (ej: `https://eduforge-backend.up.railway.app`)

### 2. Frontend en Vercel 

1. Ve a [vercel.com](https://vercel.com)
2. Conecta tu repositorio GitHub
3. **IMPORTANTE:** Configura estas variables de entorno:
   ```
   REACT_APP_API_URL = https://tu-app-railway.up.railway.app
   REACT_APP_NODE_ENV = production
   ```
4. Deploy automático desde la carpeta `frontend`

## 🌟 Características Profesionales Incluidas

- ✅ CDN global automático (Vercel)
- ✅ SSL certificates automáticos
- ✅ Deploy automático desde GitHub
- ✅ Dominios personalizados
- ✅ Métricas de rendimiento
- ✅ Logs profesionales
- ✅ Base de datos PostgreSQL (Railway)

## 🔧 Configuraciones Técnicas

- `vercel.json` - Configuración de Vercel
- `railway.toml` - Configuración de Railway  
- `netlify.toml` - Alternativa con Netlify
- Variables de entorno configuradas automáticamente

## 🎯 Resultado Final

Tu aplicación estará disponible en:
- **Frontend:** `https://tu-app.vercel.app`
- **Backend:** `https://tu-app.up.railway.app`
- **Dominio personalizado:** Configurable gratis

¡Completamente profesional y gratuito!
