// src/features/dashboard/services/dashboardService.js
/**
 * Servicio de API para dashboard
 */
import apiClient from '../../../shared/services/apiClient';
import { API_BASE_URL } from '../../../config/api';

export const dashboardService = {
  /**
   * Obtiene datos de asistencia para gráfico
   */
  async getAttendanceData() {
    const response = await apiClient.get('/dashboard_attendance/attendance_chart_real');
    return response.data;
  },

  /**
   * Obtiene resumen de riesgo
   */
  async getRiskSummary() {
    const response = await apiClient.get('/dashboard_risk/risk_summary');
    return response.data;
  },

  /**
   * Obtiene estudiantes en riesgo
   */
  async getStudentsAtRisk() {
    const response = await apiClient.get('/dashboard_risk/students_at_risk');
    return response.data;
  }
};

