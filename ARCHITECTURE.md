# EduForge System Architecture

## 🏛️ High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                           │
│                       (Web Browser)                              │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ HTTP/HTTPS
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                      FRONTEND LAYER                              │
│                     (React + Vite)                               │
│  ┌──────────────────┐            ┌───────────────────────┐     │
│  │   Dashboard      │            │  Student Analysis     │     │
│  │   Component      │            │     Component         │     │
│  │  - Stats Cards   │            │  - Input Form         │     │
│  │  - Pie Chart     │            │  - Risk Circle        │     │
│  │  - Bar Chart     │            │  - Radar Chart        │     │
│  │  - Table         │            │  - Factor Cards       │     │
│  └──────────────────┘            └───────────────────────┘     │
│                                                                  │
│  Libraries: Recharts, Axios                                     │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ REST API (JSON)
                            │ POST /predict
                            │ POST /analyze
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                       BACKEND LAYER                              │
│                      (FastAPI)                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   API Endpoints                          │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │   │
│  │  │   GET    │  │   GET    │  │   POST   │  │  POST  │ │   │
│  │  │    /     │  │ /health  │  │ /predict │  │/analyze│ │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └────────┘ │   │
│  └─────────────────────────┬───────────────────────────────┘   │
│                            │                                     │
│  ┌─────────────────────────▼───────────────────────────────┐   │
│  │              Business Logic Layer                        │   │
│  │  - Data validation (Pydantic)                           │   │
│  │  - Risk level calculation                               │   │
│  │  - Recommendation generation                            │   │
│  │  - Factor analysis                                      │   │
│  └─────────────────────────┬───────────────────────────────┘   │
│                            │                                     │
└────────────────────────────┼─────────────────────────────────────┘
                            │
                            │ Model Inference
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                    MACHINE LEARNING LAYER                        │
│                   (scikit-learn)                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         Random Forest Classifier                         │   │
│  │                                                          │   │
│  │  Input Features (8):                                    │   │
│  │  - Attendance Rate        - Family Income               │   │
│  │  - Average Grade          - Parent Education            │   │
│  │  - Study Hours/Week       - Extracurricular Activities  │   │
│  │  - Failed Subjects        - Age                         │   │
│  │                                                          │   │
│  │  Output:                                                │   │
│  │  - Dropout Probability (0-100%)                         │   │
│  │  - Risk Level (Low/Medium/High)                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Model: dropout_model.pkl (1.3 MB)                              │
│  Trained on: 1000 synthetic samples                             │
│  Accuracy: ~80%                                                 │
└──────────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow

### 1. Prediction Request Flow
```
User Input Form
    │
    ├── Validation (Client-side)
    │
    ▼
HTTP POST Request (JSON)
    │
    ├── CORS Check
    │
    ▼
FastAPI Endpoint (/predict)
    │
    ├── Pydantic Validation
    │
    ▼
Feature Extraction
    │
    ├── Convert to numpy array
    │
    ▼
ML Model Inference
    │
    ├── predict_proba()
    │
    ▼
Risk Calculation
    │
    ├── Threshold: <30% = Low, 30-60% = Medium, >60% = High
    │
    ▼
Recommendation Generation
    │
    ├── Rule-based logic
    │
    ▼
JSON Response
    │
    ├── dropout_probability
    ├── risk_level
    └── recommendations
    │
    ▼
Frontend Rendering
    │
    ├── Update UI
    ├── Display charts
    └── Show recommendations
```

### 2. Analysis Request Flow
```
User Input + Student ID
    │
    ▼
HTTP POST /analyze?student_id=XXX
    │
    ▼
Prediction (as above)
    │
    ▼
Factor Analysis
    │
    ├── Academic Performance
    ├── Attendance
    ├── Study Habits
    ├── Socioeconomic Factors
    └── Engagement
    │
    ▼
Comprehensive Response
    │
    ├── Student Data
    ├── Prediction
    └── Factors Analysis
    │
    ▼
Detailed UI Rendering
    │
    ├── Risk Circle
    ├── Factor Cards
    ├── Radar Chart
    └── Recommendations List
```

## 🗂️ Component Structure

### Frontend Components
```
frontend/src/
├── main.jsx                 # Entry point
├── App.jsx                  # Main app component
├── App.css                  # App styles
├── index.css               # Global styles
└── components/
    ├── Dashboard.jsx        # Dashboard view
    ├── Dashboard.css        # Dashboard styles
    ├── StudentAnalysis.jsx  # Analysis view
    └── StudentAnalysis.css  # Analysis styles
```

### Backend Structure
```
backend/
├── app/
│   └── main.py             # FastAPI application
├── models/
│   └── dropout_model.pkl   # Trained ML model
└── train_model.py          # Model training script
```

## 🔐 Security Considerations

### Current Implementation
- ✅ CORS configured for cross-origin requests
- ✅ Input validation with Pydantic
- ✅ Type safety with Python type hints
- ✅ Error handling with try-catch blocks

### Production Recommendations
- 🔒 Add authentication (JWT tokens)
- 🔒 Rate limiting for API endpoints
- 🔒 HTTPS/TLS encryption
- 🔒 Environment variables for configuration
- 🔒 Input sanitization
- 🔒 SQL injection prevention (if using DB)
- 🔒 API key management

## 📦 Dependencies

### Backend Dependencies
```
fastapi==0.109.0           # Web framework
uvicorn==0.27.0           # ASGI server
scikit-learn==1.4.0       # ML library
pandas==2.2.0             # Data processing
numpy==1.26.3             # Numerical computing
pydantic==2.5.3           # Data validation
joblib==1.3.2             # Model persistence
python-multipart==0.0.6   # Form data support
```

### Frontend Dependencies
```
react: 18.3.1             # UI library
vite: ^7.1.9              # Build tool
recharts: ^2.15.1         # Charts
axios: ^1.7.9             # HTTP client
```

## 🚀 Deployment Architecture

### Development
```
┌──────────────┐         ┌──────────────┐
│   Frontend   │         │   Backend    │
│  localhost   │  HTTP   │  localhost   │
│   :5173      │◄───────►│    :8000     │
└──────────────┘         └──────────────┘
```

### Production (Recommended)
```
                          ┌──────────────┐
                          │    Nginx     │
                          │ Reverse Proxy│
                          │   (SSL/TLS)  │
                          └───────┬──────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
            ┌───────▼────────┐        ┌────────▼────────┐
            │   Frontend     │        │    Backend      │
            │   (Static)     │        │   (Uvicorn)     │
            │   Port 80/443  │        │   Port 8000     │
            └────────────────┘        └─────────┬───────┘
                                                │
                                     ┌──────────▼────────┐
                                     │   ML Model Files  │
                                     │   (Persistent)    │
                                     └───────────────────┘
```

## 📊 Performance Optimization

### Backend Optimizations
- Model loaded once at startup
- Numpy arrays for fast computation
- Minimal data transformation
- Efficient endpoint design

### Frontend Optimizations
- React lazy loading (potential)
- Chart data memoization
- Conditional rendering
- CSS optimization

## 🔧 Configuration

### Backend Configuration
```python
# backend/app/main.py
app = FastAPI(
    title="EduForge API",
    description="Sistema de predicción de deserción estudiantil",
    version="1.0.0"
)

# CORS settings
allow_origins=["*"]  # Restrict in production
```

### Frontend Configuration
```javascript
// frontend/vite.config.js
server: {
    host: '0.0.0.0',
    port: 5173
}

// API URL
const API_URL = 'http://localhost:8000'
```

## 📈 Scalability

### Current Capacity
- Single instance deployment
- Handles ~100 concurrent users
- <100ms response time per request

### Scaling Options
- **Horizontal**: Multiple backend instances + load balancer
- **Vertical**: Increase server resources
- **Caching**: Redis for frequently accessed predictions
- **Database**: PostgreSQL for historical data
- **Queue**: Celery for async processing

## 🧪 Testing Strategy

### Backend Testing
```
Unit Tests:
- Model prediction accuracy
- Endpoint response validation
- Business logic correctness

Integration Tests:
- API endpoint functionality
- Model loading and inference
- Error handling
```

### Frontend Testing
```
Unit Tests:
- Component rendering
- Form validation
- Data transformations

E2E Tests:
- User workflows
- API integration
- Chart rendering
```

## 📝 Logging & Monitoring

### Current Logging
- Console output for requests
- Error messages with stack traces
- Model loading status

### Production Recommendations
- Structured logging (JSON format)
- Log aggregation (ELK stack)
- Application monitoring (Prometheus, Grafana)
- Error tracking (Sentry)
- Performance metrics

## 🔄 CI/CD Pipeline (Proposed)

```
Code Push → GitHub Actions
    │
    ├── Lint & Format Check
    ├── Run Tests
    ├── Build Application
    ├── Security Scan
    │
    ▼
Deploy to Staging
    │
    ├── Smoke Tests
    ├── Integration Tests
    │
    ▼
Manual Approval
    │
    ▼
Deploy to Production
    │
    └── Health Check
```

---

This architecture is designed to be:
- **Modular**: Easy to modify individual components
- **Scalable**: Can handle growth in users and data
- **Maintainable**: Clear separation of concerns
- **Extensible**: Simple to add new features

For questions or suggestions about the architecture, please open an issue on GitHub.
