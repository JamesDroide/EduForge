import axios from "axios";

// Configuración de API para diferentes entornos
const getApiUrl = () => {
  // Prioridad 1: Variable de entorno REACT_APP_API_URL (si existe)
  if (process.env.REACT_APP_API_URL) {
    let apiUrl = process.env.REACT_APP_API_URL;

    // Eliminar barra extra al final (si existe)
    if (apiUrl.endsWith("/")) {
      apiUrl = apiUrl.slice(0, -1);
    }

    console.log(`🌐 API URL configurada desde .env: ${apiUrl}`);
    return apiUrl;
  }

  // Prioridad 2: Detectar entorno de Node
  if (process.env.NODE_ENV === "development") {
    console.log("🔧 Modo desarrollo: usando localhost:8000");
    return "http://localhost:8000";
  }

  // Prioridad 3: Fallback para producción
  const productionUrl = "https://eduforge-production.up.railway.app";
  console.log(`🚀 Modo producción: usando ${productionUrl}`);
  return productionUrl;
};

export const API_BASE_URL = getApiUrl();

// Log para debugging (solo en desarrollo)
if (process.env.NODE_ENV === "development") {
  console.log("📡 Configuración API:", {
    baseURL: API_BASE_URL,
    environment: process.env.NODE_ENV,
    fromEnv: !!process.env.REACT_APP_API_URL,
  });
}

// Crear instancia de axios configurada
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor para agregar el token de autenticación
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar respuestas
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token inválido o expirado
      localStorage.removeItem("token");
      window.location.href = "/authentication/sign-in";
    }
    return Promise.reject(error);
  }
);

// Endpoints específicos
export const API_ENDPOINTS = {
  // Auth endpoints
  LOGIN: `${API_BASE_URL}/auth/login`,
  REGISTER: `${API_BASE_URL}/auth/register`,
  ME: `${API_BASE_URL}/auth/me`,
  CHANGE_PASSWORD: `${API_BASE_URL}/auth/change-password`,
  LOGOUT: `${API_BASE_URL}/auth/logout`,
  USERS: `${API_BASE_URL}/auth/users`,

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

export default api;
