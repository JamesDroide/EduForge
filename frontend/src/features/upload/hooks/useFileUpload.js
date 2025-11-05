// src/features/upload/hooks/useFileUpload.js
/**
 * Hook personalizado para gestionar carga de archivos
 */
import { useState, useCallback } from 'react';
import { uploadService } from '../services/uploadService';
import { predictionService } from '../../predictions/services/predictionService';

export const useFileUpload = () => {
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [uploadResult, setUploadResult] = useState(null);

  /**
   * Sube y procesa un archivo CSV
   */
  const uploadAndPredict = useCallback(async (file) => {
    setUploading(true);
    setProcessing(false);
    setProgress(0);
    setError(null);
    setUploadResult(null);

    try {
      // Paso 1: Subir archivo (30%)
      console.log('📤 Subiendo archivo...');
      setProgress(30);
      const uploadResponse = await uploadService.uploadFile(file);

      if (!uploadResponse.success) {
        throw new Error(uploadResponse.message || 'Error al subir archivo');
      }

      setUploading(false);
      setProcessing(true);
      setProgress(50);

      // Paso 2: Realizar predicciones (70%)
      console.log('🔮 Realizando predicciones...');
      const predictResponse = await uploadService.predict(
        uploadResponse.filename,
        uploadResponse.upload_id
      );

      setProgress(90);

      // Paso 3: Guardar en cache (100%)
      if (predictResponse.predictions) {
        predictionService.saveToCache(predictResponse.predictions);
      }

      setProgress(100);
      setUploadResult({
        success: true,
        predictions: predictResponse.predictions,
        total: predictResponse.predictions?.length || 0,
        uploadId: uploadResponse.upload_id
      });

      return predictResponse;

    } catch (err) {
      console.error('❌ Error en upload:', err);
      setError(err.message || 'Error al procesar archivo');
      setUploadResult({
        success: false,
        error: err.message
      });
      throw err;
    } finally {
      setUploading(false);
      setProcessing(false);
    }
  }, []);

  /**
   * Limpia el estado
   */
  const reset = useCallback(() => {
    setUploading(false);
    setProcessing(false);
    setProgress(0);
    setError(null);
    setUploadResult(null);
  }, []);

  return {
    uploading,
    processing,
    progress,
    error,
    uploadResult,
    uploadAndPredict,
    reset,
    isProcessing: uploading || processing
  };
};

