import { useState } from "react";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import {
  Checkbox,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
} from "@mui/material";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDButton from "components/MDButton";
import Icon from "@mui/material/Icon";
import api from "config/api";
import MDAlert from "components/MDAlert";
import { format } from "date-fns";
import { es } from "date-fns/locale";

function CompareUploads({ uploads }) {
  const [selectedUploads, setSelectedUploads] = useState([]);
  const [showComparison, setShowComparison] = useState(false);
  const [comparisonData, setComparisonData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [alert, setAlert] = useState({ show: false, message: "", color: "info" });

  const showAlert = (message, color) => {
    setAlert({ show: true, message, color });
    setTimeout(() => setAlert({ show: false, message: "", color: "info" }), 5000);
  };

  const handleSelectUpload = (uploadId) => {
    if (selectedUploads.includes(uploadId)) {
      setSelectedUploads(selectedUploads.filter((id) => id !== uploadId));
    } else {
      if (selectedUploads.length >= 5) {
        showAlert("Puedes comparar máximo 5 cargas a la vez", "warning");
        return;
      }
      setSelectedUploads([...selectedUploads, uploadId]);
    }
  };

  const handleCompare = async () => {
    if (selectedUploads.length < 2) {
      showAlert("Selecciona al menos 2 cargas para comparar", "warning");
      return;
    }

    setLoading(true);
    try {
      const response = await api.post("/api/history/compare", {
        upload_ids: selectedUploads,
      });
      setComparisonData(response.data);
      setShowComparison(true);
    } catch (error) {
      console.error("Error comparando cargas:", error);
      showAlert("Error al comparar las cargas", "error");
    } finally {
      setLoading(false);
    }
  };

  const handleClearSelection = () => {
    setSelectedUploads([]);
  };

  return (
    <>
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

      {/* Barra de acciones con diseño mejorado */}
      <MDBox
        mb={3}
        p={3}
        sx={{
          background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
          borderRadius: 3,
          boxShadow: "0 8px 32px 0 rgba(102, 126, 234, 0.37)",
          backdropFilter: "blur(4px)",
          border: "1px solid rgba(255, 255, 255, 0.18)",
        }}
      >
        <Grid container alignItems="center" spacing={3}>
          <Grid item xs={12} md={6}>
            <MDBox
              display="flex"
              alignItems="center"
              justifyContent={{ xs: "center", md: "flex-start" }}
              gap={2}
            >
              <MDBox
                sx={{
                  backgroundColor: "rgba(255, 255, 255, 0.25)",
                  borderRadius: "50%",
                  width: 48,
                  height: 48,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  boxShadow: "0 4px 15px rgba(0,0,0,0.2)",
                }}
              >
                <Icon sx={{ color: "white", fontSize: 28 }}>playlist_add_check</Icon>
              </MDBox>
              <MDBox>
                <MDTypography variant="h4" color="white" fontWeight="bold">
                  {selectedUploads.length}
                </MDTypography>
                <MDTypography variant="caption" color="white" sx={{ opacity: 0.9 }}>
                  de 5 cargas seleccionadas
                </MDTypography>
              </MDBox>
            </MDBox>
          </Grid>
          <Grid item xs={12} md={6}>
            <MDBox
              display="flex"
              gap={1.5}
              justifyContent={{ xs: "center", md: "flex-end" }}
              flexWrap="wrap"
            >
              {selectedUploads.length > 0 && (
                <>
                  <MDButton
                    variant="outlined"
                    color="white"
                    size="small"
                    onClick={handleClearSelection}
                    sx={{
                      fontSize: "0.75rem",
                      padding: "8px 16px",
                      borderWidth: 2,
                      borderRadius: 2,
                      textTransform: "none",
                      fontWeight: "600",
                      minWidth: "100px",
                      "&:hover": {
                        borderWidth: 2,
                        backgroundColor: "rgba(255,255,255,0.15)",
                        transform: "translateY(-2px)",
                        boxShadow: "0 4px 12px rgba(0,0,0,0.2)",
                      },
                      transition: "all 0.3s ease",
                    }}
                  >
                    <Icon sx={{ fontSize: 16, mr: 0.5 }}>clear</Icon>
                    Limpiar
                  </MDButton>
                  <MDButton
                    variant="contained"
                    color="white"
                    size="small"
                    onClick={handleCompare}
                    disabled={loading || selectedUploads.length < 2}
                    sx={{
                      fontSize: "0.75rem",
                      padding: "8px 20px",
                      borderRadius: 2,
                      textTransform: "none",
                      fontWeight: "bold",
                      minWidth: "120px",
                      color: "#667eea",
                      boxShadow: "0 4px 15px rgba(0,0,0,0.2)",
                      "&:hover": {
                        backgroundColor: "#f8f9fa",
                        transform: "translateY(-2px)",
                        boxShadow: "0 6px 20px rgba(0,0,0,0.25)",
                      },
                      "&:disabled": {
                        backgroundColor: "rgba(255,255,255,0.5)",
                        color: "rgba(102, 126, 234, 0.5)",
                      },
                      transition: "all 0.3s ease",
                    }}
                  >
                    {loading ? (
                      <>
                        <CircularProgress size={16} sx={{ mr: 1, color: "#667eea" }} />
                        Comparando...
                      </>
                    ) : (
                      <>
                        <Icon sx={{ fontSize: 16, mr: 0.5 }}>compare_arrows</Icon>
                        Comparar
                      </>
                    )}
                  </MDButton>
                </>
              )}
            </MDBox>
          </Grid>
        </Grid>
      </MDBox>

      {/* Lista de cargas con checkboxes más grandes y notorios */}
      <MDBox>
        {uploads.map((upload) => {
          const isSelected = selectedUploads.includes(upload.id);
          return (
            <Card
              key={upload.id}
              onClick={() => handleSelectUpload(upload.id)}
              sx={{
                mb: 2,
                p: 2.5,
                cursor: "pointer",
                border: isSelected ? "3px solid #667eea" : "2px solid #e0e0e0",
                backgroundColor: isSelected ? "rgba(102, 126, 234, 0.08)" : "white",
                borderRadius: 2,
                transition: "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                position: "relative",
                overflow: "hidden",
                "&:hover": {
                  transform: "translateY(-4px)",
                  boxShadow: isSelected
                    ? "0 12px 40px rgba(102, 126, 234, 0.3)"
                    : "0 8px 24px rgba(0,0,0,0.15)",
                  borderColor: "#667eea",
                },
                "&::before": isSelected
                  ? {
                      content: '""',
                      position: "absolute",
                      top: 0,
                      left: 0,
                      right: 0,
                      height: "4px",
                      background: "linear-gradient(90deg, #667eea 0%, #764ba2 100%)",
                    }
                  : {},
              }}
            >
              <MDBox display="flex" alignItems="center" gap={2}>
                <MDBox
                  sx={{
                    position: "relative",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  <Checkbox
                    checked={isSelected}
                    onChange={() => handleSelectUpload(upload.id)}
                    onClick={(e) => e.stopPropagation()}
                    sx={{
                      transform: "scale(1.5)",
                      color: "#667eea",
                      padding: "12px",
                      "&.Mui-checked": {
                        color: "#667eea",
                        animation: "checkboxPulse 0.3s ease",
                      },
                      "& .MuiSvgIcon-root": {
                        fontSize: 32,
                        filter: isSelected
                          ? "drop-shadow(0 2px 4px rgba(102, 126, 234, 0.4))"
                          : "none",
                      },
                      "&:hover": {
                        backgroundColor: "rgba(102, 126, 234, 0.1)",
                      },
                      "@keyframes checkboxPulse": {
                        "0%": {
                          transform: "scale(1.5)",
                        },
                        "50%": {
                          transform: "scale(1.7)",
                        },
                        "100%": {
                          transform: "scale(1.5)",
                        },
                      },
                    }}
                  />
                </MDBox>
                <MDBox flex={1}>
                  <MDBox display="flex" alignItems="center" gap={1} mb={1}>
                    <Icon
                      sx={{
                        color: isSelected ? "#667eea" : "info.main",
                        fontSize: 22,
                        transition: "all 0.3s ease",
                      }}
                    >
                      description
                    </Icon>
                    <MDTypography
                      variant="button"
                      fontWeight="bold"
                      color={isSelected ? "info" : "dark"}
                      sx={{
                        fontSize: "0.95rem",
                        transition: "all 0.3s ease",
                      }}
                    >
                      {upload.original_filename}
                    </MDTypography>
                  </MDBox>
                  <MDBox display="flex" gap={3} flexWrap="wrap">
                    <MDBox display="flex" alignItems="center" gap={0.5}>
                      <Icon sx={{ fontSize: 18, color: "text.secondary" }}>event</Icon>
                      <MDTypography variant="caption" color="text" fontWeight="medium">
                        {format(new Date(upload.upload_date), "dd/MM/yyyy HH:mm", { locale: es })}
                      </MDTypography>
                    </MDBox>
                    <MDBox display="flex" alignItems="center" gap={0.5}>
                      <Icon sx={{ fontSize: 18, color: "text.secondary" }}>group</Icon>
                      <MDTypography variant="caption" color="text" fontWeight="medium">
                        {upload.total_students} estudiantes
                      </MDTypography>
                    </MDBox>
                    <MDBox display="flex" alignItems="center" gap={0.5}>
                      <Icon sx={{ fontSize: 18, color: "error.main" }}>warning</Icon>
                      <MDTypography variant="caption" color="error" fontWeight="bold">
                        {upload.high_risk_count} en riesgo alto ({upload.high_risk_percentage}%)
                      </MDTypography>
                    </MDBox>
                  </MDBox>
                </MDBox>
                {isSelected && (
                  <MDBox
                    sx={{
                      background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                      color: "white",
                      borderRadius: "50%",
                      width: 40,
                      height: 40,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      boxShadow: "0 4px 15px rgba(102, 126, 234, 0.4)",
                      animation: "scaleIn 0.3s ease",
                      "@keyframes scaleIn": {
                        "0%": {
                          transform: "scale(0)",
                        },
                        "50%": {
                          transform: "scale(1.2)",
                        },
                        "100%": {
                          transform: "scale(1)",
                        },
                      },
                    }}
                  >
                    <Icon sx={{ fontSize: 24 }}>check</Icon>
                  </MDBox>
                )}
              </MDBox>
            </Card>
          );
        })}
      </MDBox>

      {/* Dialog de Comparación */}
      <Dialog
        open={showComparison}
        onClose={() => setShowComparison(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          <MDBox display="flex" justifyContent="space-between" alignItems="center">
            <MDBox display="flex" alignItems="center" gap={1}>
              <Icon color="info" sx={{ fontSize: 28 }}>
                analytics
              </Icon>
              <MDTypography variant="h5">Comparación de Cargas CSV</MDTypography>
            </MDBox>
            <MDButton
              variant="text"
              color="secondary"
              size="small"
              onClick={() => setShowComparison(false)}
              iconOnly
              circular
            >
              <Icon>close</Icon>
            </MDButton>
          </MDBox>
        </DialogTitle>
        <DialogContent>
          {comparisonData && (
            <>
              {/* Tabla de Comparación */}
              <TableContainer component={Paper} sx={{ mt: 2, boxShadow: 3 }}>
                <Table>
                  <TableHead>
                    <TableRow sx={{ backgroundColor: "#f5f5f5" }}>
                      <TableCell sx={{ fontWeight: "bold", fontSize: "0.875rem" }}>
                        Métrica
                      </TableCell>
                      {comparisonData.uploads.map((upload) => (
                        <TableCell key={upload.id} align="center">
                          <MDBox>
                            <MDTypography variant="caption" fontWeight="bold">
                              {upload.filename}
                            </MDTypography>
                            <MDTypography variant="caption" color="text" display="block">
                              {format(new Date(upload.upload_date), "dd/MM/yy", { locale: es })}
                            </MDTypography>
                          </MDBox>
                        </TableCell>
                      ))}
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {/* Total de Estudiantes */}
                    <TableRow>
                      <TableCell>
                        <MDBox display="flex" alignItems="center" gap={1}>
                          <Icon>group</Icon>
                          <span>Total de Estudiantes</span>
                        </MDBox>
                      </TableCell>
                      {comparisonData.uploads.map((upload) => (
                        <TableCell key={upload.id} align="center">
                          <MDTypography variant="h6" fontWeight="bold">
                            {upload.total_students}
                          </MDTypography>
                        </TableCell>
                      ))}
                    </TableRow>

                    {/* Riesgo Alto */}
                    <TableRow sx={{ backgroundColor: "rgba(244, 67, 54, 0.05)" }}>
                      <TableCell>
                        <MDBox display="flex" alignItems="center" gap={1}>
                          <Icon color="error">warning</Icon>
                          <span>Riesgo Alto</span>
                        </MDBox>
                      </TableCell>
                      {comparisonData.uploads.map((upload) => (
                        <TableCell key={upload.id} align="center">
                          <MDTypography variant="h6" color="error" fontWeight="bold">
                            {upload.high_risk_count}
                          </MDTypography>
                          <MDTypography variant="caption" color="text">
                            ({upload.high_risk_percentage}%)
                          </MDTypography>
                        </TableCell>
                      ))}
                    </TableRow>

                    {/* Riesgo Medio */}
                    <TableRow sx={{ backgroundColor: "rgba(255, 152, 0, 0.05)" }}>
                      <TableCell>
                        <MDBox display="flex" alignItems="center" gap={1}>
                          <Icon color="warning">info</Icon>
                          <span>Riesgo Medio</span>
                        </MDBox>
                      </TableCell>
                      {comparisonData.uploads.map((upload) => (
                        <TableCell key={upload.id} align="center">
                          <MDTypography variant="h6" color="warning" fontWeight="bold">
                            {upload.medium_risk_count}
                          </MDTypography>
                          <MDTypography variant="caption" color="text">
                            ({upload.medium_risk_percentage}%)
                          </MDTypography>
                        </TableCell>
                      ))}
                    </TableRow>

                    {/* Riesgo Bajo */}
                    <TableRow sx={{ backgroundColor: "rgba(76, 175, 80, 0.05)" }}>
                      <TableCell>
                        <MDBox display="flex" alignItems="center" gap={1}>
                          <Icon color="success">check_circle</Icon>
                          <span>Riesgo Bajo</span>
                        </MDBox>
                      </TableCell>
                      {comparisonData.uploads.map((upload) => (
                        <TableCell key={upload.id} align="center">
                          <MDTypography variant="h6" color="success" fontWeight="bold">
                            {upload.low_risk_count}
                          </MDTypography>
                          <MDTypography variant="caption" color="text">
                            ({upload.low_risk_percentage}%)
                          </MDTypography>
                        </TableCell>
                      ))}
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>

              {/* Análisis Visual */}
              <MDBox mt={3}>
                <MDTypography variant="h6" mb={2}>
                  <Icon>bar_chart</Icon> Análisis Visual
                </MDTypography>
                <Grid container spacing={2}>
                  {comparisonData.uploads.map((upload) => {
                    const totalRisk = upload.high_risk_count + upload.medium_risk_count;
                    const riskPercentage = ((totalRisk / upload.total_students) * 100).toFixed(1);

                    return (
                      <Grid
                        item
                        xs={12 / Math.min(comparisonData.uploads.length, 3)}
                        key={upload.id}
                      >
                        <Card sx={{ p: 2, textAlign: "center", boxShadow: 2 }}>
                          <MDTypography variant="caption" fontWeight="bold" display="block" mb={1}>
                            {upload.filename}
                          </MDTypography>
                          <MDBox mt={2}>
                            <MDTypography variant="h3" color="info" fontWeight="bold">
                              {riskPercentage}%
                            </MDTypography>
                            <MDTypography variant="caption" color="text">
                              En riesgo total
                            </MDTypography>
                          </MDBox>
                          <MDBox mt={2}>
                            <MDBox
                              sx={{
                                height: 120,
                                background: `linear-gradient(to top, 
                                  #4caf50 0%, 
                                  #4caf50 ${upload.low_risk_percentage}%, 
                                  #ff9800 ${upload.low_risk_percentage}%, 
                                  #ff9800 ${
                                    upload.low_risk_percentage + upload.medium_risk_percentage
                                  }%, 
                                  #f44336 ${
                                    upload.low_risk_percentage + upload.medium_risk_percentage
                                  }%, 
                                  #f44336 100%)`,
                                borderRadius: 2,
                                position: "relative",
                                boxShadow: "inset 0 0 10px rgba(0,0,0,0.1)",
                              }}
                            >
                              <MDBox
                                sx={{
                                  position: "absolute",
                                  top: "50%",
                                  left: "50%",
                                  transform: "translate(-50%, -50%)",
                                  backgroundColor: "rgba(0,0,0,0.7)",
                                  borderRadius: 2,
                                  padding: "8px 16px",
                                }}
                              >
                                <MDTypography variant="h5" color="white" fontWeight="bold">
                                  {upload.total_students}
                                </MDTypography>
                                <MDTypography variant="caption" color="white">
                                  estudiantes
                                </MDTypography>
                              </MDBox>
                            </MDBox>
                          </MDBox>
                        </Card>
                      </Grid>
                    );
                  })}
                </Grid>
              </MDBox>

              {/* Resumen */}
              <MDBox
                mt={3}
                p={3}
                sx={{
                  background: "linear-gradient(195deg, #42424a 0%, #191919 100%)",
                  borderRadius: 2,
                  boxShadow: 3,
                }}
              >
                <MDBox display="flex" alignItems="center" gap={1} mb={2}>
                  <Icon sx={{ color: "white", fontSize: 28 }}>summarize</Icon>
                  <MDTypography variant="h6" color="white" fontWeight="bold">
                    Resumen General
                  </MDTypography>
                </MDBox>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={4}>
                    <MDTypography variant="body2" color="white">
                      <Icon sx={{ fontSize: 16, verticalAlign: "middle", mr: 1 }}>upload_file</Icon>
                      {comparisonData.uploads.length} cargas comparadas
                    </MDTypography>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <MDTypography variant="body2" color="white">
                      <Icon sx={{ fontSize: 16, verticalAlign: "middle", mr: 1 }}>group</Icon>
                      {comparisonData.uploads.reduce((acc, u) => acc + u.total_students, 0)}{" "}
                      estudiantes en total
                    </MDTypography>
                  </Grid>
                  <Grid item xs={12} md={4}>
                    <MDTypography variant="body2" color="white">
                      <Icon sx={{ fontSize: 16, verticalAlign: "middle", mr: 1 }}>warning</Icon>
                      {comparisonData.uploads.reduce((acc, u) => acc + u.high_risk_count, 0)} en
                      riesgo alto acumulado
                    </MDTypography>
                  </Grid>
                </Grid>
              </MDBox>
            </>
          )}
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <MDButton onClick={() => setShowComparison(false)} variant="gradient" color="dark">
            Cerrar
          </MDButton>
        </DialogActions>
      </Dialog>
    </>
  );
}

export default CompareUploads;
