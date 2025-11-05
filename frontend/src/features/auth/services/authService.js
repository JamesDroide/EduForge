// src/features/auth/services/authService.js
/**
 * Servicio de API para autenticación con Clean Architecture
 */
import apiClient from '../../../shared/services/apiClient';

export const authService = {
  /**
   * Inicia sesión
   */
  async login(username, password) {
    const response = await apiClient.post('/auth-v2/login', {
      username,
      password
    });
    
    const { access_token, user } = response.data;
    
    // Guardar en localStorage
    localStorage.setItem('token', access_token);
    localStorage.setItem('user', JSON.stringify(user));
    
    return { token: access_token, user };
  },

  /**
   * Registra un nuevo usuario
   */
  async register(userData) {
    const response = await apiClient.post('/auth-v2/register', userData);
    return response.data;
  },

  /**
   * Cierra sesión
   */
  logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    localStorage.removeItem('latest_predictions');
  },

  /**
   * Obtiene el usuario actual desde localStorage
   */
  getCurrentUser() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  /**
   * Verifica si el usuario está autenticado
   */
  isAuthenticated() {
    return !!localStorage.getItem('token');
  },

  /**
   * Obtiene el token actual
   */
  getToken() {
    return localStorage.getItem('token');
  }
};
// src/shared/services/apiClient.js
/**
 * Cliente API centralizado con configuración de axios
 */
import axios from 'axios';
import { API_BASE_URL } from '../../config/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token de autenticación
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para manejar errores globales
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/authentication/sign-in';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
