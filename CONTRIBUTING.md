# Guía de Contribución a EduForge

¡Gracias por tu interés en contribuir a EduForge! Este documento proporciona directrices para contribuir al proyecto.

## 🚀 Comenzando

### Requisitos Previos
- Python 3.8 o superior
- Node.js 16 o superior
- Git
- Un editor de código (VS Code, PyCharm, etc.)

### Configuración del Entorno de Desarrollo

1. **Fork del Repositorio**
   ```bash
   # Fork en GitHub, luego clona tu fork
   git clone https://github.com/TU_USUARIO/EduForge.git
   cd EduForge
   ```

2. **Configurar Backend**
   ```bash
   # Instalar dependencias
   pip install -r requirements.txt
   
   # Entrenar el modelo
   cd backend
   python train_model.py
   
   # Iniciar servidor
   cd app
   python main.py
   ```

3. **Configurar Frontend**
   ```bash
   # Instalar dependencias
   cd frontend
   npm install
   
   # Iniciar servidor de desarrollo
   npm run dev
   ```

## 📋 Cómo Contribuir

### Reportar Bugs

Si encuentras un bug, por favor crea un issue con:
- Descripción clara del problema
- Pasos para reproducir
- Comportamiento esperado vs actual
- Capturas de pantalla (si aplica)
- Información del entorno (OS, versiones, etc.)

### Sugerir Mejoras

Para sugerir nuevas características:
- Crea un issue describiendo la funcionalidad
- Explica el caso de uso
- Proporciona ejemplos si es posible

### Pull Requests

1. **Crear una Rama**
   ```bash
   git checkout -b feature/nombre-descriptivo
   ```

2. **Hacer Cambios**
   - Sigue las convenciones de código del proyecto
   - Escribe código limpio y documentado
   - Agrega tests si es necesario

3. **Commit**
   ```bash
   git add .
   git commit -m "Descripción clara del cambio"
   ```

4. **Push y PR**
   ```bash
   git push origin feature/nombre-descriptivo
   ```
   Luego crea un Pull Request en GitHub

## 🎨 Estándares de Código

### Python (Backend)
- Sigue PEP 8
- Usa type hints cuando sea posible
- Documenta funciones con docstrings
- Nombres descriptivos para variables y funciones

```python
def calculate_risk(student_data: StudentData) -> float:
    """
    Calcula el riesgo de deserción para un estudiante.
    
    Args:
        student_data: Datos del estudiante
        
    Returns:
        Probabilidad de deserción (0-1)
    """
    pass
```

### JavaScript/React (Frontend)
- Usa ESLint
- Componentes funcionales con hooks
- Nombres descriptivos para componentes y funciones
- Documenta funciones complejas

```javascript
/**
 * Calcula las estadísticas de riesgo de los estudiantes
 * @param {Array} students - Lista de estudiantes
 * @returns {Object} Estadísticas calculadas
 */
const calculateStats = (students) => {
  // ...
}
```

## 🧪 Tests

### Backend
```bash
# Ejecutar tests (cuando estén disponibles)
pytest tests/
```

### Frontend
```bash
# Ejecutar tests (cuando estén disponibles)
cd frontend
npm test
```

## 📝 Commit Messages

Usa mensajes descriptivos siguiendo este formato:

```
tipo: descripción breve

Descripción más detallada del cambio (opcional)
```

Tipos:
- `feat`: Nueva funcionalidad
- `fix`: Corrección de bug
- `docs`: Cambios en documentación
- `style`: Cambios de formato (no afectan código)
- `refactor`: Refactorización de código
- `test`: Agregar o modificar tests
- `chore`: Tareas de mantenimiento

Ejemplos:
```
feat: agregar validación de edad en formulario

fix: corregir cálculo de probabilidad de deserción

docs: actualizar README con instrucciones de instalación
```

## 🔍 Proceso de Review

1. Un mantenedor revisará tu PR
2. Puede haber comentarios o solicitudes de cambios
3. Realiza los cambios solicitados
4. Una vez aprobado, se hará merge

## 🌟 Áreas de Contribución

### Backend
- Mejorar el modelo de ML (nuevos algoritmos, features)
- Optimizar el rendimiento de la API
- Agregar nuevos endpoints
- Mejorar validaciones y manejo de errores

### Frontend
- Mejorar UI/UX
- Agregar nuevas visualizaciones
- Optimizar rendimiento
- Mejorar responsive design
- Agregar temas (modo oscuro)

### Documentación
- Mejorar README
- Agregar tutoriales
- Traducir documentación
- Crear videos explicativos

### Tests
- Agregar tests unitarios
- Tests de integración
- Tests E2E

### Infraestructura
- Configuración de CI/CD
- Docker/Docker Compose
- Scripts de deployment

## 📞 Contacto

Si tienes preguntas, puedes:
- Abrir un issue en GitHub
- Contactar a los mantenedores

## 📄 Licencia

Al contribuir a EduForge, aceptas que tus contribuciones se licenciarán bajo la [Licencia MIT](LICENSE).

---

¡Gracias por contribuir a EduForge! 🎓✨
