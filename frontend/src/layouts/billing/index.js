import React, { useState, useEffect } from "react";
import { useLocation, useNavigate, useSearchParams } from "react-router-dom";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import Icon from "@mui/material/Icon";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDButton from "components/MDButton";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import { useStudentsCache } from "utils/studentsCache";

function Billing() {
  const location = useLocation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [hoveredCell, setHoveredCell] = useState(null);

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

  const { students: allPredictions, loading, hasValidData, refresh } = useStudentsCache();
  const [activeFilter, setActiveFilter] = useState("Todos");
  const [lastCsvTimestamp, setLastCsvTimestamp] = useState(() =>
    localStorage.getItem("csv_upload_timestamp")
  );

  // Priorizar predicciones pasadas por URL o router state sobre el cache local
  let finalPredictions = allPredictions;
  if (urlData.length > 0) {
    finalPredictions = urlData;
  } else if (stateData.length > 0) {
    finalPredictions = stateData;
  }

  useEffect(() => {
    const checkForNewCsv = () => {
      const currentTimestamp = localStorage.getItem("csv_upload_timestamp");
      if (currentTimestamp && currentTimestamp !== lastCsvTimestamp) {
        setLastCsvTimestamp(currentTimestamp);
        refresh();
      }
    };

    checkForNewCsv();

    const handleStorageChange = (e) => {
      if (
        (e.key === "csv_uploaded" && e.newValue) ||
        e.key === "csv_upload_timestamp" ||
        e.key === "latest_predictions"
      ) {
        checkForNewCsv();
        refresh();
      }
    };

    const handleCsvUploaded = () => {
      checkForNewCsv();
      refresh();
    };

    window.addEventListener("storage", handleStorageChange);
    window.addEventListener("csvUploaded", handleCsvUploaded);

    return () => {
      window.removeEventListener("storage", handleStorageChange);
      window.removeEventListener("csvUploaded", handleCsvUploaded);
    };
  }, [lastCsvTimestamp, refresh]);

  const currentPredictions = finalPredictions.filter((prediction) => {
    if (activeFilter === "Todos") return true;
    return prediction.riesgo_desercion === activeFilter;
  });

  console.log("hasValidData:", hasValidData);
  console.log("Datos filtrados a mostrar:", currentPredictions.length);

  const handleFilterChange = (filterType) => {
    setActiveFilter(filterType);
  };

  const headerCellBaseStyle = {
    border: "1px solid #ddd",
    padding: "12px 8px",
    backgroundColor: "#f2f2f2",
    fontWeight: "bold",
    fontSize: "14px",
  };

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
    fontWeight: "500",
    color: "#2c3e50",
    transition: "all 0.2s ease",
  };

  const clickableCellHoverStyle = {
    color: "#1a202c",
    fontWeight: "600",
    textShadow: "0 0 1px rgba(26, 32, 44, 0.3)",
  };

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox mt={6} mb={3}>
        <Grid container spacing={3} justifyContent="center">
          <Grid item xs={12}>
            <Card>
              <MDBox p={4}>
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
                      <Icon sx={{ verticalAlign: "middle", mr: 0.5 }}>check_circle</Icon>
                      {processingMessage ||
                        "CSV procesado exitosamente - Datos completos disponibles"}
                    </MDTypography>
                    <MDTypography variant="body2" color="text">
                      Tiempo de procesamiento: {new Date().toLocaleTimeString()} -{" "}
                      {currentPredictions.length} registros procesados
                    </MDTypography>
                  </MDBox>
                )}

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
                      <Icon sx={{ verticalAlign: "middle", mr: 0.5 }}>assessment</Icon>
                      IR AL REPORTE GENERAL (DASHBOARD)
                    </MDButton>
                  </MDBox>
                )}

                <MDTypography variant="h5" mb={2}>
                  Resultados de Predicción de Deserción
                </MDTypography>

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

                {!hasValidData ? (
                  <MDBox textAlign="center" py={5}>
                    <MDTypography variant="h3" color="text" mb={3}>
                      <Icon sx={{ verticalAlign: "middle", mr: 0.5 }}>assignment</Icon>
                      No hay datos disponibles
                    </MDTypography>
                    <MDTypography variant="h6" color="text" mb={2}>
                      Para ver los resultados completos, necesitas cargar un archivo CSV primero
                    </MDTypography>
                    <MDTypography variant="body1" color="text" mb={4}>
                      Ve a la sección &quot;Cargar Datos&quot; para subir un archivo CSV con
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
                          const riesgoDesercion = row.riesgo_desercion || "Bajo";

                          const getColorStyles = (riesgo) => {
                            switch (riesgo?.toLowerCase()) {
                              case "alto":
                                return {
                                  backgroundColor: "#ffcdd2",
                                  color: "#c62828",
                                  fontWeight: "bold",
                                };
                              case "medio":
                                return {
                                  backgroundColor: "#fff3cd",
                                  color: "#856404",
                                  fontWeight: "bold",
                                };
                              case "bajo":
                                return {
                                  backgroundColor: "#d4edda",
                                  color: "#155724",
                                  fontWeight: "normal",
                                };
                              default:
                                return {
                                  backgroundColor: "#f8f9fa",
                                  color: "inherit",
                                  fontWeight: "normal",
                                };
                            }
                          };

                          const colorStyles = getColorStyles(riesgoDesercion);

                          const handleStudentClick = (studentData) => {
                            console.log(
                              "Clic en estudiante desde Resultados completos:",
                              studentData
                            );

                            const completeStudentData = {
                              student_id:
                                studentData.id_estudiante || studentData.student_id || null,
                              name: studentData.nombre || studentData.name || "Estudiante",
                              nota: parseFloat(studentData.nota_final || studentData.nota || 0),
                              asistencia: parseFloat(studentData.asistencia || 0),
                              risk_level: studentData.riesgo_desercion || "Bajo",
                              conducta: studentData.conducta || "Regular",
                              ...studentData,
                            };

                            console.log("Navegando con datos:", completeStudentData);

                            navigate(`/individual?studentId=${completeStudentData.student_id}`, {
                              state: {
                                preselectedStudent: completeStudentData,
                                fromResultados: true,
                              },
                            });
                          };

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
