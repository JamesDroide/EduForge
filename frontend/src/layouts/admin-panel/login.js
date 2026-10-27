import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Card from "@mui/material/Card";
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDInput from "components/MDInput";
import MDButton from "components/MDButton";
import MDAlert from "components/MDAlert";
import { API_BASE_URL } from "config/api";
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

    if (!username || !password || !accessCode) {
      setError("Por favor, completa todos los campos");
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/admin/login`, {
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

      const rawText = await response.text();
      let payload = null;
      if (rawText) {
        try {
          payload = JSON.parse(rawText);
        } catch (parseErr) {
          payload = null;
        }
      }

      if (!response.ok) {
        throw new Error(
          payload?.detail ||
            payload?.message ||
            `Error de comunicación con el servidor (HTTP ${response.status})`
        );
      }

      if (!payload || !payload.access_token) {
        throw new Error("Respuesta inválida del servidor");
      }

      localStorage.setItem("admin_token", payload.access_token);
      localStorage.setItem("admin_user", JSON.stringify(payload.user));

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
