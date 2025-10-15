import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import * as XLSX from "xlsx";
import { useNavigate } from "react-router-dom";

// @mui/material
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import Icon from "@mui/material/Icon";

// Componentes del Dashboard
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDButton from "components/MDButton";

// Layout
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import { API_ENDPOINTS } from "../../config/api";

// Material Dashboard 2 React context
import { useMaterialUIController } from "context";

function UploadData() {
  const [fileData, setFileData] = useState([]);
  const [fileName, setFileName] = useState("");
  const [rawFile, setRawFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const navigate = useNavigate();
  const [controller] = useMaterialUIController();
  const { darkMode } = controller;

  const onDrop = useCallback((acceptedFiles) => {
    const file = acceptedFiles[0];
    setRawFile(file); // Guardamos el archivo original
    setFileName(file.name);

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target.result);

        // Verificar si es archivo CSV o Excel
        const isCSV = file.name.toLowerCase().endsWith(".csv");

        if (isCSV) {
          // Para archivos CSV, leer como texto
          const csvReader = new FileReader();
          csvReader.onload = (csvEvent) => {
            try {
              const csvText = csvEvent.target.result;
              const lines = csvText.split("\n");
              const csvData = lines.map((line) => line.split(",").map((cell) => cell.trim()));
              setFileData(csvData);
            } catch (csvError) {
              console.error("Error procesando CSV:", csvError);
              alert("Error al procesar el archivo CSV. Verifique que el formato sea correcto.");
            }
          };
          csvReader.readAsText(file);
        } else {
          // Para archivos Excel
          const workbook = XLSX.read(data, {
            type: "array",
            cellDates: true,
            dateNF: "dd/mm/yyyy",
          });

          if (!workbook || !workbook.SheetNames || workbook.SheetNames.length === 0) {
            throw new Error("No se pudo encontrar hojas en el archivo Excel");
          }

          const worksheet = workbook.Sheets[workbook.SheetNames[0]];
          if (!worksheet) {
            throw new Error("La primera hoja del archivo está vacía");
          }

          const json = XLSX.utils.sheet_to_json(worksheet, {
            header: 1,
            defval: "",
            blankrows: false,
          });
          setFileData(json);
        }
      } catch (error) {
        console.error("Error procesando archivo:", error);
        alert(
          `Error al procesar el archivo: ${error.message}. Por favor verifique que el archivo no esté corrupto y tenga el formato correcto.`
        );
        setFileData([]);
        setFileName("");
        setRawFile(null);
      }
    };

    reader.onerror = (error) => {
      console.error("Error leyendo archivo:", error);
      alert("Error al leer el archivo. Por favor intente nuevamente.");
    };

    reader.readAsArrayBuffer(file);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: [".csv", ".xlsx", ".xls"],
  });

  const handleUpload = async () => {
    if (!rawFile) {
      alert("No hay archivo para enviar.");
      return;
    }
    setIsProcessing(true);

    try {
      // Obtener el token de autenticación
      const token = localStorage.getItem("token");

      // Paso 1: Subir el archivo
      const formData = new FormData();
      formData.append("file", rawFile);

      const uploadRes = await fetch(API_ENDPOINTS.UPLOAD, {
        method: "POST",
        headers: {
          ...(token && { Authorization: `Bearer ${token}` }),
        },
        body: formData,
      });

      if (!uploadRes.ok) {
        throw new Error("Error al subir el archivo");
      }

      const uploadResult = await uploadRes.json();
      console.log("📤 Upload result:", uploadResult);

      // Paso 2: Procesar el archivo para predicciones
      const cleanFilename = uploadResult.filename.trim();
      const uploadId = uploadResult.upload_id; // Obtener el upload_id

      console.log("Filename limpio:", cleanFilename);
      console.log("Upload ID:", uploadId);

      // Construir URL con parámetros
      let predictUrl = `${API_ENDPOINTS.PREDICT}?filename=${encodeURIComponent(cleanFilename)}`;
      if (uploadId) {
        predictUrl += `&upload_id=${uploadId}`;
      }

      const predictRes = await fetch(predictUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token && { Authorization: `Bearer ${token}` }),
        },
      });

      if (!predictRes.ok) {
        throw new Error("Error al procesar el archivo");
      }

      const predictions = await predictRes.json();
      console.log("🔍 Predictions recibidas:", predictions.predictions?.length, "registros");
      console.log("✅ Carga guardada en historial con ID:", uploadId);

      console.log("🔄 REDIRECCIÓN INMEDIATA a /resultados-completos...");

      // Guardar datos procesados para que estén disponibles en Resultados completos
      localStorage.setItem("latest_predictions", JSON.stringify(predictions.predictions));
      localStorage.setItem("csv_upload_timestamp", new Date().toISOString());
      localStorage.setItem("csv_uploaded", Date.now().toString());
      localStorage.setItem("fromUpload", "true");

      // Disparar evento personalizado para actualizar dashboards
      window.dispatchEvent(
        new CustomEvent("csvUploaded", {
          detail: { predictions: predictions.predictions },
        })
      );

      // REDIRECCIÓN SIMPLE - solo la ruta sin parámetros
      navigate("/resultados-completos");
    } catch (error) {
      alert("Error al procesar el archivo");
      console.error(error);
    } finally {
      setIsProcessing(false);
    }
  };

  function excelDateToJSDate(serial) {
    // Convierte número de Excel a fecha legible DD/MM/YYYY
    const utc_days = Math.floor(serial - 25569);
    const utc_value = utc_days * 86400;
    const date_info = new Date(utc_value * 1000);
    const day = String(date_info.getDate()).padStart(2, "0");
    const month = String(date_info.getMonth() + 1).padStart(2, "0");
    const year = date_info.getFullYear();
    return `${day}/${month}/${year}`;
  }

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox mt={6} mb={3}>
        <Grid container spacing={3} justifyContent="center">
          <Grid item xs={12} md={10}>
            <Card
              sx={{
                backgroundColor: darkMode ? "transparent" : "white",
                backgroundImage: darkMode ? "none" : undefined,
              }}
            >
              <MDBox p={4}>
                <MDTypography variant="h5" mb={2} color={darkMode ? "white" : "dark"}>
                  Subir archivo CSV o Excel para análisis
                </MDTypography>
                <MDBox
                  onClick={getRootProps().onClick}
                  onKeyDown={getRootProps().onKeyDown}
                  tabIndex={getRootProps().tabIndex}
                  role={getRootProps().role}
                  sx={{
                    border: darkMode ? "2px dashed rgba(255, 255, 255, 0.3)" : "2px dashed #aaa",
                    borderRadius: "10px",
                    padding: "40px",
                    textAlign: "center",
                    backgroundColor: isDragActive
                      ? darkMode
                        ? "rgba(255, 255, 255, 0.1)"
                        : "#f0f0f0"
                      : darkMode
                      ? "rgba(255, 255, 255, 0.05)"
                      : "#fafafa",
                    cursor: "pointer",
                    transition: "all 0.3s ease",
                    "&:hover": {
                      backgroundColor: darkMode ? "rgba(255, 255, 255, 0.08)" : "#f0f0f0",
                      borderColor: darkMode ? "rgba(255, 255, 255, 0.5)" : "#888",
                    },
                  }}
                >
                  <input
                    ref={getInputProps().ref}
                    type={getInputProps().type}
                    multiple={getInputProps().multiple}
                    accept={getInputProps().accept}
                    onChange={getInputProps().onChange}
                    onClick={getInputProps().onClick}
                    style={getInputProps().style}
                    tabIndex={getInputProps().tabIndex}
                  />
                  <Icon
                    fontSize="large"
                    sx={{ color: darkMode ? "rgba(255, 255, 255, 0.7)" : "inherit" }}
                  >
                    cloud_upload
                  </Icon>
                  <MDTypography variant="body1" color={darkMode ? "white" : "dark"}>
                    {isDragActive
                      ? "Suelta el archivo aquí..."
                      : "Arrastra y suelta un archivo aquí o haz clic para seleccionar"}
                  </MDTypography>
                </MDBox>

                {fileName && (
                  <MDBox mt={2}>
                    <MDTypography variant="subtitle1" color={darkMode ? "white" : "dark"}>
                      <strong>Archivo cargado:</strong> {fileName}
                    </MDTypography>
                  </MDBox>
                )}

                {fileData.length > 0 && (
                  <MDBox mt={4} maxHeight="300px" sx={{ overflow: "auto" }}>
                    <MDTypography variant="h6" mb={1} color={darkMode ? "white" : "dark"}>
                      Vista previa:
                    </MDTypography>
                    <table style={{ width: "100%", borderCollapse: "collapse" }}>
                      <tbody>
                        {fileData.slice(0, 10).map((row, i) => (
                          <tr key={i}>
                            {row.map((cell, j) => {
                              let value = cell;
                              const isFechaCol =
                                fileData[0][j] &&
                                fileData[0][j].toString().toLowerCase().includes("fecha");
                              // Si la columna es 'fecha' y el valor es numérico, convertirlo
                              if (
                                isFechaCol &&
                                i > 0 &&
                                cell !== "" &&
                                !isNaN(Number(cell)) &&
                                Number(cell) > 30000 // rango típico de fechas Excel
                              ) {
                                value = excelDateToJSDate(Number(cell));
                              }
                              return (
                                <td
                                  key={j}
                                  style={{
                                    border: darkMode
                                      ? "1px solid rgba(255, 255, 255, 0.2)"
                                      : "1px solid #ddd",
                                    padding: "8px",
                                    fontSize: "14px",
                                    color: darkMode ? "rgba(255, 255, 255, 0.9)" : "inherit",
                                    backgroundColor:
                                      darkMode && i === 0
                                        ? "rgba(255, 255, 255, 0.05)"
                                        : "transparent",
                                  }}
                                >
                                  {value}
                                </td>
                              );
                            })}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </MDBox>
                )}

                <MDBox mt={4}>
                  <MDButton
                    variant="gradient"
                    color="info"
                    onClick={handleUpload}
                    disabled={!rawFile || isProcessing}
                  >
                    {isProcessing ? "Procesando..." : "Enviar"}
                  </MDButton>
                </MDBox>

                {/* Eliminamos la sección de resultados para que redirija correctamente */}
              </MDBox>
            </Card>
          </Grid>
        </Grid>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default UploadData;
