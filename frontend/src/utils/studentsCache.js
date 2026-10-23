import { useState, useEffect, useCallback } from "react";
import { API_ENDPOINTS } from "../config/api";

// Cache global para datos de estudiantes
class StudentsCache {
  constructor() {
    this.cache = new Map();
    this.lastFetch = null;
    this.CACHE_DURATION = 60 * 1000;
    this.loading = false;
    this.pendingPromise = null;
  }

  // Verificar si el cache es valido
  isValid() {
    return this.lastFetch && Date.now() - this.lastFetch < this.CACHE_DURATION;
  }

  // Obtener datos del cache o hacer fetch si es necesario
  async getStudents(forceRefresh = false) {
    if (!forceRefresh && this.isValid() && this.cache.has("students")) {
      return this.cache.get("students");
    }

    if (!forceRefresh && this.pendingPromise) {
      return await this.pendingPromise;
    }

    this.loading = true;
    this.pendingPromise = (async () => {
      try {
        const response = await fetch(API_ENDPOINTS.STUDENTS_AT_RISK, {
          timeout: 10000,
        });

        if (!response.ok) {
          throw new Error("No se pudieron cargar los estudiantes");
        }

        const data = await response.json();
        const processedData = this.processStudentData(data);

        this.cache.set("students", processedData);
        this.lastFetch = Date.now();

        return processedData;
      } catch (error) {
        console.error("Error cargando estudiantes:", error);
        return this.cache.get("students") || [];
      } finally {
        this.loading = false;
        this.pendingPromise = null;
      }
    })();

    return await this.pendingPromise;
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
          riesgo_desercion:
            student.riesgo_desercion || student.risk_level || fullData.riesgo_desercion || "Bajo",
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
    this.pendingPromise = null;
  }
}

// Instancia global del cache
const studentsCache = new StudentsCache();

// Hook personalizado para usar el cache
export const useStudentsCache = () => {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [hasValidData, setHasValidData] = useState(false);

  const fetchStudents = useCallback(async (forceRefresh = false) => {
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
  }, []);

  const refresh = useCallback(() => {
    studentsCache.invalidate();
    fetchStudents(true);
  }, [fetchStudents]);

  useEffect(() => {
    fetchStudents();

    const handleStorageChange = (e) => {
      if (e.key === "latest_predictions" || (e.key === "csv_uploaded" && e.newValue)) {
        studentsCache.invalidate();
        fetchStudents(true);
      }
    };

    const handleCsvUploaded = () => {
      studentsCache.invalidate();
      fetchStudents(true);
    };

    window.addEventListener("storage", handleStorageChange);
    window.addEventListener("csvUploaded", handleCsvUploaded);

    return () => {
      window.removeEventListener("storage", handleStorageChange);
      window.removeEventListener("csvUploaded", handleCsvUploaded);
    };
  }, [fetchStudents]);

  return {
    students,
    loading,
    hasValidData,
    refresh,
  };
};

export default studentsCache;
