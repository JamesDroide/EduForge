import { useState } from 'react'
import './App.css'
import Dashboard from './components/Dashboard'
import StudentAnalysis from './components/StudentAnalysis'

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')

  return (
    <div className="app">
      <header className="app-header">
        <h1>🎓 EduForge</h1>
        <p>Sistema de Predicción de Deserción Estudiantil</p>
      </header>
      
      <nav className="app-nav">
        <button 
          className={activeTab === 'dashboard' ? 'active' : ''}
          onClick={() => setActiveTab('dashboard')}
        >
          📊 Dashboard
        </button>
        <button 
          className={activeTab === 'analysis' ? 'active' : ''}
          onClick={() => setActiveTab('analysis')}
        >
          👤 Análisis Individual
        </button>
      </nav>

      <main className="app-main">
        {activeTab === 'dashboard' ? <Dashboard /> : <StudentAnalysis />}
      </main>

      <footer className="app-footer">
        <p>EduForge - Sistema predictivo con Machine Learning | FastAPI + React + scikit-learn</p>
      </footer>
    </div>
  )
}

export default App
