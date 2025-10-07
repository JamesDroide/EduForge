# EduForge - Quick Start Guide

## ⚡ Get Started in 5 Minutes

### Prerequisites Check
```bash
# Check Python version (need 3.8+)
python --version

# Check Node.js version (need 16+)
node --version

# Check npm
npm --version
```

## 🚀 Installation & Setup

### Step 1: Clone Repository
```bash
git clone https://github.com/JamesDroide/EduForge.git
cd EduForge
```

### Step 2: Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Train the ML model
cd backend
python train_model.py
cd ..
```

**Expected Output:**
```
Generando datos sintéticos...
Total de muestras: 1000
Deserción: 240 (24.00%)
No deserción: 760 (76.00%)

Entrenando modelo Random Forest...
Evaluating modelo...
Accuracy: 0.8050

Modelo guardado en: /path/to/backend/models/dropout_model.pkl
```

### Step 3: Frontend Setup
```bash
# Install Node.js dependencies
cd frontend
npm install
cd ..
```

### Step 4: Start Services

**Option A: Using Scripts (Recommended)**
```bash
# Terminal 1 - Start Backend
./start-backend.sh

# Terminal 2 - Start Frontend  
./start-frontend.sh
```

**Option B: Manual Start**
```bash
# Terminal 1 - Backend
cd backend/app
python main.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Step 5: Access Application
- **Frontend**: Open http://localhost:5173 in your browser
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🎯 First Steps

### 1. Explore Dashboard
1. Navigate to http://localhost:5173
2. Click "📊 Dashboard" tab
3. View 20 sample students with risk predictions
4. Click "🔄 Actualizar Datos" to generate new samples

### 2. Analyze Individual Student
1. Click "👤 Análisis Individual" tab
2. Fill in the student form:
   - Set attendance rate (e.g., 85%)
   - Enter average grade (e.g., 7.5)
   - Add study hours per week (e.g., 15)
   - Complete other fields
3. Click "🔍 Analizar Estudiante"
4. View detailed analysis with recommendations

### 3. Test API Directly
```bash
# Basic health check
curl http://localhost:8000/health

# Predict dropout for a student
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "attendance_rate": 85,
    "average_grade": 7.5,
    "study_hours_per_week": 15,
    "family_income": 2500,
    "parent_education_level": 3,
    "extracurricular_activities": 2,
    "failed_subjects": 0,
    "age": 18
  }'
```

## 📊 Understanding the Output

### Risk Levels
- 🟢 **Bajo (Low)**: < 30% probability → Student is on track
- 🟡 **Medio (Medium)**: 30-60% probability → Monitor closely
- 🔴 **Alto (High)**: > 60% probability → Immediate intervention needed

### Sample Predictions

**Low Risk Student:**
```json
{
  "dropout_probability": 4.71,
  "risk_level": "Bajo",
  "recommendations": [
    "Mantener el buen rendimiento actual"
  ]
}
```

**High Risk Student:**
```json
{
  "dropout_probability": 84.5,
  "risk_level": "Alto",
  "recommendations": [
    "Mejorar asistencia a clases - Meta: >85%",
    "Reforzar rendimiento académico con tutorías",
    "Aumentar horas de estudio semanales - Recomendado: 15-20h",
    "Programa de apoyo académico urgente",
    "Participar en actividades extracurriculares para integración",
    "Intervención inmediata: Entrevista con orientador"
  ]
}
```

## 🎨 Dashboard Features

### Statistics Cards
- **Total Estudiantes**: Count of all students
- **Riesgo Bajo**: Students with low dropout risk
- **Riesgo Medio**: Students requiring monitoring
- **Riesgo Alto**: Students needing intervention

### Visualizations
- **Pie Chart**: Risk distribution across student population
- **Bar Chart**: Comparison of grades vs attendance
- **Table**: Detailed list with all indicators

### Interactive Elements
- Sort table columns
- Hover for detailed information
- Click refresh to generate new data

## 🔧 Troubleshooting

### Backend Issues

**Problem**: Model not found
```bash
# Solution: Train the model
cd backend
python train_model.py
```

**Problem**: Port 8000 already in use
```bash
# Find process using port
lsof -i :8000
# Kill the process
kill -9 <PID>
```

### Frontend Issues

**Problem**: Port 5173 already in use
```bash
# Edit vite.config.js to use different port
export default defineConfig({
  server: {
    port: 5174  // Change port
  }
})
```

**Problem**: CORS errors
- Ensure backend is running
- Check backend CORS settings in main.py

### Common Errors

**Error**: `ModuleNotFoundError: No module named 'fastapi'`
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**Error**: `npm: command not found`
```bash
# Solution: Install Node.js
# Visit: https://nodejs.org/
```

## 📚 Next Steps

1. **Read Documentation**
   - [README.md](README.md) - Overview and setup
   - [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API reference
   - [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute

2. **Explore Code**
   - Backend: `backend/app/main.py`
   - Frontend: `frontend/src/components/`
   - ML Model: `backend/train_model.py`

3. **Customize**
   - Modify model parameters
   - Add new features
   - Improve UI/UX
   - Extend recommendations

4. **Deploy**
   - Set up production server
   - Configure reverse proxy (nginx)
   - Use environment variables
   - Enable HTTPS

## 🎓 Example Use Cases

### Use Case 1: Identify At-Risk Students
```bash
# Generate list of high-risk students
# Use Dashboard → Filter by "Alto" risk level
# Review recommendations for each student
```

### Use Case 2: Track Individual Progress
```bash
# Enter student data monthly
# Compare predictions over time
# Adjust interventions based on changes
```

### Use Case 3: Evaluate Interventions
```bash
# Predict risk before intervention
# Apply support program
# Re-predict after intervention
# Measure improvement
```

## 💡 Tips for Best Results

1. **Data Quality**: Ensure accurate input data
2. **Regular Updates**: Analyze students frequently
3. **Action on Insights**: Implement recommendations
4. **Track Progress**: Monitor changes over time
5. **Combine Factors**: Look at all indicators together

## 🆘 Getting Help

- **Issues**: Open issue on GitHub
- **Questions**: Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Contributions**: See [CONTRIBUTING.md](CONTRIBUTING.md)

## ✅ Checklist

Before starting:
- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] Git installed
- [ ] Repository cloned
- [ ] Python dependencies installed
- [ ] ML model trained
- [ ] Node modules installed
- [ ] Backend running on :8000
- [ ] Frontend running on :5173
- [ ] Browser opened to http://localhost:5173

---

**You're all set! 🎉** Start exploring EduForge and predicting student success! 🎓✨
