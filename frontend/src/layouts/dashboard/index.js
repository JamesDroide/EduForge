import React, { useEffect, useState, useCallback } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import Grid from "@mui/material/Grid";
import MDBox from "components/MDBox";
import MDAlert from "components/MDAlert";
import MDButton from "components/MDButton";
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import ReportsBarChart from "examples/Charts/BarCharts/ReportsBarChart";
import ReportsLineChart from "examples/Charts/LineCharts/ReportsLineChart";
import Projects from "layouts/dashboard/components/Projects";
import OrdersOverview from "layouts/dashboard/components/OrdersOverview";
import MediumRiskStudents from "layouts/dashboard/components/MediumRiskStudents";
import { API_ENDPOINTS } from "../../config/api";

function Dashboard() {
  const location = useLocation();
  const navigate = useNavigate();
  const [showSuccessAlert, setShowSuccessAlert] = useState(false);
  const [barChartData, setBarChartData] = useState({
    labels: ["Lun", "Mar", "Mié", "Jue", "Vie"],
    datasets: [
      {
        label: "Sin datos",
        data: [0, 0, 0, 0, 0],
        backgroundColor: "#1f77b4",
      },
    ],
  });
  const [lineChartData, setLineChartData] = useState({
    labels: [],
    datasets: {
      label: "Riesgo de deserción",
      data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    },
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const hasValidCsvData = () => {
    try {
      const storedPredictions = localStorage.getItem("latest_predictions");
      if (storedPredictions) {
        const parsedData = JSON.parse(storedPredictions);
        return parsedData && parsedData.length > 0;
      }
      return false;
    } catch (e) {
      console.warn("Error verificando datos de CSV:", e);
      return false;
    }
  };

  const loadAttendanceData = useCallback(() => {
    if (!hasValidCsvData()) {
      console.log("No hay CSV cargado, no se cargarán datos de asistencia");
      setBarChartData({
        labels: ["Lun", "Mar", "Mié", "Jue", "Vie"],
        datasets: [
          {
            label: "Sin datos",
            data: [0, 0, 0, 0, 0],
            backgroundColor: "#cccccc",
          },
        ],
      });
      return;
    }

    fetch(API_ENDPOINTS.ATTENDANCE_CHART)
      .then((res) => {
        console.log("Respuesta del servidor recibida:", res.status);
        if (!res.ok) throw new Error("No se pudo obtener asistencia");
        return res.json();
      })
      .then((data) => {
        console.log("Datos recibidos:", data);
        if (data.labels && data.datasets && data.datasets.length > 0) {
          console.log("Datos válidos encontrados:", data.datasets.length, "datasets");
          setBarChartData({
            labels: data.labels,
            datasets: data.datasets,
          });
        } else {
          console.log("No se encontraron datasets válidos");
          setBarChartData({
            labels: ["Lun", "Mar", "Mié", "Jue", "Vie"],
            datasets: [
              {
                label: "Sin datos del CSV",
                data: [0, 0, 0, 0, 0],
                backgroundColor: "#cccccc",
              },
            ],
          });
        }
      })
      .catch((err) => {
        console.error("Error cargando asistencia:", err);
        setBarChartData({
          labels: ["Lun", "Mar", "Mié", "Jue", "Vie"],
          datasets: [
            {
              label: "Sin datos",
              data: [0, 0, 0, 0, 0],
              backgroundColor: "#cccccc",
            },
          ],
        });
      });
  }, []);

  const loadRiskData = useCallback(() => {
    if (!hasValidCsvData()) {
      console.log("No hay CSV cargado, no se cargarán datos de riesgo");
      setLineChartData({
        labels: [
          "Ene",
          "Feb",
          "Mar",
          "Abr",
          "May",
          "Jun",
          "Jul",
          "Ago",
          "Sep",
          "Oct",
          "Nov",
          "Dic",
        ],
        datasets: {
          label: "Sin datos",
          data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          counts: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          totals: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
      });
      setLoading(false);
      return;
    }

    fetch(API_ENDPOINTS.RISK_SUMMARY)
      .then((res) => {
        if (!res.ok) throw new Error("No se pudo obtener riesgo de deserción");
        return res.json();
      })
      .then((data) => {
        if (data.labels && data.data) {
          setLineChartData({
            labels: data.labels,
            datasets: {
              label: "Riesgo de deserción (%)",
              data: data.data,
              counts: data.counts || [],
              totals: data.totals || [],
            },
          });
        } else {
          setError("Datos de riesgo de deserción no válidos");
        }
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error cargando riesgo:", err);
        setLineChartData({
          labels: [
            "Ene",
            "Feb",
            "Mar",
            "Abr",
            "May",
            "Jun",
            "Jul",
            "Ago",
            "Sep",
            "Oct",
            "Nov",
            "Dic",
          ],
          datasets: {
            label: "Sin datos",
            data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            counts: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            totals: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          },
        });
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    if (location.state?.message) {
      setShowSuccessAlert(true);
      setTimeout(() => {
        setShowSuccessAlert(false);
      }, 5000);
    }

    loadAttendanceData();
    loadRiskData();

    const handleStorageChange = (e) => {
      if (e.key === "csv_uploaded" && e.newValue) {
        loadAttendanceData();
        loadRiskData();
      }
    };

    const handleCsvUploaded = () => {
      console.log("Evento directo: CSV cargado, actualizando gráficos inmediatamente...");
      // Breve espera para asegurar que el backend haya persistido los datos antes de consultar
      setTimeout(() => {
        loadAttendanceData();
        loadRiskData();
      }, 1000);
    };

    window.addEventListener("storage", handleStorageChange);
    window.addEventListener("csvUploaded", handleCsvUploaded);

    return () => {
      window.removeEventListener("storage", handleStorageChange);
      window.removeEventListener("csvUploaded", handleCsvUploaded);
    };
  }, [loadAttendanceData, loadRiskData, location.state]);

  if (error) return <div style={{ color: "red", fontWeight: "bold" }}>{error}</div>;
  if (loading) return <div>Cargando datos del CSV...</div>;

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox py={3}>
        {location.state?.predictions && (
          <MDBox mb={3} textAlign="center">
            <MDButton
              variant="outlined"
              color="info"
              size="small"
              onClick={() =>
                navigate("/resultados-completos", {
                  state: { predictions: location.state.predictions },
                })
              }
            >
              Ver Resultados Detallados Completos
            </MDButton>
          </MDBox>
        )}

        <MDBox mt={4.5}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6} lg={6}>
              <MDBox mb={3}>
                <ReportsBarChart
                  color="info"
                  title="Reporte por asistencia"
                  description="Gráfico por días de la semana"
                  date="Actualizado hace 1 hora"
                  chart={barChartData}
                />
              </MDBox>
            </Grid>
            <Grid item xs={12} md={6} lg={6}>
              <MDBox mb={3}>
                <ReportsLineChart
                  color="success"
                  title="Mayor riesgo de deserción"
                  description={
                    <>
                      (<strong>Durante</strong>) el año
                    </>
                  }
                  date="Actualizado hace 1 hora"
                  chart={lineChartData}
                />
              </MDBox>
            </Grid>
          </Grid>
        </MDBox>
        <MDBox>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6} lg={6}>
              <Projects />
            </Grid>
            <Grid item xs={12} md={6} lg={6}>
              <MediumRiskStudents />
            </Grid>
          </Grid>
          <MDBox mt={3}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6} lg={4}>
                <OrdersOverview />
              </Grid>
            </Grid>
          </MDBox>
        </MDBox>
      </MDBox>
      <Footer />
      {showSuccessAlert && (
        <MDAlert
          color="success"
          dismissible
          onClose={() => setShowSuccessAlert(false)}
          sx={{ position: "fixed", top: 16, right: 16, zIndex: 999 }}
        >
          Datos actualizados correctamente desde el CSV.
        </MDAlert>
      )}
    </DashboardLayout>
  );
}

export default Dashboard;
