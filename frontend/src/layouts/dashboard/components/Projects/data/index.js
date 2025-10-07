/* eslint-disable react/prop-types */
/* eslint-disable react/function-component-definition */
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

import { useState, useEffect } from "react";

// @mui material components
import Tooltip from "@mui/material/Tooltip";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDAvatar from "components/MDAvatar";
import MDProgress from "components/MDProgress";

// Images - mantener las imágenes por defecto para estudiantes sin foto específica
import logoXD from "assets/images/juancito.jpg";
import logoSlack from "assets/images/rochita.jpg";
import logoSpotify from "assets/images/small-logos/logo-spotify.svg";
import logoJira from "assets/images/marquito.jpg";
import team1 from "assets/images/team-1.jpg";
import team2 from "assets/images/team-2.jpg";
import team3 from "assets/images/team-3.jpg";
import team4 from "assets/images/juancito.jpg";

// Array de imágenes por defecto para rotar entre estudiantes
const defaultImages = [logoXD, logoSlack, team1, team2, team3, team4, logoJira];

export default function data() {
  const [studentsAtRisk, setStudentsAtRisk] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Función para obtener estudiantes en riesgo del backend
  const fetchStudentsAtRisk = async () => {
    try {
      setLoading(true);
      const response = await fetch("http://localhost:8000/dashboard_risk/students_at_risk");

      if (!response.ok) {
        throw new Error("No se pudieron cargar los estudiantes en riesgo");
      }

      const data = await response.json();
      setStudentsAtRisk(data);
      setError(null);
    } catch (err) {
      console.error("Error fetching students at risk:", err);
      setError(err.message);
      setStudentsAtRisk([]);
    } finally {
      setLoading(false);
    }
  };

  // Cargar datos al montar el componente
  useEffect(() => {
    fetchStudentsAtRisk();

    // Actualizar cada 30 segundos para detectar nuevos datos
    const interval = setInterval(fetchStudentsAtRisk, 30000);

    // Función para escuchar cuando se sube un nuevo CSV
    const handleCsvUploaded = (event) => {
      console.log("🔄 CSV procesado, actualizando lista de estudiantes en riesgo...", event.detail);
      // Esperar un poco para que se guarden los datos en la base de datos
      setTimeout(() => {
        fetchStudentsAtRisk();
      }, 2000); // Esperar 2 segundos para asegurar que los datos se guardaron
    };

    // Función para escuchar cambios en localStorage
    const handleStorageChange = (e) => {
      if (e.key === "csv_uploaded") {
        console.log("🔄 Nuevo CSV detectado en localStorage, actualizando lista...");
        setTimeout(() => {
          fetchStudentsAtRisk();
        }, 2000);
        localStorage.removeItem("csv_uploaded");
      }
    };

    // Escuchar eventos de CSV cargado
    window.addEventListener("csvUploaded", handleCsvUploaded);
    window.addEventListener("storage", handleStorageChange);

    return () => {
      clearInterval(interval);
      window.removeEventListener("csvUploaded", handleCsvUploaded);
      window.removeEventListener("storage", handleStorageChange);
    };
  }, []);

  const avatars = (members) =>
    members.map(([image, name]) => (
      <Tooltip key={name} title={name} placeholder="bottom">
        <MDAvatar
          src={image}
          alt="name"
          size="xs"
          sx={{
            border: ({ borders: { borderWidth }, palette: { white } }) =>
              `${borderWidth[2]} solid ${white.main}`,
            cursor: "pointer",
            position: "relative",

            "&:not(:first-of-type)": {
              ml: -1.25,
            },

            "&:hover, &:focus": {
              zIndex: "10",
            },
          }}
        />
      </Tooltip>
    ));

  const Company = ({ image, name }) => (
    <MDBox display="flex" alignItems="center" lineHeight={1}>
      <MDAvatar src={image} name={name} size="sm" />
      <MDTypography variant="button" fontWeight="medium" ml={1} lineHeight={1}>
        {name}
      </MDTypography>
    </MDBox>
  );

  // Generar filas basadas en los datos del backend
  const generateRows = () => {
    if (loading) {
      return [];
    }

    if (error) {
      return [];
    }

    // Filtrar solo estudiantes con riesgo "Alto" (el riesgo medio ahora va en componente separado)
    const highRiskStudents = studentsAtRisk.filter((student) => student.risk_level === "Alto");

    if (highRiskStudents.length === 0) {
      return [];
    }

    return highRiskStudents.map((student, index) => {
      // Asignar imagen por defecto rotando entre las disponibles
      const defaultImage = defaultImages[index % defaultImages.length];

      return {
        companies: <Company image={defaultImage} name={student.name} />,
        budget: (
          <MDTypography color="error" fontWeight="bold">
            {student.risk_level}
          </MDTypography>
        ),
      };
    });
  };

  return {
    columns: [
      { Header: "Estudiante", accessor: "companies", width: "45%", align: "left" },
      { Header: "Nivel", accessor: "budget", align: "center" },
    ],
    rows: generateRows(),
    // Función para refrescar manualmente los datos
    refresh: fetchStudentsAtRisk,
  };
}
