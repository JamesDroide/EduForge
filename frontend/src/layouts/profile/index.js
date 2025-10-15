/**
=========================================================
* Material Dashboard 2 React - Profile Page
=========================================================
*/

import { useState } from "react";
import { useNavigate } from "react-router-dom";

// @mui material components
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDInput from "components/MDInput";
import MDButton from "components/MDButton";
import MDAlert from "components/MDAlert";

// Material Dashboard 2 React example components
import DashboardLayout from "examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "examples/Navbars/DashboardNavbar";
import Footer from "examples/Footer";

// Auth Context
import { useAuth } from "context/AuthContext";
import { API_ENDPOINTS } from "config/api";

// Material Dashboard 2 React context
import { useMaterialUIController } from "context";

function Profile() {
  const navigate = useNavigate();
  const { user, logout, getToken } = useAuth();
  const [controller] = useMaterialUIController();
  const { darkMode } = controller;

  // Estados para cambio de contraseña
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);

    // Validaciones
    if (!oldPassword || !newPassword || !confirmPassword) {
      setError("Por favor, completa todos los campos");
      setLoading(false);
      return;
    }

    if (newPassword !== confirmPassword) {
      setError("Las contraseñas nuevas no coinciden");
      setLoading(false);
      return;
    }

    if (newPassword.length < 6) {
      setError("La contraseña debe tener al menos 6 caracteres");
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(API_ENDPOINTS.CHANGE_PASSWORD, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${getToken()}`,
        },
        body: JSON.stringify({
          old_password: oldPassword,
          new_password: newPassword,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Error al cambiar la contraseña");
      }

      setSuccess("Contraseña cambiada exitosamente");
      setOldPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate("/authentication/sign-in");
  };

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox mb={2} />
      <MDBox mt={4} mb={3}>
        <Grid container spacing={3}>
          {/* Información del Usuario */}
          <Grid item xs={12} md={6}>
            <Card
              sx={{
                backgroundColor: darkMode ? "transparent" : "white",
                backgroundImage: darkMode ? "none" : undefined,
              }}
            >
              <MDBox
                variant="gradient"
                bgColor="info"
                borderRadius="lg"
                coloredShadow="info"
                mx={2}
                mt={-3}
                p={3}
                mb={1}
                textAlign="center"
              >
                <MDTypography variant="h4" fontWeight="medium" color="white" mt={1}>
                  Mi Perfil
                </MDTypography>
              </MDBox>
              <MDBox pt={4} pb={3} px={3}>
                <MDBox component="form" role="form">
                  <MDBox mb={2}>
                    <MDTypography
                      variant="caption"
                      color={darkMode ? "white" : "text"}
                      fontWeight="bold"
                    >
                      Nombre de Usuario
                    </MDTypography>
                    <MDInput
                      type="text"
                      value={user?.username || ""}
                      fullWidth
                      disabled
                      sx={{
                        "& .MuiInputBase-root": {
                          backgroundColor: darkMode ? "#1a2035 !important" : "white !important",
                        },
                        "& .MuiInputBase-input": {
                          color: darkMode ? "#ffffff !important" : "rgba(0, 0, 0, 0.87) !important",
                          WebkitTextFillColor: darkMode
                            ? "#ffffff !important"
                            : "rgba(0, 0, 0, 0.87) !important",
                        },
                        "& .MuiInputBase-input.Mui-disabled": {
                          WebkitTextFillColor: darkMode
                            ? "#ffffff !important"
                            : "rgba(0, 0, 0, 0.6) !important",
                          color: darkMode ? "#ffffff !important" : "rgba(0, 0, 0, 0.6) !important",
                          opacity: "1 !important",
                        },
                        "& .MuiOutlinedInput-notchedOutline": {
                          borderColor: darkMode
                            ? "rgba(255, 255, 255, 0.3) !important"
                            : "rgba(0, 0, 0, 0.23) !important",
                        },
                      }}
                    />
                  </MDBox>
                  <MDBox mb={2}>
                    <MDTypography
                      variant="caption"
                      color={darkMode ? "white" : "text"}
                      fontWeight="bold"
                    >
                      Correo Electrónico
                    </MDTypography>
                    <MDInput
                      type="email"
                      value={user?.email || ""}
                      fullWidth
                      disabled
                      sx={{
                        "& .MuiInputBase-root": {
                          backgroundColor: darkMode ? "#1a2035 !important" : "white !important",
                        },
                        "& .MuiInputBase-input": {
                          color: darkMode ? "#ffffff !important" : "rgba(0, 0, 0, 0.87) !important",
                          WebkitTextFillColor: darkMode
                            ? "#ffffff !important"
                            : "rgba(0, 0, 0, 0.87) !important",
                        },
                        "& .MuiInputBase-input.Mui-disabled": {
                          WebkitTextFillColor: darkMode
                            ? "#ffffff !important"
                            : "rgba(0, 0, 0, 0.6) !important",
                          color: darkMode ? "#ffffff !important" : "rgba(0, 0, 0, 0.6) !important",
                          opacity: "1 !important",
                        },
                        "& .MuiOutlinedInput-notchedOutline": {
                          borderColor: darkMode
                            ? "rgba(255, 255, 255, 0.3) !important"
                            : "rgba(0, 0, 0, 0.23) !important",
                        },
                      }}
                    />
                  </MDBox>
                  <MDBox mb={2}>
                    <MDTypography
                      variant="caption"
                      color={darkMode ? "white" : "text"}
                      fontWeight="bold"
                    >
                      Rol
                    </MDTypography>
                    <MDInput
                      type="text"
                      value={user?.rol === "administrador" ? "Administrador" : "Docente"}
                      fullWidth
                      disabled
                      sx={{
                        "& .MuiInputBase-root": {
                          backgroundColor: darkMode ? "#1a2035 !important" : "white !important",
                        },
                        "& .MuiInputBase-input": {
                          color: darkMode ? "#ffffff !important" : "rgba(0, 0, 0, 0.87) !important",
                          WebkitTextFillColor: darkMode
                            ? "#ffffff !important"
                            : "rgba(0, 0, 0, 0.87) !important",
                        },
                        "& .MuiInputBase-input.Mui-disabled": {
                          WebkitTextFillColor: darkMode
                            ? "#ffffff !important"
                            : "rgba(0, 0, 0, 0.6) !important",
                          color: darkMode ? "#ffffff !important" : "rgba(0, 0, 0, 0.6) !important",
                          opacity: "1 !important",
                        },
                        "& .MuiOutlinedInput-notchedOutline": {
                          borderColor: darkMode
                            ? "rgba(255, 255, 255, 0.3) !important"
                            : "rgba(0, 0, 0, 0.23) !important",
                        },
                      }}
                    />
                  </MDBox>
                  <MDBox mb={2}>
                    <MDTypography
                      variant="caption"
                      color={darkMode ? "white" : "text"}
                      fontWeight="bold"
                    >
                      Estado
                    </MDTypography>
                    <MDInput
                      type="text"
                      value={user?.is_active ? "Activo" : "Inactivo"}
                      fullWidth
                      disabled
                      sx={{
                        "& .MuiInputBase-root": {
                          backgroundColor: darkMode ? "#1a2035 !important" : "white !important",
                        },
                        "& .MuiInputBase-input": {
                          color: darkMode ? "#ffffff !important" : "rgba(0, 0, 0, 0.87) !important",
                          WebkitTextFillColor: darkMode
                            ? "#ffffff !important"
                            : "rgba(0, 0, 0, 0.87) !important",
                        },
                        "& .MuiInputBase-input.Mui-disabled": {
                          WebkitTextFillColor: darkMode
                            ? "#ffffff !important"
                            : "rgba(0, 0, 0, 0.6) !important",
                          color: darkMode ? "#ffffff !important" : "rgba(0, 0, 0, 0.6) !important",
                          opacity: "1 !important",
                        },
                        "& .MuiOutlinedInput-notchedOutline": {
                          borderColor: darkMode
                            ? "rgba(255, 255, 255, 0.3) !important"
                            : "rgba(0, 0, 0, 0.23) !important",
                        },
                      }}
                    />
                  </MDBox>
                  <MDBox mt={3}>
                    <MDButton variant="gradient" color="error" fullWidth onClick={handleLogout}>
                      Cerrar Sesión
                    </MDButton>
                  </MDBox>
                </MDBox>
              </MDBox>
            </Card>
          </Grid>

          {/* Cambio de Contraseña */}
          <Grid item xs={12} md={6}>
            <Card
              sx={{
                backgroundColor: darkMode ? "transparent" : "white",
                backgroundImage: darkMode ? "none" : undefined,
              }}
            >
              <MDBox
                variant="gradient"
                bgColor="warning"
                borderRadius="lg"
                coloredShadow="warning"
                mx={2}
                mt={-3}
                p={3}
                mb={1}
                textAlign="center"
              >
                <MDTypography variant="h4" fontWeight="medium" color="white" mt={1}>
                  Cambiar Contraseña
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
                {success && (
                  <MDBox mb={2}>
                    <MDAlert color="success" dismissible onClose={() => setSuccess("")}>
                      {success}
                    </MDAlert>
                  </MDBox>
                )}

                <MDBox component="form" role="form" onSubmit={handleChangePassword}>
                  <MDBox mb={2}>
                    <MDInput
                      type="password"
                      label="Contraseña Actual"
                      fullWidth
                      value={oldPassword}
                      onChange={(e) => setOldPassword(e.target.value)}
                      disabled={loading}
                      sx={{
                        "& .MuiInputBase-root": {
                          backgroundColor: darkMode ? "rgba(255, 255, 255, 0.1)" : "white",
                          color: darkMode ? "white" : "inherit",
                        },
                        "& .MuiInputBase-input": {
                          color: darkMode ? "white !important" : "inherit",
                        },
                        "& .MuiInputLabel-root": {
                          color: darkMode ? "rgba(255, 255, 255, 0.7)" : "inherit",
                        },
                        "& .MuiOutlinedInput-notchedOutline": {
                          borderColor: darkMode
                            ? "rgba(255, 255, 255, 0.3)"
                            : "rgba(0, 0, 0, 0.23)",
                        },
                      }}
                    />
                  </MDBox>
                  <MDBox mb={2}>
                    <MDInput
                      type="password"
                      label="Nueva Contraseña"
                      fullWidth
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      disabled={loading}
                      sx={{
                        "& .MuiInputBase-root": {
                          backgroundColor: darkMode ? "rgba(255, 255, 255, 0.1)" : "white",
                          color: darkMode ? "white" : "inherit",
                        },
                        "& .MuiInputBase-input": {
                          color: darkMode ? "white !important" : "inherit",
                        },
                        "& .MuiInputLabel-root": {
                          color: darkMode ? "rgba(255, 255, 255, 0.7)" : "inherit",
                        },
                        "& .MuiOutlinedInput-notchedOutline": {
                          borderColor: darkMode
                            ? "rgba(255, 255, 255, 0.3)"
                            : "rgba(0, 0, 0, 0.23)",
                        },
                      }}
                    />
                  </MDBox>
                  <MDBox mb={2}>
                    <MDInput
                      type="password"
                      label="Confirmar Nueva Contraseña"
                      fullWidth
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      disabled={loading}
                      sx={{
                        "& .MuiInputBase-root": {
                          backgroundColor: darkMode ? "rgba(255, 255, 255, 0.1)" : "white",
                          color: darkMode ? "white" : "inherit",
                        },
                        "& .MuiInputBase-input": {
                          color: darkMode ? "white !important" : "inherit",
                        },
                        "& .MuiInputLabel-root": {
                          color: darkMode ? "rgba(255, 255, 255, 0.7)" : "inherit",
                        },
                        "& .MuiOutlinedInput-notchedOutline": {
                          borderColor: darkMode
                            ? "rgba(255, 255, 255, 0.3)"
                            : "rgba(0, 0, 0, 0.23)",
                        },
                      }}
                    />
                  </MDBox>
                  <MDBox mt={4}>
                    <MDButton
                      variant="gradient"
                      color="warning"
                      fullWidth
                      type="submit"
                      disabled={loading}
                    >
                      {loading ? "Cambiando..." : "Cambiar Contraseña"}
                    </MDButton>
                  </MDBox>
                </MDBox>
              </MDBox>
            </Card>
          </Grid>
        </Grid>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default Profile;
