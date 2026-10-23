/* eslint-disable react/prop-types */
/* eslint-disable react/function-component-definition */
/* eslint-disable react-hooks/rules-of-hooks */

import { useState, useEffect } from "react";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDAvatar from "components/MDAvatar";
import { API_BASE_URL } from "config/api";
import defaultStudentImage from "assets/images/juancito.jpg";

export default function data() {
  const [studentsAtRisk, setStudentsAtRisk] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStudentsAtRisk = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/dashboard_risk/students_at_risk`);

      if (!response.ok) {
        throw new Error("No se pudieron cargar los estudiantes en riesgo");
      }

      const result = await response.json();
      setStudentsAtRisk(result);
      setError(null);
    } catch (err) {
      console.error("Error fetching students at risk:", err);
      setError(err.message);
      setStudentsAtRisk([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStudentsAtRisk();

    const interval = setInterval(fetchStudentsAtRisk, 30000);

    const handleCsvUploaded = (event) => {
      console.log("CSV procesado, actualizando lista de estudiantes en riesgo...", event.detail);
      setTimeout(() => {
        fetchStudentsAtRisk();
      }, 2000);
    };

    const handleStorageChange = (e) => {
      if (e.key === "csv_uploaded") {
        console.log("Nuevo CSV detectado en localStorage, actualizando lista...");
        setTimeout(() => {
          fetchStudentsAtRisk();
        }, 2000);
        localStorage.removeItem("csv_uploaded");
      }
    };

    window.addEventListener("csvUploaded", handleCsvUploaded);
    window.addEventListener("storage", handleStorageChange);

    return () => {
      clearInterval(interval);
      window.removeEventListener("csvUploaded", handleCsvUploaded);
      window.removeEventListener("storage", handleStorageChange);
    };
  }, []);

  const Company = ({ image, name }) => (
    <MDBox display="flex" alignItems="center" lineHeight={1}>
      <MDAvatar src={image} name={name} size="sm" />
      <MDTypography variant="button" fontWeight="medium" ml={1} lineHeight={1}>
        {name}
      </MDTypography>
    </MDBox>
  );

  const generateRows = () => {
    if (loading || error) {
      return [];
    }

    const highRiskStudents = studentsAtRisk.filter((student) => student.risk_level === "Alto");

    if (highRiskStudents.length === 0) {
      return [];
    }

    return highRiskStudents.map((student) => {
      return {
        companies: <Company image={defaultStudentImage} name={student.name} />,
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
    refresh: fetchStudentsAtRisk,
  };
}
