/**
=========================================================
* Material Dashboard 2 React - v2.2.0
=========================================================
*/

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

// @mui material components
import Card from "@mui/material/Card";
import Icon from "@mui/material/Icon";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDAvatar from "components/MDAvatar";

// Images por defecto
import logoXD from "assets/images/juancito.jpg";
import logoSlack from "assets/images/rochita.jpg";
import team1 from "assets/images/team-1.jpg";
import team2 from "assets/images/team-2.jpg";
import team3 from "assets/images/team-3.jpg";
import team4 from "assets/images/juancito.jpg";
import logoJira from "assets/images/marquito.jpg";

const defaultImages = [logoXD, logoSlack, team1, team2, team3, team4, logoJira];

function MediumRiskStudents() {
  const navigate = useNavigate();
  const [studentsAtRisk, setStudentsAtRisk] = useState([]);
  const [loading, setLoading] = useState(true);

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

  // Función para obtener estudiantes en riesgo del backend
  const fetchStudentsAtRisk = async () => {
    try {
      setLoading(true);

      // Solo cargar datos si hay un CSV válido
      if (!hasValidCsvData()) {
        console.log("📭 No hay CSV cargado, no se mostrarán estudiantes en riesgo medio");
        setStudentsAtRisk([]);
        setLoading(false);
        return;
      }

      const response = await fetch("http://localhost:8000/dashboard_risk/students_at_risk");

      if (!response.ok) {
        throw new Error("No se pudieron cargar los estudiantes en riesgo");
      }

      const data = await response.json();
      // Filtrar solo estudiantes con riesgo "Medio"
      const mediumRiskStudents = data.filter((student) => student.risk_level === "Medio");
      setStudentsAtRisk(mediumRiskStudents);
    } catch (err) {
      console.error("Error fetching medium risk students:", err);
      setStudentsAtRisk([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStudentsAtRisk();

    // Función para escuchar cuando se sube un nuevo CSV
    const handleCsvUploaded = () => {
      console.log("🔄 CSV cargado, actualizando estudiantes riesgo medio...");
      setTimeout(() => {
        fetchStudentsAtRisk();
      }, 1000);
    };

    // Función para escuchar cambios en localStorage
    const handleStorageChange = (e) => {
      if (e.key === "csv_uploaded") {
        console.log("🔄 Nuevo CSV detectado, actualizando estudiantes riesgo medio...");
        fetchStudentsAtRisk();
        localStorage.removeItem("csv_uploaded");
      }
    };

    // Escuchar eventos de CSV cargado
    window.addEventListener("csvUploaded", handleCsvUploaded);
    window.addEventListener("storage", handleStorageChange);

    return () => {
      window.removeEventListener("csvUploaded", handleCsvUploaded);
      window.removeEventListener("storage", handleStorageChange);
    };
  }, []);

  // Función para manejar el clic en un estudiante
  const handleStudentClick = (student) => {
    // Buscar los datos completos del estudiante desde localStorage
    let completeStudentData = student;

    try {
      const storedPredictions = localStorage.getItem("latest_predictions");
      if (storedPredictions) {
        const parsedData = JSON.parse(storedPredictions);
        // Buscar el estudiante específico en los datos completos
        const fullStudentData = parsedData.find(
          (p) =>
            (p.id_estudiante && p.id_estudiante.toString() === student.student_id.toString()) ||
            (p.student_id && p.student_id.toString() === student.student_id.toString()) ||
            (p.nombre && p.nombre === student.name)
        );

        if (fullStudentData) {
          console.log("✅ Datos completos encontrados:", fullStudentData);
          completeStudentData = {
            student_id:
              fullStudentData.id_estudiante || fullStudentData.student_id || student.student_id,
            name: fullStudentData.nombre || fullStudentData.name || student.name,
            nota: fullStudentData.nota || fullStudentData.nota_final || 0,
            asistencia: fullStudentData.asistencia || 0,
            risk_level:
              fullStudentData.riesgo_desercion || fullStudentData.risk_level || student.risk_level,
            conducta: fullStudentData.conducta || "Regular",
            ...fullStudentData,
          };
        } else {
          console.warn("⚠️ No se encontraron datos completos para:", student.name);
        }
      }
    } catch (e) {
      console.error("Error buscando datos completos:", e);
    }

    // Formatear los datos del estudiante para el análisis individual
    const formattedStudent = {
      student_id: completeStudentData.student_id || student.student_id,
      name: completeStudentData.name || student.name,
      nota: completeStudentData.nota || 0,
      asistencia: completeStudentData.asistencia || 0,
      risk_level: completeStudentData.risk_level || student.risk_level,
      conducta: completeStudentData.conducta || "Regular",
      ...completeStudentData,
    };

    console.log("📊 Datos formateados para enviar:", formattedStudent);

    // Guardar el estudiante seleccionado en localStorage
    localStorage.setItem("selected_student_for_analysis", JSON.stringify(formattedStudent));

    // Navegar al análisis individual
    navigate("/individual", {
      state: {
        preselectedStudent: formattedStudent,
        fromDashboard: true,
      },
    });
  };

  const renderStudents = () => {
    if (loading) {
      return (
        <MDBox p={2}>
          <MDTypography variant="button" color="text" fontWeight="light">
            Cargando estudiantes...
          </MDTypography>
        </MDBox>
      );
    }

    if (studentsAtRisk.length === 0) {
      return (
        <MDBox p={2}>
          <MDTypography variant="button" color="text" fontWeight="light">
            No hay estudiantes con riesgo medio
          </MDTypography>
        </MDBox>
      );
    }

    return studentsAtRisk.map((student, index) => {
      const defaultImage = defaultImages[index % defaultImages.length];

      return (
        <MDBox
          key={student.student_id}
          display="flex"
          alignItems="center"
          px={1}
          py={0.5}
          sx={{
            cursor: "pointer",
            borderRadius: 1,
            transition: "all 0.2s ease",
            "&:hover": {
              backgroundColor: "#f5f5f5",
            },
          }}
          onClick={() => handleStudentClick(student)}
          title="Haz clic para ver el análisis individual"
        >
          <MDBox mr={2}>
            <MDAvatar src={defaultImage} alt={student.name} size="sm" />
          </MDBox>
          <MDBox flex="1">
            <MDTypography
              variant="button"
              fontWeight="medium"
              lineHeight={1}
              sx={{
                transition: "all 0.2s ease",
                "&:hover": {
                  fontWeight: "bold",
                  color: "#1976d2",
                },
              }}
            >
              {student.name}
            </MDTypography>
            <MDTypography variant="caption" color="warning" fontWeight="bold" display="block">
              Riesgo Medio
            </MDTypography>
          </MDBox>
        </MDBox>
      );
    });
  };

  return (
    <Card sx={{ height: "100%" }}>
      <MDBox display="flex" justifyContent="space-between" alignItems="center" pt={1} px={2}>
        <MDTypography variant="h6" fontWeight="medium" textTransform="capitalize">
          Estudiantes Riesgo Medio
        </MDTypography>
        <MDBox display="flex" alignItems="flex-start">
          <MDBox color="warning" mr={1}>
            <Icon color="inherit" fontSize="small">
              warning
            </Icon>
          </MDBox>
        </MDBox>
      </MDBox>
      <MDBox pt={1} pb={2} px={2}>
        <MDBox mb={2}>
          <MDTypography variant="button" color="text" fontWeight="light">
            Estudiantes que requieren atención preventiva
          </MDTypography>
        </MDBox>
        <MDBox>{renderStudents()}</MDBox>
      </MDBox>
    </Card>
  );
}

export default MediumRiskStudents;
