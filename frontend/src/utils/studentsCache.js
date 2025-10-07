import React from "react";

// Cache global para datos de estudiantes
class StudentsCache {
  constructor() {
    this.cache = new Map();
    this.lastFetch = null;
    this.CACHE_DURATION = 30 * 1000; // 30 segundos
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

    console.log("🔄 Cargando datos del servidor...");
    try {
      const response = await fetch("http://localhost:8000/dashboard_risk/students_at_risk");

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
    }
  }

  // Procesar datos una sola vez
  processStudentData(rawData) {
    try {
      const storedPredictions = localStorage.getItem("latest_predictions");
      let parsedLocalData = [];

      if (storedPredictions) {
        parsedLocalData = JSON.parse(storedPredictions);
      }

      return rawData.map((student) => {
        let studentData = {
          id_estudiante: student.student_id,
          nombre: student.name,
          nota_final: parseFloat(student.nota || 0),
          asistencia: parseFloat(student.asistencia || 0),
          riesgo_desercion: student.risk_level || "Bajo",
          conducta: student.conducta || "Regular",
          fecha: new Date().toISOString().split("T")[0],
        };

        // Buscar datos completos en localStorage
        const fullStudentData = parsedLocalData.find(
          (p) =>
            (p.id_estudiante && p.id_estudiante.toString() === student.student_id.toString()) ||
            (p.nombre && p.nombre === student.name)
        );

        if (fullStudentData) {
          studentData = { ...fullStudentData };
        }

        return studentData;
      });
    } catch (e) {
      console.warn("Error procesando datos:", e);
      return rawData;
    }
  }

  // Invalidar cache cuando se sube nuevo CSV
  invalidate() {
    console.log("🗑️ Cache invalidado - próxima carga será fresca");
    this.cache.clear();
    this.lastFetch = null;
  }
}

// Instancia global del cache
export const studentsCache = new StudentsCache();

// Hook personalizado optimizado
export const useStudentsCache = () => {
  const [students, setStudents] = React.useState([]);
  const [loading, setLoading] = React.useState(false);
  const [hasValidData, setHasValidData] = React.useState(false);

  const loadStudents = React.useCallback(async (forceRefresh = false) => {
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

  React.useEffect(() => {
    loadStudents();

    const handleCsvUploaded = () => {
      console.log("🔄 Nuevo CSV detectado - invalidando cache");
      studentsCache.invalidate();
      setTimeout(() => loadStudents(true), 1000);
    };

    const handleStorageChange = (e) => {
      if (e.key === "csv_uploaded" || e.key === "latest_predictions") {
        studentsCache.invalidate();
        loadStudents(true);
        if (e.key === "csv_uploaded") {
          localStorage.removeItem("csv_uploaded");
        }
      }
    };

    window.addEventListener("csvUploaded", handleCsvUploaded);
    window.addEventListener("storage", handleStorageChange);

    return () => {
      window.removeEventListener("csvUploaded", handleCsvUploaded);
      window.removeEventListener("storage", handleStorageChange);
    };
  }, [loadStudents]);

  return { students, loading, hasValidData, refresh: () => loadStudents(true) };
};

export default studentsCache;
