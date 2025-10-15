import { useState, useEffect, useCallback } from "react";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import {
  Chip,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Tooltip,
  IconButton,
  Tabs,
  Tab,
} from "@mui/material";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDButton from "components/MDButton";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import DataTable from "examples/Tables/DataTable";
import Icon from "@mui/material/Icon";
import api from "config/api";
import MDAlert from "components/MDAlert";
import { format } from "date-fns";
import { es } from "date-fns/locale";
import CompareUploads from "./components/CompareUploads";

function UploadHistory() {
  const [uploads, setUploads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedUpload, setSelectedUpload] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [showPredictions, setShowPredictions] = useState(false);
  const [loadingPredictions, setLoadingPredictions] = useState(false);
  const [statistics, setStatistics] = useState(null);
  const [alert, setAlert] = useState({ show: false, message: "", color: "info" });
  const [viewMode, setViewMode] = useState(0); // 0: Lista, 1: Comparar

  const showAlert = (message, color) => {
    setAlert({ show: true, message, color });
    setTimeout(() => setAlert({ show: false, message: "", color: "info" }), 5000);
  };

  const fetchStatistics = useCallback(async () => {
    try {
      const response = await api.get("/api/history/statistics/summary");
      setStatistics(response.data);
    } catch (error) {
      console.error("Error cargando estadísticas:", error);
    }
  }, []);

  const fetchUploadHistory = useCallback(async () => {
    try {
      setLoading(true);
      const response = await api.get("/api/history", {
        params: { search: searchQuery },
      });
      setUploads(response.data);
    } catch (error) {
      console.error("Error cargando historial:", error);
      showAlert("Error al cargar el historial", "error");
    } finally {
      setLoading(false);
    }
  }, [searchQuery]);

  useEffect(() => {
    fetchUploadHistory();
    fetchStatistics();
  }, [fetchUploadHistory, fetchStatistics]);

  const fetchPredictions = async (uploadId) => {
    try {
      setLoadingPredictions(true);
      const response = await api.get(`/api/history/${uploadId}/predictions`);
      setPredictions(response.data);
      setShowPredictions(true);
    } catch (error) {
      console.error("Error cargando predicciones:", error);
      showAlert("Error al cargar las predicciones", "error");
    } finally {
      setLoadingPredictions(false);
    }
  };

  const handleViewPredictions = (upload) => {
    setSelectedUpload(upload);
    fetchPredictions(upload.id);
  };

  const handleDeleteUpload = async (uploadId) => {
    if (
      !window.confirm("¿Estás seguro de eliminar esta carga? Esta acción no se puede deshacer.")
    ) {
      return;
    }

    try {
      await api.delete(`/api/history/${uploadId}`);
      showAlert("Carga eliminada exitosamente", "success");
      fetchUploadHistory();
      fetchStatistics();
    } catch (error) {
      console.error("Error eliminando carga:", error);
      showAlert("Error al eliminar la carga", "error");
    }
  };

  const handleDownloadCSV = async (uploadId, filename) => {
    try {
      const response = await api.get(`/api/history/${uploadId}/download`, {
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      showAlert("Archivo descargado exitosamente", "success");
    } catch (error) {
      console.error("Error descargando CSV:", error);
      showAlert("Error al descargar el archivo", "error");
    }
  };

  const handleExportPredictions = async (uploadId, exportFormat) => {
    try {
      const response = await api.get(`/api/history/${uploadId}/export`, {
        params: { format: exportFormat },
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute(
        "download",
        `predicciones_${uploadId}.${exportFormat === "excel" ? "xlsx" : "csv"}`
      );
      document.body.appendChild(link);
      link.click();
      link.remove();
      showAlert("Predicciones exportadas exitosamente", "success");
    } catch (error) {
      console.error("Error exportando predicciones:", error);
      showAlert("Error al exportar las predicciones", "error");
    }
  };

  const getStatusChip = (status) => {
    const statusConfig = {
      success: { color: "success", label: "Exitoso" },
      error: { color: "error", label: "Error" },
      partial: { color: "warning", label: "Parcial" },
      processing: { color: "info", label: "Procesando" },
    };
    const config = statusConfig[status] || statusConfig.processing;
    return <Chip label={config.label} color={config.color} size="small" />;
  };

  const getRiskChip = (riesgo) => {
    const riskConfig = {
      Alto: { color: "error", icon: "warning" },
      Medio: { color: "warning", icon: "info" },
      Bajo: { color: "success", icon: "check_circle" },
    };
    const config = riskConfig[riesgo] || riskConfig.Bajo;
    return (
      <Chip label={riesgo} color={config.color} size="small" icon={<Icon>{config.icon}</Icon>} />
    );
  };

  const uploadsTableData = {
    columns: [
      { Header: "archivo", accessor: "filename", width: "25%" },
      { Header: "fecha", accessor: "date", width: "15%" },
      { Header: "usuario", accessor: "user", width: "15%" },
      { Header: "estudiantes", accessor: "students", align: "center", width: "10%" },
      { Header: "riesgo alto", accessor: "high_risk", align: "center", width: "10%" },
      { Header: "estado", accessor: "status", align: "center", width: "10%" },
      { Header: "acciones", accessor: "actions", align: "center", width: "15%" },
    ],
    rows: uploads.map((upload) => ({
      filename: (
        <MDBox>
          <MDTypography variant="caption" fontWeight="medium">
            {upload.original_filename}
          </MDTypography>
          <MDTypography variant="caption" color="text" display="block">
            {upload.processed_students} procesados
          </MDTypography>
        </MDBox>
      ),
      date: (
        <MDTypography variant="caption">
          {format(new Date(upload.upload_date), "dd/MM/yyyy HH:mm", { locale: es })}
        </MDTypography>
      ),
      user: (
        <MDTypography variant="caption">{upload.user_full_name || upload.username}</MDTypography>
      ),
      students: (
        <MDTypography variant="caption" fontWeight="medium">
          {upload.total_students}
        </MDTypography>
      ),
      high_risk: (
        <MDBox>
          <MDTypography variant="caption" fontWeight="bold" color="error">
            {upload.high_risk_count}
          </MDTypography>
          <MDTypography variant="caption" color="text" display="block">
            ({upload.high_risk_percentage}%)
          </MDTypography>
        </MDBox>
      ),
      status: getStatusChip(upload.status),
      actions: (
        <MDBox display="flex" gap={1} justifyContent="center">
          <Tooltip title="Ver predicciones">
            <IconButton size="small" color="info" onClick={() => handleViewPredictions(upload)}>
              <Icon>visibility</Icon>
            </IconButton>
          </Tooltip>
          <Tooltip title="Descargar CSV">
            <IconButton
              size="small"
              color="primary"
              onClick={() => handleDownloadCSV(upload.id, upload.original_filename)}
            >
              <Icon>download</Icon>
            </IconButton>
          </Tooltip>
          <Tooltip title="Eliminar">
            <IconButton size="small" color="error" onClick={() => handleDeleteUpload(upload.id)}>
              <Icon>delete</Icon>
            </IconButton>
          </Tooltip>
        </MDBox>
      ),
    })),
  };

  const predictionsTableData = {
    columns: [
      { Header: "ID", accessor: "id", width: "8%" },
      { Header: "nombre", accessor: "nombre", width: "25%" },
      { Header: "nota", accessor: "nota", align: "center", width: "10%" },
      { Header: "asistencia", accessor: "asistencia", align: "center", width: "12%" },
      { Header: "conducta", accessor: "conducta", align: "center", width: "12%" },
      { Header: "riesgo", accessor: "riesgo", align: "center", width: "13%" },
      { Header: "probabilidad", accessor: "probabilidad", align: "center", width: "15%" },
    ],
    rows: predictions.map((pred) => ({
      id: (
        <MDTypography variant="caption" fontWeight="medium">
          {pred.estudiante_id}
        </MDTypography>
      ),
      nombre: <MDTypography variant="caption">{pred.nombre || "Sin nombre"}</MDTypography>,
      nota: (
        <MDTypography variant="caption" fontWeight="medium">
          {pred.nota_final?.toFixed(2)}
        </MDTypography>
      ),
      asistencia: <MDTypography variant="caption">{pred.asistencia?.toFixed(1)}%</MDTypography>,
      conducta: <Chip label={pred.conducta || "N/A"} size="small" variant="outlined" />,
      riesgo: getRiskChip(pred.riesgo_desercion),
      probabilidad: (
        <MDTypography
          variant="caption"
          fontWeight="bold"
          color={
            pred.probabilidad_desercion > 0.7
              ? "error"
              : pred.probabilidad_desercion > 0.4
              ? "warning"
              : "success"
          }
        >
          {(pred.probabilidad_desercion * 100).toFixed(1)}%
        </MDTypography>
      ),
    })),
  };

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox pt={6} pb={3}>
        {alert.show && (
          <MDBox mb={2}>
            <MDAlert
              color={alert.color}
              dismissible
              onClose={() => setAlert({ ...alert, show: false })}
            >
              {alert.message}
            </MDAlert>
          </MDBox>
        )}

        {/* Estadísticas Generales */}
        {statistics && (
          <Grid container spacing={3} mb={3}>
            <Grid item xs={12} md={3}>
              <Card>
                <MDBox p={2} textAlign="center">
                  <MDTypography variant="h4" fontWeight="bold" color="info">
                    {statistics.total_uploads}
                  </MDTypography>
                  <MDTypography variant="caption" color="text">
                    Total de Cargas
                  </MDTypography>
                </MDBox>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <MDBox p={2} textAlign="center">
                  <MDTypography variant="h4" fontWeight="bold" color="success">
                    {statistics.total_students_processed}
                  </MDTypography>
                  <MDTypography variant="caption" color="text">
                    Estudiantes Procesados
                  </MDTypography>
                </MDBox>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <MDBox p={2} textAlign="center">
                  <MDTypography variant="h4" fontWeight="bold" color="error">
                    {statistics.total_high_risk}
                  </MDTypography>
                  <MDTypography variant="caption" color="text">
                    En Riesgo Alto
                  </MDTypography>
                </MDBox>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card>
                <MDBox p={2} textAlign="center">
                  <MDTypography variant="h4" fontWeight="bold" color="dark">
                    {statistics.uploads_last_30_days}
                  </MDTypography>
                  <MDTypography variant="caption" color="text">
                    Últimos 30 días
                  </MDTypography>
                </MDBox>
              </Card>
            </Grid>
          </Grid>
        )}

        {/* Tabla de Historial */}
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Card>
              <MDBox
                mx={2}
                mt={-3}
                py={3}
                px={2}
                variant="gradient"
                bgColor="info"
                borderRadius="lg"
                coloredShadow="info"
              >
                <Grid container alignItems="center" spacing={2}>
                  {/* Título centrado */}
                  <Grid item xs={12} md={4}>
                    <MDTypography variant="h5" color="white" fontWeight="bold">
                      Historial de Cargas CSV
                    </MDTypography>
                  </Grid>

                  {/* Tabs centrados */}
                  <Grid item xs={12} md={4} sx={{ display: "flex", justifyContent: "center" }}>
                    <Tabs
                      value={viewMode}
                      onChange={(e, newValue) => setViewMode(newValue)}
                      sx={{
                        minHeight: 36,
                        "& .MuiTabs-indicator": {
                          backgroundColor: "white",
                          height: 3,
                        },
                        "& .MuiTab-root": {
                          color: "rgba(255,255,255,0.7)",
                          minHeight: 36,
                          fontSize: "0.875rem",
                          fontWeight: 500,
                          textTransform: "none",
                          padding: "6px 16px",
                          "&:hover": {
                            color: "white",
                            backgroundColor: "rgba(255,255,255,0.1)",
                          },
                        },
                        "& .Mui-selected": {
                          color: "white !important",
                          fontWeight: "bold",
                        },
                      }}
                    >
                      <Tab
                        icon={<Icon sx={{ fontSize: 18 }}>list</Icon>}
                        iconPosition="start"
                        label="Lista"
                      />
                      <Tab
                        icon={<Icon sx={{ fontSize: 18 }}>compare_arrows</Icon>}
                        iconPosition="start"
                        label="Comparar"
                      />
                    </Tabs>
                  </Grid>

                  {/* Buscador a la derecha */}
                  <Grid item xs={12} md={4}>
                    {viewMode === 0 && (
                      <MDBox display="flex" gap={1} justifyContent="flex-end">
                        <TextField
                          placeholder="Buscar archivo..."
                          size="small"
                          value={searchQuery}
                          onChange={(e) => setSearchQuery(e.target.value)}
                          InputProps={{
                            startAdornment: (
                              <Icon sx={{ mr: 1, color: "text.secondary" }}>search</Icon>
                            ),
                          }}
                          sx={{
                            backgroundColor: "white",
                            borderRadius: 1,
                            "& .MuiOutlinedInput-root": {
                              fontSize: "0.875rem",
                              "&:hover": {
                                boxShadow: "0 0 0 2px rgba(255,255,255,0.3)",
                              },
                              "&.Mui-focused": {
                                boxShadow: "0 0 0 2px rgba(255,255,255,0.5)",
                              },
                            },
                          }}
                        />
                        <MDButton
                          variant="contained"
                          color="white"
                          size="small"
                          onClick={fetchUploadHistory}
                          sx={{
                            minWidth: "auto",
                            padding: "6px 16px",
                            fontSize: "0.875rem",
                            fontWeight: 500,
                          }}
                        >
                          <Icon sx={{ fontSize: 18 }}>search</Icon>
                          &nbsp;Buscar
                        </MDButton>
                      </MDBox>
                    )}
                  </Grid>
                </Grid>
              </MDBox>
              <MDBox pt={3}>
                {loading ? (
                  <MDBox display="flex" justifyContent="center" p={3}>
                    <CircularProgress />
                  </MDBox>
                ) : uploads.length === 0 ? (
                  <MDBox p={3} textAlign="center">
                    <MDTypography variant="h6" color="text">
                      No hay cargas en el historial
                    </MDTypography>
                    <MDTypography variant="caption" color="text">
                      Sube un archivo CSV para comenzar
                    </MDTypography>
                  </MDBox>
                ) : (
                  <MDBox p={3}>
                    {viewMode === 0 ? (
                      <DataTable
                        table={uploadsTableData}
                        isSorted={false}
                        entriesPerPage={false}
                        showTotalEntries={false}
                        noEndBorder
                      />
                    ) : (
                      <CompareUploads uploads={uploads} />
                    )}
                  </MDBox>
                )}
              </MDBox>
            </Card>
          </Grid>
        </Grid>

        {/* Dialog de Predicciones */}
        <Dialog
          open={showPredictions}
          onClose={() => setShowPredictions(false)}
          maxWidth="lg"
          fullWidth
        >
          <DialogTitle>
            <MDBox display="flex" justifyContent="space-between" alignItems="center">
              <MDTypography variant="h5">
                Predicciones - {selectedUpload?.original_filename}
              </MDTypography>
              <MDBox display="flex" gap={1}>
                <MDButton
                  variant="outlined"
                  color="info"
                  size="small"
                  onClick={() => handleExportPredictions(selectedUpload?.id, "csv")}
                >
                  <Icon>download</Icon>&nbsp;CSV
                </MDButton>
                <MDButton
                  variant="outlined"
                  color="success"
                  size="small"
                  onClick={() => handleExportPredictions(selectedUpload?.id, "excel")}
                >
                  <Icon>download</Icon>&nbsp;Excel
                </MDButton>
              </MDBox>
            </MDBox>
            {selectedUpload && (
              <MDBox mt={2}>
                <Grid container spacing={2}>
                  <Grid item xs={3}>
                    <MDTypography variant="caption" color="text">
                      Procesados: <strong>{selectedUpload.processed_students}</strong>
                    </MDTypography>
                  </Grid>
                  <Grid item xs={3}>
                    <MDTypography variant="caption" color="error">
                      Riesgo Alto: <strong>{selectedUpload.high_risk_count}</strong>
                    </MDTypography>
                  </Grid>
                  <Grid item xs={3}>
                    <MDTypography variant="caption" color="warning">
                      Riesgo Medio: <strong>{selectedUpload.medium_risk_count}</strong>
                    </MDTypography>
                  </Grid>
                  <Grid item xs={3}>
                    <MDTypography variant="caption" color="success">
                      Riesgo Bajo: <strong>{selectedUpload.low_risk_count}</strong>
                    </MDTypography>
                  </Grid>
                </Grid>
              </MDBox>
            )}
          </DialogTitle>
          <DialogContent>
            {loadingPredictions ? (
              <MDBox display="flex" justifyContent="center" p={3}>
                <CircularProgress />
              </MDBox>
            ) : (
              <DataTable
                table={predictionsTableData}
                isSorted={false}
                entriesPerPage={{ defaultValue: 10, entries: [10, 25, 50, 100] }}
                showTotalEntries
                noEndBorder
              />
            )}
          </DialogContent>
          <DialogActions>
            <MDButton onClick={() => setShowPredictions(false)} color="secondary">
              Cerrar
            </MDButton>
          </DialogActions>
        </Dialog>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default UploadHistory;
