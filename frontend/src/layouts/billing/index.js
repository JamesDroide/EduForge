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
import React, { useEffect, useState } from "react";
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

  const { showDashboardButton, processingMessage } = location.state || {};

  // Usar cache optimizado en lugar de fetch individual
  const { students: allPredictions, loading, hasValidData } = useStudentsCache();
  const [activeFilter, setActiveFilter] = useState("Todos");

  // Determinar datos desde múltiples fuentes, pero priorizar el estado interno
  let finalPredictions = allPredictions;

  // Si hay datos desde URL o state, usar esos primero
  if (urlData.length > 0) {
    finalPredictions = urlData;
  } else if (stateData.length > 0) {
    finalPredictions = stateData;
  }

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
                      📊 Ir al Reporte General (Dashboard)
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
                          Todos
                        </MDButton>
                      </Grid>
                      <Grid item>
                        <MDButton
                          variant={activeFilter === "Alto" ? "contained" : "outlined"}
                          color="error"
                          onClick={() => handleFilterChange("Alto")}
                        >
                          Alto Riesgo
                        </MDButton>
                      </Grid>
                      <Grid item>
                        <MDButton
                          variant={activeFilter === "Medio" ? "contained" : "outlined"}
                          color="warning"
                          onClick={() => handleFilterChange("Medio")}
                        >
                          Medio Riesgo
                        </MDButton>
                      </Grid>
                      <Grid item>
                        <MDButton
                          variant={activeFilter === "Bajo" ? "contained" : "outlined"}
                          color="success"
                          onClick={() => handleFilterChange("Bajo")}
                        >
                          Bajo Riesgo
                        </MDButton>
                      </Grid>
                    </Grid>
                  </MDBox>
                )}

                {/* Solo mostrar estadísticas si hay datos del CSV */}
                {hasValidData && currentPredictions.length > 0 && (
                  <MDBox mb={3} p={2} sx={{ backgroundColor: "#f8f9fa", borderRadius: "8px" }}>
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={4}>
                        <MDTypography variant="body2" fontWeight="bold">
                          Total estudiantes: {currentPredictions.length}
                        </MDTypography>
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <MDTypography variant="body2" fontWeight="bold" color="error">
                          Riesgo Alto:{" "}
                          {currentPredictions.filter((p) => p.riesgo_desercion === "Alto").length}
                        </MDTypography>
                      </Grid>
                      <Grid item xs={12} md={4}>
                        <MDTypography variant="body2" fontWeight="bold" color="warning">
                          Riesgo Medio:{" "}
                          {currentPredictions.filter((p) => p.riesgo_desercion === "Medio").length}
                        </MDTypography>
                      </Grid>
                    </Grid>
                  </MDBox>
                )}

                {/* Mostrar contenido según el estado - Replicando la lógica del dashboard */}
                {!hasValidData ? (
                  // Vista vacía cuando no hay CSV cargado (igual que dashboard e individual)
                  <MDBox textAlign="center" py={5}>
                    <MDTypography variant="h3" color="text" mb={3}>
                      📋 No hay datos disponibles
                    </MDTypography>
                    <MDTypography variant="h6" color="text" mb={2}>
                      Para ver los resultados completos, necesitas cargar un archivo CSV primero
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
                ) : loading ? (
                  <MDBox textAlign="center" py={4}>
                    <MDTypography variant="h6" color="text">
                      Cargando datos...
                    </MDTypography>
                  </MDBox>
                ) : currentPredictions.length > 0 ? (
                  // TABLA CON DATOS - solo si hay CSV válido
                  <MDBox
                    mt={4}
                    sx={{
                      height: "500px",
                      overflowY: "auto",
                      overflowX: "hidden",
                      width: "100%",
                    }}
                  >
                    <table
                      style={{
                        width: "100%",
                        borderCollapse: "collapse",
                        tableLayout: "fixed",
                      }}
                    >
                      <thead>
                        <tr>
                          {Object.keys(currentPredictions[0] || {}).map((key, index) => {
                            // Definir anchos específicos para cada columna
                            const getColumnWidth = (columnKey, columnIndex) => {
                              switch (columnKey.toLowerCase()) {
                                case "id_estudiante":
                                  return "8%";
                                case "nombre":
                                  return "15%";
                                case "nota":
                                case "nota_final":
                                  return "8%";
                                case "asistencia":
                                  return "8%";
                                case "inasistencia":
                                  return "8%";
                                case "conducta":
                                  return "10%";
                                case "fecha":
                                  return "10%";
                                case "tiempo_prediccion":
                                  return "12%";
                                case "resultado_prediccion":
                                  return "8%";
                                case "riesgo":
                                case "riesgo_desercion":
                                  return "13%";
                                default:
                                  return "10%";
                              }
                            };

                            return (
                              <th
                                key={key}
                                style={{
                                  border: "1px solid #ddd",
                                  padding: "12px 8px",
                                  textAlign: "left",
                                  backgroundColor: "#f2f2f2",
                                  fontWeight: "bold",
                                  fontSize: "14px",
                                  width: getColumnWidth(key, index),
                                  wordWrap: "break-word",
                                }}
                              >
                                {key}
                              </th>
                            );
                          })}
                        </tr>
                      </thead>
                      <tbody>
                        {currentPredictions.map((row, index) => {
                          // Detectar el nivel de riesgo para aplicar colores correctos
                          const riesgoDesercion = Object.values(row).find(
                            (val) =>
                              typeof val === "string" &&
                              (val.toLowerCase() === "alto" ||
                                val.toLowerCase() === "medio" ||
                                val.toLowerCase() === "bajo")
                          );

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
                                studentData.id_estudiante ||
                                studentData.student_id ||
                                studentData.ID ||
                                null,
                              name:
                                studentData.nombre ||
                                studentData.name ||
                                studentData.Nombre ||
                                "Estudiante",
                              nota: parseFloat(
                                studentData.nota_final || studentData.nota || studentData.Nota || 0
                              ),
                              asistencia: parseFloat(
                                studentData.asistencia || studentData.Asistencia || 0
                              ),
                              risk_level:
                                studentData.riesgo_desercion ||
                                studentData.risk_level ||
                                studentData["Riesgo de Deserción"] ||
                                "Bajo",
                              conducta: studentData.conducta || studentData.Conducta || "Regular",
                              ...studentData, // Incluir todos los datos originales
                            };

                            // Buscar datos completos desde localStorage solo como respaldo
                            try {
                              const storedPredictions = localStorage.getItem("latest_predictions");
                              if (storedPredictions) {
                                const parsedData = JSON.parse(storedPredictions);

                                // Buscar el estudiante específico en los datos completos
                                const fullStudentData = parsedData.find(
                                  (p) =>
                                    (p.id_estudiante &&
                                      p.id_estudiante.toString() ===
                                        completeStudentData.student_id?.toString()) ||
                                    (p.student_id &&
                                      p.student_id.toString() ===
                                        completeStudentData.student_id?.toString()) ||
                                    (p.nombre && p.nombre === completeStudentData.name) ||
                                    (p.name && p.name === completeStudentData.name)
                                );

                                if (fullStudentData) {
                                  // Combinar datos encontrados con datos base
                                  completeStudentData = {
                                    ...completeStudentData,
                                    ...fullStudentData,
                                    student_id:
                                      fullStudentData.id_estudiante ||
                                      fullStudentData.student_id ||
                                      completeStudentData.student_id,
                                    name:
                                      fullStudentData.nombre ||
                                      fullStudentData.name ||
                                      completeStudentData.name,
                                    nota: parseFloat(
                                      fullStudentData.nota_final ||
                                        fullStudentData.nota ||
                                        completeStudentData.nota ||
                                        0
                                    ),
                                    risk_level:
                                      fullStudentData.riesgo_desercion ||
                                      fullStudentData.risk_level ||
                                      completeStudentData.risk_level,
                                  };
                                }
                              }
                            } catch (e) {
                              console.error("Error buscando datos completos:", e);
                            }

                            console.log("📤 Navegando con datos:", completeStudentData);

                            // Navegar al análisis individual
                            navigate("/individual", {
                              state: {
                                preselectedStudent: completeStudentData,
                                fromDashboard: true,
                              },
                            });
                          };

                          return (
                            <tr key={index} style={colorStyles}>
                              {Object.entries(row).map(([key, value], cellIndex) => (
                                <td
                                  key={cellIndex}
                                  style={{
                                    border: "1px solid #ddd",
                                    padding: "8px",
                                    fontSize: "13px",
                                    wordWrap: "break-word",
                                    overflow: "hidden",
                                    cursor: key === "nombre" ? "pointer" : "default",
                                    textDecoration: key === "nombre" ? "underline" : "none",
                                  }}
                                  onClick={
                                    key === "nombre" ? () => handleStudentClick(row) : undefined
                                  }
                                  title={
                                    key === "nombre" ? "Clic para ver análisis individual" : ""
                                  }
                                >
                                  {typeof value === "number"
                                    ? key === "id_estudiante" || key.toLowerCase().includes("id")
                                      ? Math.round(value)
                                      : value.toFixed(2)
                                    : value}
                                </td>
                              ))}
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </MDBox>
                ) : (
                  // Mensaje alternativo si hay CSV pero no hay datos después del filtro
                  <MDBox textAlign="center" py={4}>
                    <MDTypography variant="h6" color="text">
                      {activeFilter === "Todos"
                        ? "No hay datos para mostrar"
                        : `No hay estudiantes con riesgo ${activeFilter}`}
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
