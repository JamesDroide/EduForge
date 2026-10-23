# Guia de Seguridad - EduForge

## Gestion de Credenciales del Superadmin

### IMPORTANTE: Credenciales Privadas

Las credenciales del superadministrador del panel de gestion se manejan mediante **variables de entorno** y **NUNCA** deben estar hardcodeadas en el codigo fuente.

### Configuracion de Variables de Entorno

#### Archivo `.env` (Local)

Las credenciales se configuran en el archivo `.env` en `backend/.env`:

```env
SUPERADMIN_USERNAME=administrador
SUPERADMIN_PASSWORD=tu_contrasena_segura_aqui
SUPERADMIN_EMAIL=administrador@eduforge.com
ADMIN_ACCESS_CODE=TU_CODIGO_SEGURO_AQUI
```

**NUNCA** subas el archivo `.env` al repositorio Git.

#### Variables de Entorno en Produccion

Para entornos de produccion (Railway, Vercel, etc.), configura las variables de entorno en el panel de configuracion de tu plataforma:

- `SUPERADMIN_USERNAME`
- `SUPERADMIN_PASSWORD`
- `SUPERADMIN_EMAIL`
- `ADMIN_ACCESS_CODE`
- `SECRET_KEY`
- `DATABASE_URL`

### Proteccion del Usuario Superadmin

El usuario superadmin esta **completamente oculto y protegido** en el panel de administracion:

#### Protecciones Implementadas:

1. **No visible en la lista de usuarios**: El endpoint `/admin/users` filtra automaticamente al superadmin
2. **No accesible individualmente**: No se puede obtener su informacion via `/admin/users/{id}`
3. **No editable**: No se puede modificar sus datos
4. **No puede cambiar su contrasena desde el panel**: Solo mediante variables de entorno
5. **No eliminable**: Esta protegido contra eliminacion accidental

#### Como funciona:

```python
SUPERADMIN_USERNAME = os.getenv("SUPERADMIN_USERNAME", "administrador")

if user.username == SUPERADMIN_USERNAME:
    raise HTTPException(403, "No se puede acceder/modificar este usuario")
```

### Crear/Actualizar Usuario Superadmin

Para crear o actualizar el usuario superadmin, ejecuta:

```bash
python src/migrations/create_admin_panel_user.py
```

Este script:
- Lee las credenciales desde variables de entorno
- Crea el usuario si no existe
- Actualiza las credenciales si el usuario ya existe
- NO expone credenciales en logs publicos

### Dos Tipos de Usuarios Independientes

El sistema mantiene **dos usuarios administradores independientes**:

#### 1. Usuario `admin` (Sistema General)
- **Proposito**: Acceso general a la API
- **Credenciales por defecto**: 
  - Username: `admin`
  - Password: `admin123`
- **Uso**: Login regular, gestion de API
- **Cambiar despues del primer login**
- **Visible en el panel de administracion**: SI

#### 2. Usuario `administrador` (Panel de Gestion - Superadmin)
- **Proposito**: Acceso exclusivo al panel de administracion especial
- **Credenciales**: Definidas en variables de entorno
- **Requiere**: Username + Password + Codigo de Acceso
- **Uso**: Gestion completa del sistema, panel administrativo
- **Visible en el panel de administracion**: NO (oculto por seguridad)

### Endpoints Eliminados por Seguridad

Los siguientes endpoints fueron **eliminados** por exponer informacion sensible:

- `/diagnostico-usuarios` - Exponia credenciales en respuesta JSON

### Mejores Practicas

1. **Variables de Entorno**
   - Usa siempre variables de entorno para credenciales
   - Manten un archivo `.env.example` con valores de ejemplo
   - Nunca commitees el archivo `.env` real

2. **Credenciales Seguras**
   - Usa contrasenas fuertes (min. 12 caracteres)
   - Combina letras, numeros y simbolos
   - Cambia las contrasenas por defecto inmediatamente

3. **Gestion de Secretos**
   - Rota las credenciales periodicamente
   - Usa diferentes credenciales para desarrollo y produccion
   - Limita el acceso al archivo `.env`

4. **Logs y Documentacion**
   - NO registres credenciales en logs
   - NO documentes credenciales reales en README
   - Usa placeholders genericos en ejemplos

5. **Panel de Administracion**
   - El superadmin NO debe aparecer en listados
   - El superadmin NO debe ser editable desde la interfaz
   - El superadmin solo se gestiona mediante scripts de migracion

### Cambiar Credenciales del Superadmin

1. Actualiza las variables en `.env`:
   ```env
   SUPERADMIN_USERNAME=nuevo_usuario
   SUPERADMIN_PASSWORD=nueva_contrasena_segura
   SUPERADMIN_EMAIL=nuevo_email@dominio.com
   ADMIN_ACCESS_CODE=NUEVO_CODIGO_2025
   ```

2. Ejecuta el script de migracion:
   ```bash
   python src/migrations/create_admin_panel_user.py
   ```

3. Verifica el cambio intentando iniciar sesion con las nuevas credenciales.

### Checklist de Seguridad

Antes de subir a produccion, verifica:

- [ ] Archivo `.env` esta en `.gitignore`
- [ ] Variables de entorno configuradas en el servidor de produccion
- [ ] Contrasenas por defecto cambiadas
- [ ] `SECRET_KEY` unico y seguro en produccion
- [ ] `ADMIN_ACCESS_CODE` unico y no predecible
- [ ] Credenciales del superadmin son fuertes
- [ ] No hay credenciales hardcodeadas en el codigo
- [ ] Logs no exponen informacion sensible
- [ ] Usuario superadmin NO visible en el panel de administracion
- [ ] Endpoints de diagnostico eliminados

### Recuperacion de Acceso

Si pierdes acceso al panel de administracion:

1. Verifica las variables en `.env`
2. Ejecuta el script de diagnostico (solo en desarrollo local):
   ```bash
   python src/migrations/create_admin_panel_user.py
   ```
3. Revisa los logs del script para confirmar las credenciales
4. Si es necesario, actualiza manualmente en la base de datos (ultima opcion)

### Contacto de Seguridad

Para reportar vulnerabilidades de seguridad, contacta al equipo de desarrollo de forma privada.

---

**Ultima actualizacion**: 2025-10-14
