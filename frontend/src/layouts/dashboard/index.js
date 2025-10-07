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
import Grid from "@mui/material/Grid";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";

// Material Dashboard 2 React example components
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";
import ReportsBarChart from "examples/Charts/BarCharts/ReportsBarChart";
import ReportsLineChart from "examples/Charts/LineCharts/ReportsLineChart";
import ComplexStatisticsCard from "examples/Cards/StatisticsCards/ComplexStatisticsCard";

// Data
import reportsBarChartDataDefault from "layouts/dashboard/data/reportsBarChartData";
import reportsLineChartDataDefault from "layouts/dashboard/data/reportsLineChartData";

// Dashboard components
import Projects from "layouts/dashboard/components/Projects";
import OrdersOverview from "layouts/dashboard/components/OrdersOverview";
import MediumRiskStudents from "layouts/dashboard/components/MediumRiskStudents";
import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import MDAlert from "components/MDAlert";
import MDButton from "components/MDButton";

function Dashboard() {
  const location = useLocation();
  const navigate = useNavigate();
  const [showSuccessAlert, setShowSuccessAlert] = useState(false);
  // Estado para los datos de los gráficos
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

  // Función para verificar si hay datos de CSV válidos
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

  // Función para cargar datos de asistencia usando el nuevo endpoint con datos reales del CSV
  const loadAttendanceData = () => {
    // Solo cargar datos si hay un CSV válido
    if (!hasValidCsvData()) {
      console.log("📭 No hay CSV cargado, mostrando estado vacío para asistencia");
      setBarChartData({
        labels: ["Lun", "Mar", "Mié", "Jue", "Vie"],
        datasets: [
          {
            label: "No hay datos - Cargar CSV",
            data: [0, 0, 0, 0, 0],
            backgroundColor: "#cccccc",
          },
        ],
      });
      return;
    }

    console.log("🔄 Cargando datos de asistencia...");
    fetch("http://localhost:8000/dashboard_attendance/attendance_chart_real")
      .then((res) => {
        console.log("📡 Respuesta del servidor recibida:", res.status);
        if (!res.ok) throw new Error("No se pudo obtener asistencia");
        return res.json();
      })
      .then((data) => {
        console.log("📊 Datos recibidos:", data);
        if (data.labels && data.datasets && data.datasets.length > 0) {
          console.log("✅ Datos válidos encontrados:", data.datasets.length, "datasets");
          setBarChartData({
            labels: data.labels, // Días de semana en X
            datasets: data.datasets, // Cada mes como serie separada
          });
        } else {
          console.log("⚠️ No se encontraron datasets válidos");
          // Fallback a datos simples si no hay datasets
          setBarChartData({
            labels: ["Lun", "Mar", "Mié", "Jue", "Vie"],
            datasets: [
              {
                label: "Sin datos del CSV",
                data: [0, 0, 0, 0, 0],
                backgroundColor: "#1f77b4",
              },
            ],
          });
        }
      })
      .catch((err) => {
        console.error("❌ Error cargando asistencia:", err);
        setBarChartData({
          labels: ["Lun", "Mar", "Mié", "Jue", "Vie"],
          datasets: [
            {
              label: "Error al cargar",
              data: [0, 0, 0, 0, 0],
              backgroundColor: "#ff4444",
            },
          ],
        });
      });
  };

  // Función para cargar datos de riesgo
  const loadRiskData = () => {
    // Solo cargar datos si hay un CSV válido
    if (!hasValidCsvData()) {
      console.log("📭 No hay CSV cargado, mostrando estado vacío para riesgo");
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
          label: "No hay datos - Cargar CSV",
          data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          counts: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          totals: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        },
      });
      setLoading(false);
      return;
    }

    fetch("http://localhost:8000/dashboard_risk/risk_summary")
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
              counts: data.counts || [], // Cantidades de estudiantes en riesgo
              totals: data.totals || [], // Totales de estudiantes por mes
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
  };

  useEffect(() => {
    // Mostrar notificación si se viene desde la carga de CSV
    if (location.state?.message) {
      setShowSuccessAlert(true);
      // Ocultar la notificación después de 5 segundos
      setTimeout(() => {
        setShowSuccessAlert(false);
      }, 5000);
    }

    // Cargar datos iniciales solo una vez
    loadAttendanceData();
    loadRiskData();

    // Función para escuchar cambios de datos (cuando se sube un nuevo CSV)
    const handleStorageChange = (e) => {
      if (e.key === "csv_uploaded") {
        console.log("🔄 Nuevo CSV detectado, actualizando gráficos...");
        loadAttendanceData();
        loadRiskData();
        // Limpiar el flag después de actualizar
        localStorage.removeItem("csv_uploaded");
      }
    };

    // Función para escuchar evento directo de CSV cargado
    const handleCsvUploaded = (e) => {
      console.log("🔄 Evento directo: CSV cargado, actualizando gráficos inmediatamente...");
      setTimeout(() => {
        loadAttendanceData();
        loadRiskData();
      }, 1000); // Pequeña delay para asegurar que el backend haya procesado los datos
    };

    // Escuchar cambios en localStorage para detectar cuando se sube un CSV
    window.addEventListener("storage", handleStorageChange);

    // Escuchar evento personalizado para actualización inmediata
    window.addEventListener("csvUploaded", handleCsvUploaded);

    // Limpieza al desmontar el componente
    return () => {
      window.removeEventListener("storage", handleStorageChange);
      window.removeEventListener("csvUploaded", handleCsvUploaded);
    };
  }, []);

  if (error) return <div style={{ color: "red", fontWeight: "bold" }}>{error}</div>;
  if (loading) return <div>Cargando datos del CSV...</div>;

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox py={3}>
        {/* Botón para ver resultados detallados */}
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

        <Grid container spacing={3}></Grid>
        <MDBox mt={4.5}>
          <Grid container spacing={3}>
            <Grid item xs={18} md={10} lg={8}>
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
            <Grid item xs={12} md={6} lg={4}>
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
            <Grid item xs={12} md={6} lg={4}>
              <MDBox mb={3}></MDBox>
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
