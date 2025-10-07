import { useState } from 'react'
import axios from 'axios'
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer } from 'recharts'
import './StudentAnalysis.css'

const API_URL = 'http://localhost:8000'

const StudentAnalysis = () => {
  const [studentId, setStudentId] = useState('')
  const [formData, setFormData] = useState({
    attendance_rate: 85,
    average_grade: 7.5,
    study_hours_per_week: 15,
    family_income: 2500,
    parent_education_level: 3,
    extracurricular_activities: 2,
    failed_subjects: 0,
    age: 18
  })
  const [analysis, setAnalysis] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: parseFloat(value) || 0
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const id = studentId || `EST-${Date.now().toString().slice(-6)}`
      const response = await axios.post(`${API_URL}/analyze?student_id=${id}`, formData)
      setAnalysis(response.data)
    } catch (err) {
      setError('Error al analizar el estudiante. Verifica que el servidor esté ejecutándose.')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const getRadarData = () => {
    if (!analysis) return []
    
    const data = analysis.student_data
    return [
      { subject: 'Asistencia', value: (data.attendance_rate / 100) * 100, fullMark: 100 },
      { subject: 'Promedio', value: (data.average_grade / 10) * 100, fullMark: 100 },
      { subject: 'Hrs Estudio', value: (data.study_hours_per_week / 30) * 100, fullMark: 100 },
      { subject: 'Ed. Padres', value: (data.parent_education_level / 5) * 100, fullMark: 100 },
      { subject: 'Actividades', value: (data.extracurricular_activities / 5) * 100, fullMark: 100 },
      { subject: 'Sin Reprobadas', value: Math.max(0, (5 - data.failed_subjects) / 5) * 100, fullMark: 100 }
    ]
  }

  const getRiskColor = (risk) => {
    switch (risk) {
      case 'Bajo': return '#10b981'
      case 'Medio': return '#f59e0b'
      case 'Alto': return '#ef4444'
      default: return '#6b7280'
    }
  }

  return (
    <div className="student-analysis">
      <div className="analysis-header">
        <h2>Análisis Individual de Estudiante</h2>
        <p>Ingresa los datos del estudiante para obtener una predicción detallada</p>
      </div>

      <div className="analysis-content">
        <form onSubmit={handleSubmit} className="analysis-form">
          <div className="form-section">
            <h3>📋 Información del Estudiante</h3>
            <div className="form-group">
              <label>ID del Estudiante (opcional)</label>
              <input
                type="text"
                value={studentId}
                onChange={(e) => setStudentId(e.target.value)}
                placeholder="EST-001"
              />
            </div>
            <div className="form-group">
              <label>Edad</label>
              <input
                type="number"
                name="age"
                value={formData.age}
                onChange={handleInputChange}
                min="15"
                max="30"
                required
              />
            </div>
          </div>

          <div className="form-section">
            <h3>📚 Rendimiento Académico</h3>
            <div className="form-group">
              <label>Tasa de Asistencia (%)</label>
              <input
                type="number"
                name="attendance_rate"
                value={formData.attendance_rate}
                onChange={handleInputChange}
                min="0"
                max="100"
                step="0.1"
                required
              />
              <span className="input-help">{formData.attendance_rate}%</span>
            </div>
            <div className="form-group">
              <label>Promedio de Calificaciones (0-10)</label>
              <input
                type="number"
                name="average_grade"
                value={formData.average_grade}
                onChange={handleInputChange}
                min="0"
                max="10"
                step="0.1"
                required
              />
              <span className="input-help">{formData.average_grade}/10</span>
            </div>
            <div className="form-group">
              <label>Materias Reprobadas</label>
              <input
                type="number"
                name="failed_subjects"
                value={formData.failed_subjects}
                onChange={handleInputChange}
                min="0"
                required
              />
            </div>
          </div>

          <div className="form-section">
            <h3>⏰ Hábitos de Estudio</h3>
            <div className="form-group">
              <label>Horas de Estudio por Semana</label>
              <input
                type="number"
                name="study_hours_per_week"
                value={formData.study_hours_per_week}
                onChange={handleInputChange}
                min="0"
                max="168"
                step="0.5"
                required
              />
              <span className="input-help">{formData.study_hours_per_week} horas</span>
            </div>
            <div className="form-group">
              <label>Actividades Extracurriculares</label>
              <input
                type="number"
                name="extracurricular_activities"
                value={formData.extracurricular_activities}
                onChange={handleInputChange}
                min="0"
                max="10"
                required
              />
            </div>
          </div>

          <div className="form-section">
            <h3>👨‍👩‍👧 Contexto Socioeconómico</h3>
            <div className="form-group">
              <label>Ingreso Familiar Mensual ($)</label>
              <input
                type="number"
                name="family_income"
                value={formData.family_income}
                onChange={handleInputChange}
                min="0"
                step="100"
                required
              />
              <span className="input-help">${formData.family_income}</span>
            </div>
            <div className="form-group">
              <label>Nivel Educativo de Padres (1-5)</label>
              <select
                name="parent_education_level"
                value={formData.parent_education_level}
                onChange={handleInputChange}
                required
              >
                <option value="1">1 - Primaria</option>
                <option value="2">2 - Secundaria</option>
                <option value="3">3 - Preparatoria</option>
                <option value="4">4 - Universidad</option>
                <option value="5">5 - Posgrado</option>
              </select>
            </div>
          </div>

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? '⏳ Analizando...' : '🔍 Analizar Estudiante'}
          </button>
        </form>

        {error && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}

        {analysis && (
          <div className="analysis-results">
            <div className="result-header">
              <h3>Resultados del Análisis - {analysis.student_id}</h3>
            </div>

            <div className="prediction-card">
              <div className="prediction-main">
                <div className="probability-circle" style={{ 
                  borderColor: getRiskColor(analysis.prediction.risk_level) 
                }}>
                  <span className="probability-value">
                    {analysis.prediction.dropout_probability.toFixed(1)}%
                  </span>
                  <span className="probability-label">Probabilidad de Deserción</span>
                </div>
                <div className="risk-info">
                  <h4>Nivel de Riesgo</h4>
                  <span 
                    className="risk-badge large"
                    style={{ backgroundColor: getRiskColor(analysis.prediction.risk_level) }}
                  >
                    {analysis.prediction.risk_level}
                  </span>
                </div>
              </div>
            </div>

            <div className="factors-grid">
              <div className="factor-card">
                <h4>📊 Rendimiento Académico</h4>
                <p className="factor-status">{analysis.factors_analysis.academic_performance.status}</p>
                <ul>
                  <li>Promedio: {analysis.factors_analysis.academic_performance.average_grade.toFixed(1)}</li>
                  <li>Materias reprobadas: {analysis.factors_analysis.academic_performance.failed_subjects}</li>
                </ul>
              </div>

              <div className="factor-card">
                <h4>📅 Asistencia</h4>
                <p className="factor-status">{analysis.factors_analysis.attendance.status}</p>
                <ul>
                  <li>Tasa: {analysis.factors_analysis.attendance.rate.toFixed(1)}%</li>
                </ul>
              </div>

              <div className="factor-card">
                <h4>📖 Hábitos de Estudio</h4>
                <p className="factor-status">{analysis.factors_analysis.study_habits.status}</p>
                <ul>
                  <li>Horas semanales: {analysis.factors_analysis.study_habits.hours_per_week.toFixed(1)}</li>
                </ul>
              </div>

              <div className="factor-card">
                <h4>🏠 Contexto Socioeconómico</h4>
                <p className="factor-status">{analysis.factors_analysis.socioeconomic_factors.status}</p>
                <ul>
                  <li>Ingreso familiar: ${analysis.factors_analysis.socioeconomic_factors.family_income.toFixed(0)}</li>
                  <li>Nivel educativo padres: {analysis.factors_analysis.socioeconomic_factors.parent_education_level}</li>
                </ul>
              </div>

              <div className="factor-card">
                <h4>🎯 Participación</h4>
                <p className="factor-status">{analysis.factors_analysis.engagement.status}</p>
                <ul>
                  <li>Actividades extracurriculares: {analysis.factors_analysis.engagement.extracurricular_activities}</li>
                </ul>
              </div>
            </div>

            <div className="radar-chart-card">
              <h4>Perfil del Estudiante</h4>
              <ResponsiveContainer width="100%" height={400}>
                <RadarChart data={getRadarData()}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="subject" />
                  <PolarRadiusAxis angle={90} domain={[0, 100]} />
                  <Radar name="Estudiante" dataKey="value" stroke="#667eea" fill="#667eea" fillOpacity={0.6} />
                </RadarChart>
              </ResponsiveContainer>
            </div>

            <div className="recommendations-card">
              <h4>💡 Recomendaciones</h4>
              <ul className="recommendations-list">
                {analysis.prediction.recommendations.map((rec, index) => (
                  <li key={index}>{rec}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default StudentAnalysis
