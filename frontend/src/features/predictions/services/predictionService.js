// src/features/predictions/services/predictionService.js
/**
 * Servicio de API para predicciones
 */
import apiClient from '../../../shared/services/apiClient';

export const predictionService = {
  /**
   * Obtiene todas las predicciones
   */
  async getAll() {
    const response = await apiClient.get('/predictions/');
    return response.data;
  },

  /**
   * Obtiene predicciones por nivel de riesgo
   */
  async getByRiskLevel(riskLevel) {
    const response = await apiClient.get(`/predictions/risk/${riskLevel}`);
    return response.data;
  },

  /**
   * Obtiene predicciones de un estudiante específico
   */
  async getByStudentId(studentId) {
    const response = await apiClient.get(`/predictions/student/${studentId}`);
    return response.data;
  },

  /**
   * Realiza predicciones desde un archivo CSV
   */
  async predictFromFile(filename) {
    const response = await apiClient.post('/predictions/predict', null, {
      params: { filename }
    });
    return response.data;
  },

  /**
   * Obtiene predicciones desde cache local (compatibilidad)
   */
  getFromCache() {
    const cached = localStorage.getItem('latest_predictions');
    return cached ? JSON.parse(cached) : [];
  },

  /**
   * Guarda predicciones en cache local
   */
  saveToCache(predictions) {
    localStorage.setItem('latest_predictions', JSON.stringify(predictions));
    localStorage.setItem('csv_upload_timestamp', Date.now().toString());
    window.dispatchEvent(new Event('csvUploaded'));
  },

  /**
   * Limpia cache de predicciones
   */
  clearCache() {
    localStorage.removeItem('latest_predictions');
    localStorage.removeItem('csv_upload_timestamp');
  }
};

