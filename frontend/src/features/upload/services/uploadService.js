// src/features/upload/services/uploadService.js
/**
 * Servicio de API para carga de archivos
 */
import apiClient from '../../../shared/services/apiClient';
import { API_BASE_URL } from '../../../config/api';

export const uploadService = {
  /**
   * Sube un archivo CSV
   */
  async uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  },

  /**
   * Realiza predicciones sobre el archivo subido
   */
  async predict(filename, uploadId = null) {
    const response = await apiClient.post('/predict', null, {
      params: { filename, upload_id: uploadId }
    });
    return response.data;
  },

  /**
   * Obtiene el historial de cargas
   */
  async getHistory() {
    const response = await apiClient.get('/api/upload-history');
    return response.data;
  },

  /**
   * Compara dos uploads
   */
  async compareUploads(uploadId1, uploadId2) {
    const response = await apiClient.get('/api/upload-history/compare', {
      params: { upload1: uploadId1, upload2: uploadId2 }
    });
    return response.data;
  },

  /**
   * Elimina un upload
   */
  async deleteUpload(uploadId) {
    const response = await apiClient.delete(`/api/upload-history/${uploadId}`);
    return response.data;
  }
};

