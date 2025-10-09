// Configuración de API para diferentes entornos
const getApiUrl = () => {
  // En producción, usar la variable de entorno
  let apiUrl = process.env.REACT_APP_API_URL || "https://eduforge-production.up.railway.app";

  // Eliminar barra extra al final (si existe)
  if (apiUrl.endsWith("/")) {
    apiUrl = apiUrl.slice(0, -1);
  }

  // Si es desarrollo, usar localhost
  if (process.env.NODE_ENV !== "production") {
    return "http://localhost:8000"; // Para desarrollo local
  }

  return apiUrl;
};

export const API_BASE_URL = getApiUrl();

// Endpoints específicos
export const API_ENDPOINTS = {
  // Dashboard endpoints
  STUDENTS_AT_RISK: `${API_BASE_URL}/dashboard_risk/students_at_risk`,
  RISK_SUMMARY: `${API_BASE_URL}/dashboard_risk/risk_summary`,
  ATTENDANCE_CHART: `${API_BASE_URL}/dashboard_attendance/attendance_chart_real`,

  // Upload endpoints
  UPLOAD: `${API_BASE_URL}/upload`,
  PREDICT: `${API_BASE_URL}/predict`,

  // General endpoints
  DASHBOARD_STATUS: `${API_BASE_URL}/dashboard-status`,
  CLEAR_DASHBOARD: `${API_BASE_URL}/clear-dashboard`,
};

export default API_BASE_URL;
