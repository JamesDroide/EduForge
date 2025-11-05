/**
=========================================================
* Material Dashboard 2 React - Análisis Individual
=========================================================
*/

import React, { useState, useEffect, useCallback, useMemo } from "react";
import { useLocation, useNavigate, useSearchParams } from "react-router-dom";

// @mui material components
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import Autocomplete from "@mui/material/Autocomplete";
import TextField from "@mui/material/TextField";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDButton from "components/MDButton";
import MDAvatar from "components/MDAvatar";
import MDAlert from "components/MDAlert";

// Material Dashboard 2 React example components
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";

// Imagen por defecto para estudiantes
import defaultStudentImage from "assets/images/Estudiante.jpg";

import { API_ENDPOINTS } from "../../config/api";

function IndividualAnalysis() {
  const location = useLocation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [students, setStudents] = useState([]);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [studentData, setStudentData] = useState(null);
  const [error, setError] = useState(null);
  const [riskFilter, setRiskFilter] = useState("Todos");
  const [searchText, setSearchText] = useState(""); // Para controlar el input
  const [hasValidData, setHasValidData] = useState(false);

  // Cargar lista de estudiantes al montar el componente
  useEffect(() => {
    fetchStudents();

    // Función para escuchar cuando se sube un nuevo CSV (como en reporte general)
    const handleCsvUploaded = () => {
      console.log("🔄 CSV cargado, actualizando estudiantes en análisis individual...");
      setTimeout(() => {
        fetchStudents();
      }, 1000);
    };

    // Función para escuchar cambios en localStorage
    const handleStorageChange = (e) => {
      if (e.key === "csv_uploaded" || e.key === "latest_predictions") {
        console.log("🔄 Nuevos datos detectados, actualizando estudiantes...");
        fetchStudents();
        if (e.key === "csv_uploaded") {
          localStorage.removeItem("csv_uploaded");
        }
      }
    };

    // Escuchar eventos de CSV cargado
    window.addEventListener("csvUploaded", handleCsvUploaded);
    window.addEventListener("storage", handleStorageChange);

    return () => {
      window.removeEventListener("csvUploaded", handleCsvUploaded);
      window.removeEventListener("storage", handleStorageChange);
    };
  }, []); // Solo ejecutar una vez al montar

  // Función separada para verificar estudiantes preseleccionados
  const checkPreselectedStudent = useCallback(() => {
    // Primero verificar desde URL parameters (desde Resultados Completos)
    const studentIdFromUrl = searchParams.get("studentId");
    if (studentIdFromUrl && students.length > 0) {
      const studentFromUrl = students.find(
        (s) =>
          s.student_id?.toString() === studentIdFromUrl ||
          s.id_estudiante?.toString() === studentIdFromUrl ||
          s.ID?.toString() === studentIdFromUrl
      );

      if (studentFromUrl) {
        console.log("📊 Estudiante encontrado desde URL:", studentFromUrl);
        setSelectedStudent(studentFromUrl);
        processStudentData(studentFromUrl);
        return;
      }
    }

    // Segundo: verificar desde state (navegación directa)
    if (location.state?.preselectedStudent) {
      const student = location.state.preselectedStudent;
      console.log("📊 Estudiante preseleccionado desde state:", student);
      setSelectedStudent(student);
      processStudentData(student);
      return;
    }

    // Tercero: verificar desde localStorage (respaldo)
    const storedStudent = localStorage.getItem("selected_student_for_analysis");
    if (storedStudent) {
      try {
        const student = JSON.parse(storedStudent);
        console.log("📊 Estudiante preseleccionado desde localStorage:", student);
        setSelectedStudent(student);
        processStudentData(student);
        // Limpiar el localStorage después de usar
        localStorage.removeItem("selected_student_for_analysis");
      } catch (e) {
        console.error("Error parsing preselected student:", e);
      }
    }
  }, [students, searchParams, location.state]);

  // Efecto separado para verificar estudiante preseleccionado
  useEffect(() => {
    if (students.length > 0) {
      checkPreselectedStudent();
    }
  }, [students.length, checkPreselectedStudent]);

  // Función para procesar los datos del estudiante (separada de handleStudentSelect)
  const processStudentData = (student) => {
    setError(null);

    try {
      // Usar datos reales del estudiante seleccionado
      const realStudentData = {
        ...student,
        factoresRiesgo: [
          {
            factor: "Asistencia",
            impacto: student.asistencia < 70 ? "Alto" : student.asistencia < 85 ? "Medio" : "Bajo",
            valor: `${student.asistencia}%`,
            descripcion:
              student.asistencia < 70
                ? "Asistencia crítica - requiere intervención"
                : student.asistencia < 85
                ? "Asistencia irregular - monitoreo necesario"
                : "Asistencia excelente",
          },
          {
            factor: "Notas",
            impacto: student.nota < 11 ? "Alto" : student.nota < 14 ? "Medio" : "Bajo",
            valor: `${student.nota}/20`,
            descripcion:
              student.nota < 11
                ? "Rendimiento deficiente - apoyo urgente"
                : student.nota < 14
                ? "Rendimiento regular - refuerzo necesario"
                : "Rendimiento satisfactorio",
          },
          {
            factor: "Conducta",
            impacto:
              student.conducta === "Mala"
                ? "Alto"
                : student.conducta === "Regular"
                ? "Medio"
                : "Bajo",
            valor: student.conducta || "Regular",
            descripcion:
              student.conducta === "Mala"
                ? "Problemas disciplinarios frecuentes"
                : student.conducta === "Regular"
                ? "Conducta aceptable con mejoras posibles"
                : "Excelente comportamiento",
          },
        ],
      };

      setStudentData(realStudentData);
      console.log("✅ Datos del estudiante procesados:", realStudentData);
    } catch (err) {
      console.error("Error procesando datos del estudiante:", err);
      setError("Error cargando datos del estudiante");
    }
  };

  const fetchStudents = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.STUDENTS_AT_RISK);

      if (!response.ok) {
        throw new Error("No se pudieron cargar los estudiantes");
      }

      const data = await response.json();

      if (data.length > 0) {
        console.log("📊 Datos RAW desde backend (primeros 3 estudiantes):", data.slice(0, 3));

        // Procesar los datos de forma más directa
        const formattedStudents = data.map((student) => {
          console.log(`🔍 Procesando estudiante: ${student.name}`, student);

          // Extraer y convertir los valores correctamente
          let nota = 0;
          let asistencia = 0;
          let conducta = "Regular";

          // Buscar primero en localStorage para datos completos
          try {
            const storedPredictions = localStorage.getItem("latest_predictions");
            if (storedPredictions) {
              const parsedData = JSON.parse(storedPredictions);
              const fullStudentData = parsedData.find(
                (p) =>
                  (p.id_estudiante &&
                    p.id_estudiante.toString() === student.student_id.toString()) ||
                  (p.nombre && p.nombre === student.name)
              );

              if (fullStudentData) {
                console.log(
                  `✅ Datos completos encontrados en localStorage para ${student.name}:`,
                  fullStudentData
                );
                nota = parseFloat(fullStudentData.nota_final || fullStudentData.nota || 0);
                asistencia = parseFloat(fullStudentData.asistencia || 0);
                conducta = fullStudentData.conducta || "Regular";
              }
            }
          } catch (e) {
            console.warn("Error accediendo localStorage:", e);
          }

          // Si no se encontraron datos en localStorage, usar datos del backend
          if (nota === 0 && asistencia === 0) {
            console.log(`⚠️ Usando datos del backend para ${student.name}`);
            // Convertir string a números si es necesario
            nota = parseFloat(student.nota || student.nota_final || 0);
            asistencia = parseFloat(student.asistencia || 0);
            conducta = student.conducta || "Regular";
          }

          console.log(`📝 Valores finales para ${student.name}:`, { nota, asistencia, conducta });

          return {
            student_id: student.student_id,
            name: student.name,
            nota: nota,
            asistencia: asistencia,
            risk_level: student.risk_level || "Bajo",
            conducta: conducta,
            ...student,
          };
        });

        setStudents(formattedStudents);
        setHasValidData(true);
        console.log("✅ Estudiantes formateados finales:", formattedStudents.slice(0, 2));
      } else {
        console.log("📭 No hay datos en el backend, mostrando estado vacío");
        setStudents([]);
        setHasValidData(false);
      }
    } catch (err) {
      console.error("Error cargando estudiantes:", err);
      setStudents([]);
      setHasValidData(false);
    }
  };

  const handleStudentSelect = async (event, student) => {
    if (!student) return;

    setSelectedStudent(student);
    setError(null);

    try {
      // Extraer datos con múltiples posibles nombres de campos
      const nota = student.nota || student.nota_final || 0;
      const asistencia = student.asistencia || 0;
      const conducta = student.conducta || "Regular";

      console.log("📊 Datos del estudiante seleccionado:", {
        nota,
        asistencia,
        conducta,
        originalStudent: student,
      });

      // Usar datos reales del estudiante seleccionado (del CSV cargado)
      const realStudentData = {
        ...student,
        nota: nota, // Asegurar que nota esté disponible
        asistencia: asistencia, // Asegurar que asistencia esté disponible
        conducta: conducta, // Asegurar que conducta esté disponible
        // Usar datos reales en lugar de simulados
        factoresRiesgo: [
          {
            factor: "Asistencia",
            impacto: asistencia < 70 ? "Alto" : asistencia < 85 ? "Medio" : "Bajo",
            valor: `${asistencia}%`,
            descripcion:
              asistencia < 70
                ? "Asistencia crítica - requiere intervención"
                : asistencia < 85
                ? "Asistencia irregular - monitoreo necesario"
                : "Asistencia excelente",
          },
          {
            factor: "Notas",
            impacto: nota < 11 ? "Alto" : nota < 14 ? "Medio" : "Bajo",
            valor: `${nota}/20`,
            descripcion:
              nota < 11
                ? "Rendimiento deficiente - apoyo urgente"
                : nota < 14
                ? "Rendimiento regular - refuerzo necesario"
                : "Rendimiento satisfactorio",
          },
          {
            factor: "Conducta",
            impacto: conducta === "Mala" ? "Alto" : conducta === "Regular" ? "Medio" : "Bajo",
            valor: conducta || "Regular",
            descripcion:
              conducta === "Mala"
                ? "Problemas disciplinarios frecuentes"
                : conducta === "Regular"
                ? "Conducta aceptable con mejoras posibles"
                : "Excelente comportamiento",
          },
        ],
      };

      setStudentData(realStudentData);
      console.log("✅ Datos del estudiante procesados:", realStudentData);
    } catch (err) {
      console.error("Error procesando datos del estudiante:", err);
      setError("Error cargando datos del estudiante");
    }
  };

  const getRiskColor = (riskLevel) => {
    switch (riskLevel) {
      case "Alto":
        return "error";
      case "Medio":
        return "warning";
      case "Bajo":
        return "success";
      default:
        return "info";
    }
  };

  const getRandomImage = (studentId) => {
    return defaultStudentImage;
  };

  // Filtrado memoizado que se recalcula cuando cambian students, riskFilter o searchText
  const filteredAndSearchedStudents = useMemo(() => {
    console.log("🔍 Recalculando filtrado con:", {
      riskFilter,
      searchText,
      totalStudents: students.length,
    });

    // Primero filtrar por riesgo
    let filtered = students.filter((student) => {
      return riskFilter === "Todos" || student.risk_level === riskFilter;
    });

    // Luego filtrar por texto de búsqueda si hay texto
    if (searchText && searchText.trim().length > 0) {
      const searchValue = searchText.toLowerCase().trim();
      filtered = filtered.filter((student) => {
        const nameMatch = student.name.toLowerCase().includes(searchValue);
        const idMatch = student.student_id?.toString().includes(searchValue);
        return nameMatch || idMatch;
      });
      console.log(`📝 Filtrado por "${searchText}": ${filtered.length} resultados`);
    }

    return filtered;
  }, [students, riskFilter, searchText]);

  // Función para manejar el cambio en el input del Autocomplete
  const handleInputChange = useCallback((event, newInputValue, reason) => {
    console.log("🎯 Input change:", { newInputValue, reason });

    // Solo actualizar si el cambio es por typing del usuario
    if (reason === "input") {
      setSearchText(newInputValue || "");
    }

    // Si se limpia el input, también limpiar nuestro estado
    if (reason === "clear") {
      setSearchText("");
    }
  }, []);

  // Función para limpiar la búsqueda cuando cambie el filtro de riesgo
  const handleRiskFilterChange = useCallback((newFilter) => {
    console.log("🔄 Cambiando filtro de riesgo:", newFilter);
    setRiskFilter(newFilter);
    setSearchText(""); // Limpiar búsqueda al cambiar filtro
  }, []);

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox py={3}>
        {/* Mostrar vista vacía si no hay datos válidos */}
        {!hasValidData ? (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Card>
                <MDBox p={5} textAlign="center">
                  <MDTypography variant="h3" color="text" mb={3}>
                    📋 No hay datos disponibles
                  </MDTypography>
                  <MDTypography variant="h6" color="text" mb={2}>
                    Para usar el análisis individual, necesitas cargar un archivo CSV primero
                  </MDTypography>
                  <MDTypography variant="body1" color="text" mb={4}>
                    Ve a la sección &quot;Cargar Datos&quot; para subir un archivo CSV con
                    información de estudiantes
                  </MDTypography>
                  <MDButton
                    variant="contained"
                    color="primary"
                    onClick={() => navigate("/subir-archivos")}
                  >
                    Ir a Cargar Datos
                  </MDButton>
                </MDBox>
              </Card>
            </Grid>
          </Grid>
        ) : (
          // Vista normal con datos
          <Grid container spacing={3}>
            {/* Buscador de estudiantes */}
            <Grid item xs={12}>
              <Card>
                <MDBox p={3}>
                  <MDTypography variant="h5" mb={2}>
                    Análisis Individual de Estudiantes
                  </MDTypography>
                  <MDTypography variant="body2" color="text" mb={3}>
                    Busca y selecciona un estudiante para ver su análisis detallado
                  </MDTypography>

                  {/* Filtros por nivel de riesgo */}
                  <MDBox mb={3}>
                    <MDTypography variant="button" fontWeight="bold" mb={2} display="block">
                      Filtrar por nivel de riesgo:
                    </MDTypography>
                    <Grid container spacing={2}>
                      <Grid item>
                        <MDButton
                          variant={riskFilter === "Todos" ? "contained" : "outlined"}
                          color="primary"
                          size="small"
                          onClick={() => handleRiskFilterChange("Todos")}
                        >
                          Todos ({students.length})
                        </MDButton>
                      </Grid>
                      <Grid item>
                        <MDButton
                          variant={riskFilter === "Alto" ? "contained" : "outlined"}
                          color="error"
                          size="small"
                          onClick={() => handleRiskFilterChange("Alto")}
                        >
                          Alto Riesgo ({students.filter((s) => s.risk_level === "Alto").length})
                        </MDButton>
                      </Grid>
                      <Grid item>
                        <MDButton
                          variant={riskFilter === "Medio" ? "contained" : "outlined"}
                          color="warning"
                          size="small"
                          onClick={() => handleRiskFilterChange("Medio")}
                        >
                          Medio Riesgo ({students.filter((s) => s.risk_level === "Medio").length})
                        </MDButton>
                      </Grid>
                      <Grid item>
                        <MDButton
                          variant={riskFilter === "Bajo" ? "contained" : "outlined"}
                          color="success"
                          size="small"
                          onClick={() => handleRiskFilterChange("Bajo")}
                        >
                          Bajo Riesgo ({students.filter((s) => s.risk_level === "Bajo").length})
                        </MDButton>
                      </Grid>
                    </Grid>
                  </MDBox>

                  <Autocomplete
                    key={`${riskFilter}-${students.length}`} // Forzar re-render cuando cambien los datos
                    options={filteredAndSearchedStudents}
                    getOptionLabel={(option) => `${option.name} (ID: ${option.student_id})`}
                    onChange={handleStudentSelect}
                    onInputChange={handleInputChange}
                    inputValue={searchText}
                    noOptionsText={
                      searchText
                        ? `No se encontraron estudiantes que coincidan con "${searchText}"`
                        : "No hay estudiantes disponibles"
                    }
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        label={`Buscar estudiante por nombre o ID (${filteredAndSearchedStudents.length} estudiantes)`}
                        variant="outlined"
                        fullWidth
                        placeholder="Escribe el nombre o ID del estudiante..."
                      />
                    )}
                    renderOption={(props, option) => (
                      // eslint-disable-next-line react/jsx-props-no-spreading
                      <li {...props}>
                        <MDBox display="flex" alignItems="center">
                          <MDAvatar
                            src={getRandomImage(option.student_id)}
                            size="sm"
                            sx={{ mr: 2 }}
                          />
                          <MDBox>
                            <MDTypography variant="button" fontWeight="bold">
                              {option.name}
                            </MDTypography>
                            <MDTypography
                              variant="caption"
                              color={getRiskColor(option.risk_level)}
                              display="block"
                            >
                              Riesgo: {option.risk_level}
                            </MDTypography>
                          </MDBox>
                        </MDBox>
                      </li>
                    )}
                    // Configuraciones adicionales para mejor control
                    clearOnEscape
                    disableCloseOnSelect={false}
                    blurOnSelect
                    selectOnFocus
                    clearOnBlur
                    handleHomeEndKeys
                  />
                </MDBox>
              </Card>
            </Grid>

            {/* Información del estudiante seleccionado */}
            {selectedStudent && (
              <>
                {/* Información básica */}
                <Grid item xs={12} md={4}>
                  <Card sx={{ height: "100%" }}>
                    <MDBox p={3} textAlign="center">
                      <MDAvatar
                        src={getRandomImage(selectedStudent.student_id)}
                        size="xxl"
                        sx={{ mb: 2 }}
                      />
                      <MDTypography variant="h5" fontWeight="bold">
                        {selectedStudent.name}
                      </MDTypography>
                      <MDTypography variant="body2" color="text" mb={2}>
                        ID: {selectedStudent.student_id}
                      </MDTypography>

                      <MDAlert color={getRiskColor(selectedStudent.risk_level)} sx={{ mb: 2 }}>
                        <MDTypography variant="button" fontWeight="bold">
                          Riesgo de Deserción: {selectedStudent.risk_level}
                        </MDTypography>
                      </MDAlert>

                      <MDBox mt={3}>
                        <MDTypography variant="h6" mb={1}>
                          Métricas Actuales
                        </MDTypography>
                        <MDBox display="flex" justifyContent="space-between" mb={1}>
                          <MDTypography variant="body2">Nota Actual:</MDTypography>
                          <MDTypography variant="body2" fontWeight="bold">
                            {selectedStudent.nota}/20
                          </MDTypography>
                        </MDBox>
                        <MDBox display="flex" justifyContent="space-between" mb={1}>
                          <MDTypography variant="body2">Asistencia:</MDTypography>
                          <MDTypography variant="body2" fontWeight="bold">
                            {selectedStudent.asistencia}%
                          </MDTypography>
                        </MDBox>
                        <MDBox display="flex" justifyContent="space-between" mb={1}>
                          <MDTypography variant="body2">Conducta:</MDTypography>
                          <MDTypography
                            variant="body2"
                            fontWeight="bold"
                            color={
                              selectedStudent.conducta === "Mala"
                                ? "error"
                                : selectedStudent.conducta === "Regular"
                                ? "warning"
                                : "success"
                            }
                          >
                            {selectedStudent.conducta || "Regular"}
                          </MDTypography>
                        </MDBox>
                      </MDBox>
                    </MDBox>
                  </Card>
                </Grid>

                {/* Factores de riesgo */}
                <Grid item xs={12} md={8}>
                  <Card sx={{ height: "100%" }}>
                    <MDBox p={3}>
                      <MDTypography variant="h6" mb={3}>
                        Análisis de Factores de Riesgo
                      </MDTypography>

                      {studentData?.factoresRiesgo?.map((factor, index) => (
                        <MDBox key={index} mb={4}>
                          <MDBox
                            display="flex"
                            justifyContent="space-between"
                            alignItems="center"
                            mb={2}
                          >
                            <MDBox>
                              <MDTypography variant="button" fontWeight="bold" mb={1}>
                                {factor.factor}
                              </MDTypography>
                              <MDTypography variant="body2" color="text" display="block">
                                Valor actual: {factor.valor}
                              </MDTypography>
                            </MDBox>
                            <MDAlert color={getRiskColor(factor.impacto)} sx={{ py: 0.5, px: 1 }}>
                              <MDTypography variant="caption" fontWeight="bold">
                                {factor.impacto}
                              </MDTypography>
                            </MDAlert>
                          </MDBox>

                          {/* Barra de progreso visual mejorada */}
                          <MDBox mb={2}>
                            <MDBox
                              sx={{
                                width: "100%",
                                height: 12,
                                backgroundColor: "#f0f0f0",
                                borderRadius: 2,
                                overflow: "hidden",
                                position: "relative",
                              }}
                            >
                              <MDBox
                                sx={{
                                  width: (() => {
                                    // Calcular el ancho dinámicamente según el factor y su valor
                                    if (factor.factor === "Asistencia") {
                                      // Para asistencia: usar el porcentaje directamente
                                      const asistenciaValue = parseFloat(
                                        factor.valor.replace("%", "")
                                      );
                                      return `${Math.min(100, Math.max(0, asistenciaValue))}%`;
                                    } else if (factor.factor === "Notas") {
                                      // Para notas: convertir de escala 0-20 a porcentaje 0-100
                                      const notaValue = parseFloat(factor.valor.split("/")[0]);
                                      const porcentaje = (notaValue / 20) * 100;
                                      return `${Math.min(100, Math.max(0, porcentaje))}%`;
                                    } else if (factor.factor === "Conducta") {
                                      // Para conducta: mapear valores cualitativos a porcentajes
                                      const conductaValue = factor.valor.toLowerCase();
                                      if (conductaValue === "mala") return "25%";
                                      if (conductaValue === "regular") return "50%";
                                      if (conductaValue === "buena") return "75%";
                                      if (conductaValue === "excelente") return "100%";
                                      return "50%"; // valor por defecto para "Regular"
                                    }
                                    return "50%"; // fallback
                                  })(),
                                  height: "100%",
                                  backgroundColor:
                                    factor.impacto === "Alto"
                                      ? "#f44336"
                                      : factor.impacto === "Medio"
                                      ? "#ff9800"
                                      : "#4caf50",
                                  transition: "width 0.3s ease",
                                }}
                              />
                              <MDTypography
                                variant="caption"
                                sx={{
                                  position: "absolute",
                                  top: "50%",
                                  left: "50%",
                                  transform: "translate(-50%, -50%)",
                                  color: "#ffffff",
                                  fontWeight: "bold",
                                  fontSize: "11px",
                                  textShadow: "2px 2px 4px rgba(0,0,0,0.9)",
                                  zIndex: 10,
                                }}
                              >
                                {factor.valor}
                              </MDTypography>
                            </MDBox>
                          </MDBox>

                          {/* Descripción y rangos */}
                          <MDBox p={2} sx={{ backgroundColor: "#f8f9fa", borderRadius: 1 }}>
                            <MDTypography variant="body2" color="text" mb={1}>
                              📊 {factor.descripcion}
                            </MDTypography>

                            {/* Mostrar rangos específicos según el factor */}
                            {factor.factor === "Asistencia" && (
                              <MDBox mt={1}>
                                <MDTypography variant="caption" color="text">
                                  <strong>Rangos:</strong>
                                  <span style={{ color: "#4caf50", marginLeft: "8px" }}>
                                    ✅ Bajo riesgo: ≥85%
                                  </span>
                                  <span style={{ color: "#ff9800", marginLeft: "8px" }}>
                                    ⚠️ Medio riesgo: 70-84%
                                  </span>
                                  <span style={{ color: "#f44336", marginLeft: "8px" }}>
                                    ❌ Alto riesgo: &lt;70%
                                  </span>
                                </MDTypography>
                              </MDBox>
                            )}

                            {factor.factor === "Notas" && (
                              <MDBox mt={1}>
                                <MDTypography variant="caption" color="text">
                                  <strong>Rangos:</strong>
                                  <span style={{ color: "#4caf50", marginLeft: "8px" }}>
                                    ✅ Bajo riesgo: ≥14/20
                                  </span>
                                  <span style={{ color: "#ff9800", marginLeft: "8px" }}>
                                    ⚠️ Medio riesgo: 11-13.9/20
                                  </span>
                                  <span style={{ color: "#f44336", marginLeft: "8px" }}>
                                    ❌ Alto riesgo: &lt;11/20
                                  </span>
                                </MDTypography>
                              </MDBox>
                            )}

                            {factor.factor === "Conducta" && (
                              <MDBox mt={1}>
                                <MDTypography variant="caption" color="text">
                                  <strong>Categorías:</strong>
                                  <span style={{ color: "#4caf50", marginLeft: "8px" }}>
                                    ✅ Bajo riesgo: Buena/Excelente
                                  </span>
                                  <span style={{ color: "#ff9800", marginLeft: "8px" }}>
                                    ⚠️ Medio riesgo: Regular
                                  </span>
                                  <span style={{ color: "#f44336", marginLeft: "8px" }}>
                                    ❌ Alto riesgo: Mala
                                  </span>
                                </MDTypography>
                              </MDBox>
                            )}
                          </MDBox>
                        </MDBox>
                      ))}

                      {/* Recomendaciones mejoradas */}
                      <MDBox mt={4} p={3} sx={{ backgroundColor: "#e3f2fd", borderRadius: 2 }}>
                        <MDTypography variant="h6" mb={2} color="info">
                          🎯 Recomendaciones Personalizadas
                        </MDTypography>

                        {/* Recomendaciones específicas por factor */}
                        {studentData?.factoresRiesgo?.map(
                          (factor, index) =>
                            factor.impacto !== "Bajo" && (
                              <MDBox key={index} mb={2}>
                                <MDTypography
                                  variant="button"
                                  fontWeight="bold"
                                  color="text"
                                  display="block"
                                >
                                  📌 {factor.factor} ({factor.impacto} riesgo - {factor.valor}):
                                </MDTypography>
                                <ul style={{ marginTop: "4px", marginBottom: "8px" }}>
                                  {factor.factor === "Asistencia" && factor.impacto === "Alto" && (
                                    <>
                                      <li>
                                        <MDTypography variant="body2">
                                          Contacto inmediato con padres/tutores
                                        </MDTypography>
                                      </li>
                                      <li>
                                        <MDTypography variant="body2">
                                          Identificar barreras que impiden la asistencia
                                        </MDTypography>
                                      </li>
                                      <li>
                                        <MDTypography variant="body2">
                                          Plan de recuperación de clases perdidas
                                        </MDTypography>
                                      </li>
                                    </>
                                  )}
                                  {factor.factor === "Asistencia" && factor.impacto === "Medio" && (
                                    <>
                                      <li>
                                        <MDTypography variant="body2">
                                          Monitoreo semanal de asistencia
                                        </MDTypography>
                                      </li>
                                      <li>
                                        <MDTypography variant="body2">
                                          Recordatorios y seguimiento personalizado
                                        </MDTypography>
                                      </li>
                                    </>
                                  )}
                                  {factor.factor === "Notas" && factor.impacto === "Alto" && (
                                    <>
                                      <li>
                                        <MDTypography variant="body2">
                                          Tutoría académica inmediata
                                        </MDTypography>
                                      </li>
                                      <li>
                                        <MDTypography variant="body2">
                                          Evaluación de necesidades de aprendizaje
                                        </MDTypography>
                                      </li>
                                      <li>
                                        <MDTypography variant="body2">
                                          Plan de refuerzo académico personalizado
                                        </MDTypography>
                                      </li>
                                    </>
                                  )}
                                  {factor.factor === "Notas" && factor.impacto === "Medio" && (
                                    <>
                                      <li>
                                        <MDTypography variant="body2">
                                          Apoyo en materias específicas
                                        </MDTypography>
                                      </li>
                                      <li>
                                        <MDTypography variant="body2">
                                          Técnicas de estudio y organización
                                        </MDTypography>
                                      </li>
                                    </>
                                  )}
                                  {factor.factor === "Conducta" && factor.impacto === "Alto" && (
                                    <>
                                      <li>
                                        <MDTypography variant="body2">
                                          Reunión urgente con equipo disciplinario
                                        </MDTypography>
                                      </li>
                                      <li>
                                        <MDTypography variant="body2">
                                          Plan de mejora conductual
                                        </MDTypography>
                                      </li>
                                    </>
                                  )}
                                  {factor.factor === "Conducta" && factor.impacto === "Medio" && (
                                    <>
                                      <li>
                                        <MDTypography variant="body2">
                                          Charlas motivacionales y orientación
                                        </MDTypography>
                                      </li>
                                      <li>
                                        <MDTypography variant="body2">
                                          Actividades de integración social
                                        </MDTypography>
                                      </li>
                                    </>
                                  )}
                                </ul>
                              </MDBox>
                            )
                        )}

                        {/* Mensaje cuando todo está bien */}
                        {studentData?.factoresRiesgo?.every(
                          (factor) => factor.impacto === "Bajo"
                        ) && (
                          <MDBox>
                            <MDTypography variant="body2" color="success">
                              🎉 ¡Excelente! Este estudiante mantiene un rendimiento satisfactorio
                              en todas las áreas. Continuar con el seguimiento regular y reconocer
                              sus logros.
                            </MDTypography>
                          </MDBox>
                        )}
                      </MDBox>
                    </MDBox>
                  </Card>
                </Grid>

                {/* Historial académico */}
                <Grid item xs={12}>
                  <Card>
                    <MDBox p={3}>
                      <MDTypography variant="h6" mb={3}>
                        Historial Académico Reciente
                      </MDTypography>

                      <Grid container spacing={3}>
                        <Grid item xs={12} md={6}>
                          <MDBox p={2} sx={{ backgroundColor: "#f8f9fa", borderRadius: 2 }}>
                            <MDTypography variant="button" fontWeight="bold" mb={2} display="block">
                              📊 Evolución de Notas
                            </MDTypography>
                            {studentData?.historialNotas?.map((registro, index) => (
                              <MDBox
                                key={index}
                                display="flex"
                                justifyContent="space-between"
                                mb={1}
                              >
                                <MDTypography variant="body2">{registro.fecha}</MDTypography>
                                <MDTypography variant="body2" fontWeight="bold">
                                  {registro.nota}/20
                                </MDTypography>
                              </MDBox>
                            ))}
                          </MDBox>
                        </Grid>

                        <Grid item xs={12} md={6}>
                          <MDBox p={2} sx={{ backgroundColor: "#f8f9fa", borderRadius: 2 }}>
                            <MDTypography variant="button" fontWeight="bold" mb={2} display="block">
                              📅 Evolución de Asistencia
                            </MDTypography>
                            {studentData?.historialAsistencia?.map((registro, index) => (
                              <MDBox
                                key={index}
                                display="flex"
                                justifyContent="space-between"
                                mb={1}
                              >
                                <MDTypography variant="body2">{registro.fecha}</MDTypography>
                                <MDTypography variant="body2" fontWeight="bold">
                                  {registro.asistencia}%
                                </MDTypography>
                              </MDBox>
                            ))}
                          </MDBox>
                        </Grid>
                      </Grid>
                    </MDBox>
                  </Card>
                </Grid>
              </>
            )}

            {/* Estado inicial */}
            {!selectedStudent && (
              <Grid item xs={12}>
                <Card>
                  <MDBox p={5} textAlign="center">
                    <MDTypography variant="h4" color="text" mb={2}>
                      👤 Selecciona un Estudiante
                    </MDTypography>
                    <MDTypography variant="body1" color="text">
                      Usa el buscador arriba para encontrar y analizar a un estudiante específico
                    </MDTypography>
                  </MDBox>
                </Card>
              </Grid>
            )}

            {error && (
              <Grid item xs={12}>
                <MDAlert color="error">{error}</MDAlert>
              </Grid>
            )}
          </Grid>
        )}
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default IndividualAnalysis;
