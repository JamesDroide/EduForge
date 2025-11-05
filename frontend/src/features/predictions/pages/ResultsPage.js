/**
=========================================================
* Material Dashboard 2 React - v2.2.0
=========================================================

* Product Page: https://www.creative-tim.com/product/material-dashboard-react
* Copyright 2023 Creative Tim (https://www.creative-tim.com)

Coded by www.creative-tim.com

 =========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
*/

// @mui material components
import React, { useState, useEffect } from "react";
import { useLocation, useNavigate, useSearchParams } from "react-router-dom";

// @mui/material imports
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDButton from "components/MDButton";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";

// Cache optimizado para estudiantes
import { useStudentsCache } from "utils/studentsCache";

function Billing() {
  const location = useLocation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [hoveredCell, setHoveredCell] = useState(null);

  // Obtener datos desde multiple fuentes
  const stateData = location.state?.predictions || [];
  const urlPredictions = searchParams.get("predictions");
  const fromUpload = searchParams.get("fromUpload") === "true";

  let urlData = [];
  if (urlPredictions) {
    try {
      urlData = JSON.parse(decodeURIComponent(urlPredictions));
    } catch (e) {
      console.error("Error parsing URL predictions:", e);
    }
  }

  const { processingMessage } = location.state || {};

  // Usar cache optimizado en lugar de fetch individual
  const { students: allPredictions, loading, hasValidData, refresh } = useStudentsCache();
  const [activeFilter, setActiveFilter] = useState("Todos");
  const [lastCsvTimestamp, setLastCsvTimestamp] = useState(null);

  // Determinar datos desde múltiples fuentes, pero priorizar el estado interno
  let finalPredictions = allPredictions;

  // Si hay datos desde URL o state, usar esos primero
  if (urlData.length > 0) {
    finalPredictions = urlData;
  } else if (stateData.length > 0) {
    finalPredictions = stateData;
  }

  // Detectar cambios en el CSV y forzar actualización
  useEffect(() => {
    const checkForNewCsv = () => {
      const currentTimestamp = localStorage.getItem("csv_upload_timestamp");
      if (currentTimestamp && currentTimestamp !== lastCsvTimestamp) {
        console.log("🔄 Nuevo CSV detectado en Resultados Completos, actualizando...");
        setLastCsvTimestamp(currentTimestamp);
        refresh(); // Forzar actualización del caché
      }
    };

    // Verificar inmediatamente
    checkForNewCsv();

    // Escuchar eventos de nuevo CSV
    const handleCsvUploaded = (event) => {
      console.log("📄 Evento CSV detectado en Resultados Completos");
      refresh();
    };

    // Verificar cada 1 segundo para detectar cambios rápidamente
    const intervalId = setInterval(checkForNewCsv, 1000);

    window.addEventListener("csvUploaded", handleCsvUploaded);

    return () => {
      clearInterval(intervalId);
      window.removeEventListener("csvUploaded", handleCsvUploaded);
    };
  }, [lastCsvTimestamp, refresh]);

  // Aplicar filtro a los datos
  const currentPredictions = finalPredictions.filter((prediction) => {
    if (activeFilter === "Todos") return true;
    return prediction.riesgo_desercion === activeFilter;
  });

  console.log("📊 hasValidData:", hasValidData);
  console.log("📊 Datos filtrados a mostrar:", currentPredictions.length);

  // Función para manejar el filtrado
  const handleFilterChange = (filterType) => {
    setActiveFilter(filterType);
  };

  // Estilos para las celdas de encabezado
  const headerCellBaseStyle = {
    border: "1px solid #ddd",
    padding: "12px 8px",
    backgroundColor: "#f2f2f2",
    fontWeight: "bold",
    fontSize: "14px",
  };

  // Estilos para las celdas de datos
  const dataCellStyle = {
    border: "1px solid #ddd",
    padding: "8px",
    fontSize: "13px",
  };

  const dataCellBoldStyle = {
    border: "1px solid #ddd",
    padding: "8px",
    fontSize: "13px",
    fontWeight: "bold",
  };

  const clickableCellStyle = {
    border: "1px solid #ddd",
    padding: "8px",
    fontSize: "13px",
    cursor: "pointer",
    fontWeight: "500", // Un poco más destacado que el texto normal
    color: "#2c3e50", // Color más oscuro y profesional
    transition: "all 0.2s ease", // Transición suave
  };

  // Estilo para el hover de las celdas clickeables
  const clickableCellHoverStyle = {
    color: "#1a202c", // Color más oscuro en hover
    fontWeight: "600", // Más bold en hover
    textShadow: "0 0 1px rgba(26, 32, 44, 0.3)", // Sutil sombra para mayor contraste
  };

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox mt={6} mb={3}>
        <Grid container spacing={3} justifyContent="center">
          <Grid item xs={12}>
            <Card>
              <MDBox p={4}>
                {/* Mensaje de procesamiento exitoso */}
                {(processingMessage || fromUpload) && (
                  <MDBox
                    mb={3}
                    p={2}
                    sx={{
                      backgroundColor: "#d4edda",
                      borderRadius: "8px",
                      border: "1px solid #c3e6cb",
                    }}
                  >
                    <MDTypography variant="h6" color="success" fontWeight="bold">
                      ✅{" "}
                      {processingMessage ||
                        "CSV procesado exitosamente - Datos completos disponibles"}
                    </MDTypography>
                    <MDTypography variant="body2" color="text">
                      Tiempo de procesamiento: {new Date().toLocaleTimeString()} -{" "}
                      {currentPredictions.length} registros procesados
                    </MDTypography>
                  </MDBox>
                )}

                {/* Botón para ir al Dashboard - Solo visible si hay datos */}
                {hasValidData && currentPredictions.length > 0 && (
                  <MDBox mb={3} textAlign="center">
                    <MDButton
                      variant="gradient"
                      color="success"
                      size="large"
                      onClick={() =>
                        navigate("/dashboard", {
                          state: {
                            message: "Datos actualizados desde resultados completos",
                          },
                        })
                      }
                    >
                      📊 IR AL REPORTE GENERAL (DASHBOARD)
                    </MDButton>
                  </MDBox>
                )}

                <MDTypography variant="h5" mb={2}>
                  Resultados de Predicción de Deserción
                </MDTypography>

                {/* Solo mostrar filtros si hay datos del CSV */}
                {hasValidData && (
                  <MDBox mb={3}>
                    <Grid container spacing={2} justifyContent="center">
                      <Grid item>
                        <MDButton
                          variant={activeFilter === "Todos" ? "contained" : "outlined"}
                          color="primary"
                          onClick={() => handleFilterChange("Todos")}
                        >
                          TODOS
                        </MDButton>
                      </Grid>
                      <Grid item>
                        <MDButton
                          variant={activeFilter === "Alto" ? "contained" : "outlined"}
                          color="error"
                          onClick={() => handleFilterChange("Alto")}
                        >
                          ALTO RIESGO
                        </MDButton>
                      </Grid>
                      <Grid item>
                        <MDButton
                          variant={activeFilter === "Medio" ? "contained" : "outlined"}
                          color="warning"
                          onClick={() => handleFilterChange("Medio")}
                        >
                          MEDIO RIESGO
                        </MDButton>
                      </Grid>
                      <Grid item>
                        <MDButton
                          variant={activeFilter === "Bajo" ? "contained" : "outlined"}
                          color="success"
                          onClick={() => handleFilterChange("Bajo")}
                        >
                          BAJO RIESGO
                        </MDButton>
                      </Grid>
                    </Grid>
                  </MDBox>
                )}

                {/* Solo mostrar estadísticas si hay datos del CSV */}
                {hasValidData && currentPredictions.length > 0 && (
                  <MDBox mb={3} p={2} sx={{ backgroundColor: "#f8f9fa", borderRadius: "8px" }}>
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={3}>
                        <MDTypography variant="body2" fontWeight="bold">
                          Total estudiantes: {currentPredictions.length}
                        </MDTypography>
                      </Grid>
                      <Grid item xs={12} md={3}>
                        <MDTypography variant="body2" fontWeight="bold" color="error">
                          Riesgo Alto:{" "}
                          {currentPredictions.filter((p) => p.riesgo_desercion === "Alto").length}
                        </MDTypography>
                      </Grid>
                      <Grid item xs={12} md={3}>
                        <MDTypography variant="body2" fontWeight="bold" color="warning">
                          Riesgo Medio:{" "}
                          {currentPredictions.filter((p) => p.riesgo_desercion === "Medio").length}
                        </MDTypography>
                      </Grid>
                      <Grid item xs={12} md={3}>
                        <MDTypography variant="body2" fontWeight="bold" color="info">
                          Tasa de casos identificados:{" "}
                          {finalPredictions.length > 0
                            ? (
                                (finalPredictions.filter((p) => p.riesgo_desercion === "Alto")
                                  .length /
                                  finalPredictions.length) *
                                100
                              ).toFixed(2)
                            : "0.00"}
                          %
                        </MDTypography>
                      </Grid>
                    </Grid>
                  </MDBox>
                )}

                {/* Mostrar contenido según el estado */}
                {!hasValidData ? (
                  // Vista vacía cuando no hay CSV cargado
                  <MDBox textAlign="center" py={5}>
                    <MDTypography variant="h3" color="text" mb={3}>
                      📋 No hay datos disponibles
                    </MDTypography>
                    <MDTypography variant="h6" color="text" mb={2}>
                      Para ver los resultados completos, necesitas cargar un archivo CSV primero
                    </MDTypography>
                    <MDTypography variant="body1" color="text" mb={4}>
                      Ve a la sección "Cargar Datos" para subir un archivo CSV con
                      <br />
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
                ) : loading ? (
                  <MDBox textAlign="center" py={4}>
                    <MDTypography variant="h6" color="text">
                      Cargando datos...
                    </MDTypography>
                  </MDBox>
                ) : currentPredictions.length > 0 ? (
                  // TABLA CON DATOS - Una sola tabla limpia y bien formateada
                  <MDBox
                    mt={4}
                    sx={{
                      height: "500px",
                      overflowY: "auto",
                      overflowX: "auto",
                      width: "100%",
                    }}
                  >
                    <table
                      style={{
                        width: "100%",
                        borderCollapse: "collapse",
                        tableLayout: "auto",
                        minWidth: "1000px",
                      }}
                    >
                      <thead>
                        <tr>
                          <th
                            style={{
                              ...headerCellBaseStyle,
                              minWidth: "60px",
                            }}
                          >
                            ID
                          </th>
                          <th
                            style={{
                              ...headerCellBaseStyle,
                              minWidth: "150px",
                            }}
                          >
                            Nombre
                          </th>
                          <th
                            style={{
                              ...headerCellBaseStyle,
                              minWidth: "80px",
                            }}
                          >
                            Nota
                          </th>
                          <th
                            style={{
                              ...headerCellBaseStyle,
                              minWidth: "100px",
                            }}
                          >
                            Conducta
                          </th>
                          <th
                            style={{
                              ...headerCellBaseStyle,
                              minWidth: "100px",
                            }}
                          >
                            Asistencia
                          </th>
                          <th
                            style={{
                              ...headerCellBaseStyle,
                              minWidth: "150px",
                            }}
                          >
                            Tiempo Predicción
                          </th>
                          <th
                            style={{
                              ...headerCellBaseStyle,
                              minWidth: "130px",
                            }}
                          >
                            Resultado Predicción
                          </th>
                          <th
                            style={{
                              ...headerCellBaseStyle,
                              minWidth: "130px",
                            }}
                          >
                            Riesgo Deserción
                          </th>
                          <th
                            style={{
                              ...headerCellBaseStyle,
                              minWidth: "130px",
                            }}
                          >
                            Probabilidad Deserción
                          </th>
                        </tr>
                      </thead>
                      <tbody>
                        {currentPredictions.map((row, index) => {
                          // Detectar el nivel de riesgo para aplicar colores correctos
                          const riesgoDesercion = row.riesgo_desercion || "Bajo";

                          // Función para obtener colores según el nivel de riesgo
                          const getColorStyles = (riesgo) => {
                            switch (riesgo?.toLowerCase()) {
                              case "alto":
                                return {
                                  backgroundColor: "#ffcdd2", // Rojo claro
                                  color: "#c62828", // Rojo oscuro
                                  fontWeight: "bold",
                                };
                              case "medio":
                                return {
                                  backgroundColor: "#fff3cd", // Amarillo claro
                                  color: "#856404", // Amarillo oscuro/marrón
                                  fontWeight: "bold",
                                };
                              case "bajo":
                                return {
                                  backgroundColor: "#d4edda", // Verde claro
                                  color: "#155724", // Verde oscuro
                                  fontWeight: "normal",
                                };
                              default:
                                return {
                                  backgroundColor: "#f8f9fa", // Gris claro por defecto
                                  color: "inherit",
                                  fontWeight: "normal",
                                };
                            }
                          };

                          const colorStyles = getColorStyles(riesgoDesercion);

                          // Función para manejar el clic en el nombre del estudiante
                          const handleStudentClick = (studentData) => {
                            console.log(
                              "🔍 Clic en estudiante desde Resultados completos:",
                              studentData
                            );

                            // Crear objeto base con los datos disponibles del row
                            let completeStudentData = {
                              student_id:
                                studentData.id_estudiante || studentData.student_id || null,
                              name: studentData.nombre || studentData.name || "Estudiante",
                              nota: parseFloat(studentData.nota_final || studentData.nota || 0),
                              asistencia: parseFloat(studentData.asistencia || 0),
                              risk_level: studentData.riesgo_desercion || "Bajo",
                              conducta: studentData.conducta || "Regular",
                              ...studentData,
                            };

                            console.log("📤 Navegando con datos:", completeStudentData);

                            // Navegar al análisis individual con el ID del estudiante en la URL
                            navigate(`/individual?studentId=${completeStudentData.student_id}`, {
                              state: {
                                preselectedStudent: completeStudentData,
                                fromResultados: true,
                              },
                            });
                          };

                          // Crear estilo dinámico para la celda del nombre
                          const nameRowKey = `name-${index}`;
                          const isHovered = hoveredCell === nameRowKey;
                          const dynamicNameCellStyle = {
                            ...clickableCellStyle,
                            ...(isHovered ? clickableCellHoverStyle : {}),
                          };

                          return (
                            <tr key={index} style={colorStyles}>
                              <td style={dataCellStyle}>
                                {row.id_estudiante || row.student_id || index + 1}
                              </td>
                              <td
                                style={dynamicNameCellStyle}
                                onClick={() => handleStudentClick(row)}
                                onMouseEnter={() => setHoveredCell(nameRowKey)}
                                onMouseLeave={() => setHoveredCell(null)}
                              >
                                {row.nombre || row.name || "N/A"}
                              </td>
                              <td style={dataCellStyle}>{row.nota_final || row.nota || "N/A"}</td>
                              <td style={dataCellStyle}>{row.conducta || "N/A"}</td>
                              <td style={dataCellStyle}>{row.asistencia || "N/A"}</td>
                              <td style={dataCellStyle}>{row.tiempo_prediccion || "N/A"}</td>
                              <td style={dataCellStyle}>{row.resultado_prediccion || "N/A"}</td>
                              <td style={dataCellBoldStyle}>{row.riesgo_desercion || "Bajo"}</td>
                              <td style={dataCellStyle}>{row.probabilidad_desercion || "N/A"}</td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </MDBox>
                ) : (
                  <MDBox textAlign="center" py={4}>
                    <MDTypography variant="h6" color="text">
                      No hay datos que coincidan con el filtro seleccionado
                    </MDTypography>
                  </MDBox>
                )}
              </MDBox>
            </Card>
          </Grid>
        </Grid>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default Billing;
