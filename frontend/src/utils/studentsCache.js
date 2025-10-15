import { useState, useEffect } from "react";
import { API_ENDPOINTS } from "../config/api";

// Cache global para datos de estudiantes
class StudentsCache {
  constructor() {
    this.cache = new Map();
    this.lastFetch = null;
    this.CACHE_DURATION = 60 * 1000; // Aumentar a 60 segundos
    this.loading = false; // Evitar múltiples peticiones simultáneas
  }

  // Verificar si el cache es válido
  isValid() {
    return this.lastFetch && Date.now() - this.lastFetch < this.CACHE_DURATION;
  }

  // Obtener datos del cache o hacer fetch si es necesario
  async getStudents(forceRefresh = false) {
    if (!forceRefresh && this.isValid() && this.cache.has("students")) {
      console.log("📦 Usando datos del cache - RÁPIDO");
      return this.cache.get("students");
    }

    // Evitar múltiples peticiones simultáneas
    if (this.loading) {
      console.log("⏳ Esperando petición en curso...");
      return this.cache.get("students") || [];
    }

    console.log("🔄 Cargando datos del servidor...");
    this.loading = true;

    try {
      const response = await fetch(API_ENDPOINTS.STUDENTS_AT_RISK, {
        timeout: 10000, // 10 segundos de timeout
      });

      if (!response.ok) {
        throw new Error("No se pudieron cargar los estudiantes");
      }

      const data = await response.json();

      // Procesar los datos una sola vez
      const processedData = this.processStudentData(data);

      // Guardar en cache
      this.cache.set("students", processedData);
      this.lastFetch = Date.now();

      console.log(`✅ ${processedData.length} estudiantes cargados y guardados en cache`);
      return processedData;
    } catch (error) {
      console.error("❌ Error cargando estudiantes:", error);
      return this.cache.get("students") || [];
    } finally {
      this.loading = false;
    }
  }

  // Procesar datos una sola vez
  processStudentData(rawData) {
    if (!rawData || rawData.length === 0) {
      return [];
    }

    try {
      const storedPredictions = localStorage.getItem("latest_predictions");
      let fullDataMap = new Map();

      if (storedPredictions) {
        const parsedData = JSON.parse(storedPredictions);
        parsedData.forEach((student) => {
          const key = student.id_estudiante || student.student_id || student.nombre || student.name;
          if (key) fullDataMap.set(key.toString(), student);
        });
      }

      return rawData.map((student) => {
        // Buscar datos completos
        const fullData =
          fullDataMap.get(student.student_id?.toString()) || fullDataMap.get(student.name) || {};

        return {
          student_id: student.student_id,
          name: student.name,
          nota: parseFloat(fullData.nota_final || fullData.nota || student.nota || 0),
          asistencia: parseFloat(fullData.asistencia || student.asistencia || 0),
          risk_level: student.risk_level || fullData.riesgo_desercion || "Bajo",
          conducta: fullData.conducta || student.conducta || "Regular",
          ...student,
          ...fullData,
        };
      });
    } catch (error) {
      console.error("Error processing student data:", error);
      return rawData;
    }
  }

  // Invalidar cache
  invalidate() {
    this.cache.clear();
    this.lastFetch = null;
    this.loading = false;
    console.log("🗑️ Cache invalidado - próxima carga será fresca");
  }
}

// Instancia global del cache
const studentsCache = new StudentsCache();

// Hook personalizado para usar el cache
export const useStudentsCache = () => {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasValidData, setHasValidData] = useState(false);

  const fetchStudents = async (forceRefresh = false) => {
    setLoading(true);
    try {
      const data = await studentsCache.getStudents(forceRefresh);
      setStudents(data);
      setHasValidData(data.length > 0);
    } catch (error) {
      console.error("Error loading students:", error);
      setStudents([]);
      setHasValidData(false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStudents();

    // Escuchar cambios en localStorage
    const handleStorageChange = (e) => {
      if (e.key === "latest_predictions" || e.key === "csv_uploaded") {
        console.log("🔄 Detectado cambio en localStorage, invalidando caché...");
        studentsCache.invalidate();
        fetchStudents(true);
      }
    };

    // Escuchar eventos personalizados para invalidación inmediata
    const handleCsvUploaded = () => {
      console.log("🆕 Nuevo CSV detectado, actualizando datos...");
      studentsCache.invalidate();
      fetchStudents(true);
    };

    window.addEventListener("storage", handleStorageChange);
    window.addEventListener("csvUploaded", handleCsvUploaded);

    return () => {
      window.removeEventListener("storage", handleStorageChange);
      window.removeEventListener("csvUploaded", handleCsvUploaded);
    };
  }, []); // Sin dependencias ya que fetchStudents se define dentro del componente

  return {
    students,
    loading,
    hasValidData,
    refresh: () => {
      console.log("🔄 Refresh manual solicitado");
      studentsCache.invalidate();
      fetchStudents(true);
    },
  };
};

export default studentsCache;
