# Changelog

All notable changes to EduForge will be documented in this file.

## [1.0.0] - 2025-01-XX

### Added

#### Backend
- FastAPI REST API with CORS support
- Machine Learning model using Random Forest Classifier
- Model training script with synthetic data generation
- `/predict` endpoint for dropout probability prediction
- `/analyze` endpoint for detailed student analysis
- Automatic recommendations generation based on student data
- Comprehensive factors analysis (academic, attendance, study habits, socioeconomic, engagement)
- Health check endpoint
- Pydantic models for data validation

#### Frontend
- React application with Vite build tool
- Interactive Dashboard with:
  - Statistics cards (Total, Low Risk, Medium Risk, High Risk)
  - Pie chart for risk distribution
  - Bar chart for grade vs attendance comparison
  - Student list table with all indicators
- Individual Student Analysis view with:
  - Comprehensive input form (8 different factors)
  - Real-time prediction results
  - Risk level visualization with color-coded badges
  - Radar chart for student profile visualization
  - Detailed factors analysis cards
  - Personalized recommendations
- Modern, responsive UI with gradient colors
- Tab navigation between Dashboard and Analysis views
- Recharts integration for data visualization

#### ML Model
- Random Forest Classifier with 100 estimators
- 8 input features (attendance, grades, study hours, family income, parent education, activities, failed subjects, age)
- Balanced class weights for better prediction
- Synthetic data generation for training (1000 samples)
- Model persistence with joblib
- ~80% accuracy on test set

#### Documentation
- Comprehensive README with:
  - Feature descriptions
  - Installation instructions
  - API documentation
  - Technology stack
  - Use cases
- API_DOCUMENTATION.md with detailed endpoint specifications
- CONTRIBUTING.md with contribution guidelines
- Startup scripts for easy backend and frontend launch

#### Infrastructure
- Python requirements.txt with all dependencies
- .gitignore configured for Python and Node.js
- Executable shell scripts for starting services
- Project structure organized by concerns

### Features Highlights

1. **Predictive Analytics**: ML-powered dropout risk prediction with 84.5% probability for high-risk cases
2. **Interactive Dashboard**: Real-time visualization of student population risk distribution
3. **Individual Assessment**: Detailed analysis with personalized recommendations
4. **Responsive Design**: Works on desktop and mobile devices
5. **RESTful API**: Well-structured API with automatic documentation
6. **Educational Insights**: Recommendations categorized by risk factors

### Technical Stack

- **Backend**: FastAPI 0.109.0, scikit-learn 1.4.0, pandas 2.2.0
- **Frontend**: React 18, Vite 7, Recharts, Axios
- **ML**: Random Forest, numpy, joblib

### Risk Assessment Criteria

- **Low Risk** (<30%): Students with good performance across all factors
- **Medium Risk** (30-60%): Students with some concerning indicators
- **High Risk** (>60%): Students requiring immediate intervention

### Recommendations System

Generates context-aware recommendations based on:
- Attendance patterns
- Academic performance
- Study habits
- Failed subjects count
- Extracurricular participation
- Overall risk level
