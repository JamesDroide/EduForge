# 🔒 Guía de Seguridad - EduForge

## 📋 Gestión de Credenciales del Superadmin

### ⚠️ IMPORTANTE: Credenciales Privadas

Las credenciales del superadministrador del panel de gestión se manejan mediante **variables de entorno** y **NUNCA** deben estar hardcodeadas en el código fuente.

### 🔑 Configuración de Variables de Entorno

#### Archivo `.env` (Local)

Las credenciales se configuran en el archivo `.env` en la raíz del proyecto:

```env
# ====================================
# CREDENCIALES DEL SUPERADMIN - PANEL DE GESTIÓN
# ====================================
SUPERADMIN_USERNAME=administrador
SUPERADMIN_PASSWORD=tu_contraseña_segura_aqui
SUPERADMIN_EMAIL=administrador@eduforge.com
ADMIN_ACCESS_CODE=TU_CODIGO_SEGURO_AQUI
```

**⚠️ NUNCA** subas el archivo `.env` al repositorio Git.

#### Variables de Entorno en Producción

Para entornos de producción (Railway, Vercel, etc.), configura las variables de entorno en el panel de configuración de tu plataforma:

- `SUPERADMIN_USERNAME`
- `SUPERADMIN_PASSWORD`
- `SUPERADMIN_EMAIL`
- `ADMIN_ACCESS_CODE`
- `SECRET_KEY`
- `DATABASE_URL`

### 🛡️ Protección del Usuario Superadmin

El usuario superadmin está **completamente oculto y protegido** en el panel de administración:

#### ✅ Protecciones Implementadas:

1. **No visible en la lista de usuarios**: El endpoint `/admin/users` filtra automáticamente al superadmin
2. **No accesible individualmente**: No se puede obtener su información vía `/admin/users/{id}`
3. **No editable**: No se puede modificar sus datos
4. **No puede cambiar su contraseña desde el panel**: Solo mediante variables de entorno
5. **No eliminable**: Está protegido contra eliminación accidental

#### 🔒 Cómo funciona:

```python
# Todos los endpoints verifican:
SUPERADMIN_USERNAME = os.getenv("SUPERADMIN_USERNAME", "administrador")

# Y rechazan operaciones con:
if user.username == SUPERADMIN_USERNAME:
    raise HTTPException(403, "No se puede acceder/modificar este usuario")
```

### 🛠️ Crear/Actualizar Usuario Superadmin

Para crear o actualizar el usuario superadmin, ejecuta:

```bash
python src/migrations/create_admin_panel_user.py
```

Este script:
- ✅ Lee las credenciales desde variables de entorno
- ✅ Crea el usuario si no existe
- ✅ Actualiza las credenciales si el usuario ya existe
- ✅ NO expone credenciales en logs públicos

### 🔐 Dos Tipos de Usuarios Independientes

El sistema mantiene **dos usuarios administradores independientes**:

#### 1. Usuario `admin` (Sistema General)
- **Propósito**: Acceso general a la API
- **Credenciales por defecto**: 
  - Username: `admin`
  - Password: `admin123`
- **Uso**: Login regular, gestión de API
- **Cambiar después del primer login**
- **Visible en el panel de administración**: ✅ SÍ

#### 2. Usuario `administrador` (Panel de Gestión - Superadmin)
- **Propósito**: Acceso exclusivo al panel de administración especial
- **Credenciales**: Definidas en variables de entorno
- **Requiere**: Username + Password + Código de Acceso
- **Uso**: Gestión completa del sistema, panel administrativo
- **Visible en el panel de administración**: ❌ NO (oculto por seguridad)

### 🚫 Endpoints Eliminados por Seguridad

Los siguientes endpoints fueron **eliminados** por exponer información sensible:

- ❌ `/diagnostico-usuarios` - Exponía credenciales en respuesta JSON

### ✅ Mejores Prácticas

1. **Variables de Entorno**
   - ✅ Usa siempre variables de entorno para credenciales
   - ✅ Mantén un archivo `.env.example` con valores de ejemplo
   - ✅ Nunca commitees el archivo `.env` real

2. **Credenciales Seguras**
   - ✅ Usa contraseñas fuertes (min. 12 caracteres)
   - ✅ Combina letras, números y símbolos
   - ✅ Cambia las contraseñas por defecto inmediatamente

3. **Gestión de Secretos**
   - ✅ Rota las credenciales periódicamente
   - ✅ Usa diferentes credenciales para desarrollo y producción
   - ✅ Limita el acceso al archivo `.env`

4. **Logs y Documentación**
   - ✅ NO registres credenciales en logs
   - ✅ NO documentes credenciales reales en README
   - ✅ Usa placeholders genéricos en ejemplos

5. **Panel de Administración**
   - ✅ El superadmin NO debe aparecer en listados
   - ✅ El superadmin NO debe ser editable desde la interfaz
   - ✅ El superadmin solo se gestiona mediante scripts de migración

### 🔄 Cambiar Credenciales del Superadmin

1. Actualiza las variables en `.env`:
   ```env
   SUPERADMIN_USERNAME=nuevo_usuario
   SUPERADMIN_PASSWORD=nueva_contraseña_segura
   SUPERADMIN_EMAIL=nuevo_email@dominio.com
   ADMIN_ACCESS_CODE=NUEVO_CODIGO_2025
   ```

2. Ejecuta el script de migración:
   ```bash
   python src/migrations/create_admin_panel_user.py
   ```

3. Verifica el cambio intentando iniciar sesión con las nuevas credenciales.

### 📝 Checklist de Seguridad

Antes de subir a producción, verifica:

- [ ] Archivo `.env` está en `.gitignore`
- [ ] Variables de entorno configuradas en el servidor de producción
- [ ] Contraseñas por defecto cambiadas
- [ ] `SECRET_KEY` único y seguro en producción
- [ ] `ADMIN_ACCESS_CODE` único y no predecible
- [ ] Credenciales del superadmin son fuertes
- [ ] No hay credenciales hardcodeadas en el código
- [ ] Logs no exponen información sensible
- [ ] Usuario superadmin NO visible en el panel de administración
- [ ] Endpoints de diagnóstico eliminados

### 🆘 Recuperación de Acceso

Si pierdes acceso al panel de administración:

1. Verifica las variables en `.env`
2. Ejecuta el script de diagnóstico (solo en desarrollo local):
   ```bash
   python src/migrations/create_admin_panel_user.py
   ```
3. Revisa los logs del script para confirmar las credenciales
4. Si es necesario, actualiza manualmente en la base de datos (última opción)

### 📞 Contacto de Seguridad

Para reportar vulnerabilidades de seguridad, contacta al equipo de desarrollo de forma privada.

---

**Última actualización**: 2025-10-14

