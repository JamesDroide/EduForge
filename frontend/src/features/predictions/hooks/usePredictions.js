// src/features/predictions/hooks/usePredictions.js
/**
 * Hook personalizado para gestionar predicciones
 */
import { useState, useEffect, useCallback } from 'react';
import { predictionService } from '../services/predictionService';

export const usePredictions = () => {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Carga todas las predicciones
   */
  const loadPredictions = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      // Intentar obtener desde cache primero
      const cached = predictionService.getFromCache();
      if (cached.length > 0) {
        setPredictions(cached);
        setLoading(false);
        return cached;
      }

      // Si no hay cache, obtener desde API
      const data = await predictionService.getAll();
      setPredictions(data);
      predictionService.saveToCache(data);
      return data;
    } catch (err) {
      setError(err.message || 'Error cargando predicciones');
      console.error('Error loading predictions:', err);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Filtra predicciones por nivel de riesgo
   */
  const filterByRisk = useCallback((riskLevel) => {
    if (!riskLevel || riskLevel === 'Todos') {
      return predictions;
    }
    return predictions.filter(p => p.riesgo_desercion === riskLevel);
  }, [predictions]);

  /**
   * Busca un estudiante por ID
   */
  const findStudent = useCallback((studentId) => {
    return predictions.find(p =>
      p.id_estudiante === studentId ||
      p.ID === studentId
    );
  }, [predictions]);

  /**
   * Obtiene estadísticas de predicciones
   */
  const getStats = useCallback(() => {
    const total = predictions.length;
    const highRisk = predictions.filter(p => p.riesgo_desercion === 'Alto').length;
    const mediumRisk = predictions.filter(p => p.riesgo_desercion === 'Medio').length;
    const lowRisk = predictions.filter(p => p.riesgo_desercion === 'Bajo').length;

    return {
      total,
      highRisk,
      mediumRisk,
      lowRisk,
      highRiskPercentage: total > 0 ? (highRisk / total) * 100 : 0
    };
  }, [predictions]);

  // Cargar predicciones al montar el componente
  useEffect(() => {
    loadPredictions();
  }, [loadPredictions]);

  // Escuchar eventos de nuevo CSV cargado
  useEffect(() => {
    const handleCsvUploaded = () => {
      console.log('📄 Nuevo CSV detectado, recargando predicciones...');
      loadPredictions();
    };

    window.addEventListener('csvUploaded', handleCsvUploaded);
    return () => window.removeEventListener('csvUploaded', handleCsvUploaded);
  }, [loadPredictions]);

  return {
    predictions,
    loading,
    error,
    loadPredictions,
    filterByRisk,
    findStudent,
    getStats,
    hasData: predictions.length > 0
  };
};

