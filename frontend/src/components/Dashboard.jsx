import { useState, useEffect } from 'react'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import './Dashboard.css'

const API_URL = 'http://localhost:8000'

const COLORS = ['#10b981', '#f59e0b', '#ef4444']

const Dashboard = () => {
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState({
    total: 0,
    lowRisk: 0,
    mediumRisk: 0,
    highRisk: 0
  })

  const generateSampleStudents = async () => {
    setLoading(true)
    const sampleStudents = []
    
    for (let i = 1; i <= 20; i++) {
      const studentData = {
        attendance_rate: Math.random() * 50 + 50,
        average_grade: Math.random() * 7 + 3,
        study_hours_per_week: Math.random() * 25 + 5,
        family_income: Math.random() * 4000 + 1000,
        parent_education_level: Math.floor(Math.random() * 5) + 1,
        extracurricular_activities: Math.floor(Math.random() * 5),
        failed_subjects: Math.floor(Math.random() * 6),
        age: Math.floor(Math.random() * 8) + 17
      }

      try {
        const response = await axios.post(`${API_URL}/predict`, studentData)
        sampleStudents.push({
          id: `EST-${String(i).padStart(3, '0')}`,
          ...studentData,
          prediction: response.data
        })
      } catch (error) {
        console.error('Error predicting:', error)
      }
    }

    setStudents(sampleStudents)
    calculateStats(sampleStudents)
    setLoading(false)
  }

  const calculateStats = (studentList) => {
    const stats = {
      total: studentList.length,
      lowRisk: studentList.filter(s => s.prediction.risk_level === 'Bajo').length,
      mediumRisk: studentList.filter(s => s.prediction.risk_level === 'Medio').length,
      highRisk: studentList.filter(s => s.prediction.risk_level === 'Alto').length
    }
    setStats(stats)
  }

  useEffect(() => {
    generateSampleStudents()
  }, [])

  const riskDistribution = [
    { name: 'Riesgo Bajo', value: stats.lowRisk, color: '#10b981' },
    { name: 'Riesgo Medio', value: stats.mediumRisk, color: '#f59e0b' },
    { name: 'Riesgo Alto', value: stats.highRisk, color: '#ef4444' }
  ]

  const gradeDistribution = students.map(s => ({
    id: s.id,
    promedio: parseFloat(s.average_grade.toFixed(1)),
    asistencia: parseFloat(s.attendance_rate.toFixed(1))
  }))

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'Bajo': return '#10b981'
      case 'Medio': return '#f59e0b'
      case 'Alto': return '#ef4444'
      default: return '#6b7280'
    }
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Dashboard de Análisis Predictivo</h2>
        <button onClick={generateSampleStudents} disabled={loading} className="refresh-btn">
          {loading ? '⏳ Cargando...' : '🔄 Actualizar Datos'}
        </button>
      </div>

      <div className="stats-grid">
        <div className="stat-card total">
          <div className="stat-icon">👥</div>
          <div className="stat-content">
            <h3>Total Estudiantes</h3>
            <p className="stat-value">{stats.total}</p>
          </div>
        </div>
        <div className="stat-card low-risk">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <h3>Riesgo Bajo</h3>
            <p className="stat-value">{stats.lowRisk}</p>
            <span className="stat-percent">{((stats.lowRisk / stats.total) * 100 || 0).toFixed(1)}%</span>
          </div>
        </div>
        <div className="stat-card medium-risk">
          <div className="stat-icon">⚠️</div>
          <div className="stat-content">
            <h3>Riesgo Medio</h3>
            <p className="stat-value">{stats.mediumRisk}</p>
            <span className="stat-percent">{((stats.mediumRisk / stats.total) * 100 || 0).toFixed(1)}%</span>
          </div>
        </div>
        <div className="stat-card high-risk">
          <div className="stat-icon">🚨</div>
          <div className="stat-content">
            <h3>Riesgo Alto</h3>
            <p className="stat-value">{stats.highRisk}</p>
            <span className="stat-percent">{((stats.highRisk / stats.total) * 100 || 0).toFixed(1)}%</span>
          </div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h3>Distribución de Riesgo de Deserción</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={riskDistribution}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {riskDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>Promedio vs Asistencia (Top 10 Estudiantes)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={gradeDistribution.slice(0, 10)}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="id" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="promedio" fill="#667eea" name="Promedio" />
              <Bar dataKey="asistencia" fill="#764ba2" name="Asistencia %" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="students-table-card">
        <h3>Lista de Estudiantes</h3>
        <div className="table-container">
          <table className="students-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Promedio</th>
                <th>Asistencia</th>
                <th>Materias Reprobadas</th>
                <th>Horas Estudio/Sem</th>
                <th>Probabilidad</th>
                <th>Nivel de Riesgo</th>
              </tr>
            </thead>
            <tbody>
              {students.map((student) => (
                <tr key={student.id}>
                  <td><strong>{student.id}</strong></td>
                  <td>{student.average_grade.toFixed(1)}</td>
                  <td>{student.attendance_rate.toFixed(1)}%</td>
                  <td>{student.failed_subjects}</td>
                  <td>{student.study_hours_per_week.toFixed(1)}h</td>
                  <td>{student.prediction.dropout_probability.toFixed(1)}%</td>
                  <td>
                    <span 
                      className="risk-badge" 
                      style={{ backgroundColor: getRiskColor(student.prediction.risk_level) }}
                    >
                      {student.prediction.risk_level}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
