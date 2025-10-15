/**
=========================================================
* EduForge - Admin Panel Login
=========================================================
*/

import { useState } from "react";
import { useNavigate } from "react-router-dom";

// @mui material components
import Card from "@mui/material/Card";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDInput from "components/MDInput";
import MDButton from "components/MDButton";
import MDAlert from "components/MDAlert";

// Images
import bgImage from "assets/images/bg-sign-in-basic.jpeg";

function AdminLogin() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [accessCode, setAccessCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    // Validaciones
    if (!username || !password || !accessCode) {
      setError("Por favor, completa todos los campos");
      setLoading(false);
      return;
    }

    try {
      const response = await fetch("http://localhost:8000/admin/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username,
          password,
          access_code: accessCode,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Credenciales inválidas");
      }

      const data = await response.json();
      // Guardar token de administrador
      localStorage.setItem("admin_token", data.access_token);
      localStorage.setItem("admin_user", JSON.stringify(data.user));

      // Redirigir al panel de administración
      navigate("/admin-panel/usuarios");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <MDBox
      width="100vw"
      height="100vh"
      display="flex"
      justifyContent="center"
      alignItems="center"
      sx={{
        backgroundImage: `url(${bgImage})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
      }}
    >
      <Card sx={{ maxWidth: 500, width: "90%" }}>
        <MDBox
          variant="gradient"
          bgColor="error"
          borderRadius="lg"
          coloredShadow="error"
          mx={2}
          mt={-3}
          p={3}
          mb={1}
          textAlign="center"
        >
          <MDTypography variant="h4" fontWeight="medium" color="white" mt={1}>
            Panel de Administración
          </MDTypography>
          <MDTypography display="block" variant="button" color="white" my={1}>
            Acceso Restringido - Solo Personal Autorizado
          </MDTypography>
        </MDBox>

        <MDBox pt={4} pb={3} px={3}>
          {error && (
            <MDBox mb={2}>
              <MDAlert color="error" dismissible onClose={() => setError("")}>
                {error}
              </MDAlert>
            </MDBox>
          )}

          <MDBox component="form" role="form" onSubmit={handleSubmit}>
            <MDBox mb={2}>
              <MDInput
                type="text"
                label="Usuario Administrador"
                fullWidth
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                disabled={loading}
                autoComplete="username"
              />
            </MDBox>
            <MDBox mb={2}>
              <MDInput
                type="password"
                label="Contraseña"
                fullWidth
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
                autoComplete="current-password"
              />
            </MDBox>
            <MDBox mb={2}>
              <MDInput
                type="password"
                label="Código de Acceso"
                fullWidth
                value={accessCode}
                onChange={(e) => setAccessCode(e.target.value)}
                disabled={loading}
                placeholder="Código de acceso especial"
              />
            </MDBox>
            <MDBox mt={4} mb={1}>
              <MDButton variant="gradient" color="error" fullWidth type="submit" disabled={loading}>
                {loading ? "Verificando..." : "Acceder al Panel"}
              </MDButton>
            </MDBox>
            <MDBox mt={3} mb={1} textAlign="center">
              <MDTypography variant="caption" color="text">
                Este panel es solo para administradores del sistema
              </MDTypography>
            </MDBox>
          </MDBox>
        </MDBox>
      </Card>
    </MDBox>
  );
}

export default AdminLogin;
