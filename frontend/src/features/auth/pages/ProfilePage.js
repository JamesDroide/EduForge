/**
=========================================================
* Material Dashboard 2 React - Profile Page
=========================================================
*/

import { useState, useEffect } from "react";
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
import api from "config/api";

// Material Dashboard 2 React context
import { useMaterialUIController } from "context";

function Profile() {
  const navigate = useNavigate();
  const { user, logout, getToken, updateUser } = useAuth();
  const [controller] = useMaterialUIController();
  const { darkMode } = controller;

  // Verificar si el usuario puede cambiar su contraseña
  // Los docentes y administradores NO pueden cambiar su contraseña desde aquí
  const canChangePassword = user?.rol !== "docente" && user?.rol !== "administrador";

  // Estados para información personal
  const [nombre, setNombre] = useState("");
  const [apellido, setApellido] = useState("");
  const [loadingProfile, setLoadingProfile] = useState(false);
  const [profileSuccess, setProfileSuccess] = useState("");
  const [profileError, setProfileError] = useState("");

  // Estados para cambio de contraseña
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");

  // Cargar datos del usuario al montar
  useEffect(() => {
    if (user) {
      setNombre(user.nombre || "");
      setApellido(user.apellido || "");
    }
  }, [user]);

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setProfileError("");
    setProfileSuccess("");
    setLoadingProfile(true);

    try {
      const response = await api.put("/auth-v2/update-profile", {
        nombre,
        apellido,
      });

      if (response.data) {
        setProfileSuccess("Perfil actualizado exitosamente");
        // Actualizar el contexto de usuario
        if (updateUser) {
          updateUser({ ...user, nombre, apellido });
        }
      }
    } catch (err) {
      setProfileError(err.response?.data?.detail || "Error al actualizar el perfil");
    } finally {
      setLoadingProfile(false);
    }
  };

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
          <Grid item xs={12} md={canChangePassword ? 6 : 12}>
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
                {profileSuccess && (
                  <MDAlert color="success" dismissible onClose={() => setProfileSuccess("")}>
                    {profileSuccess}
                  </MDAlert>
                )}
                {profileError && (
                  <MDAlert color="error" dismissible onClose={() => setProfileError("")}>
                    {profileError}
                  </MDAlert>
                )}
                <MDBox component="form" role="form" onSubmit={handleUpdateProfile}>
                  {/* Campos editables de nombre y apellido */}
                  <MDBox mb={2}>
                    <MDTypography
                      variant="caption"
                      color={darkMode ? "white" : "text"}
                      fontWeight="bold"
                    >
                      Nombre
                    </MDTypography>
                    <MDInput
                      type="text"
                      value={nombre}
                      onChange={(e) => setNombre(e.target.value)}
                      placeholder="Ingresa tu nombre"
                      fullWidth
                    />
                  </MDBox>
                  <MDBox mb={2}>
                    <MDTypography
                      variant="caption"
                      color={darkMode ? "white" : "text"}
                      fontWeight="bold"
                    >
                      Apellido
                    </MDTypography>
                    <MDInput
                      type="text"
                      value={apellido}
                      onChange={(e) => setApellido(e.target.value)}
                      placeholder="Ingresa tu apellido"
                      fullWidth
                    />
                  </MDBox>
                  <MDBox mb={3}>
                    <MDButton
                      variant="gradient"
                      color="success"
                      fullWidth
                      type="submit"
                      disabled={loadingProfile}
                    >
                      {loadingProfile ? "Actualizando..." : "Actualizar Perfil"}
                    </MDButton>
                  </MDBox>

                  {/* Campos de solo lectura */}
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
                        "& .MuiInputBase-input.Mui-disabled": {
                          WebkitTextFillColor: darkMode
                            ? "#ffffff !important"
                            : "rgba(0, 0, 0, 0.6) !important",
                          color: darkMode ? "#ffffff !important" : "rgba(0, 0, 0, 0.6) !important",
                          opacity: "1 !important",
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
                        "& .MuiInputBase-input.Mui-disabled": {
                          WebkitTextFillColor: darkMode
                            ? "#ffffff !important"
                            : "rgba(0, 0, 0, 0.6) !important",
                          color: darkMode ? "#ffffff !important" : "rgba(0, 0, 0, 0.6) !important",
                          opacity: "1 !important",
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
                        "& .MuiInputBase-input.Mui-disabled": {
                          WebkitTextFillColor: darkMode
                            ? "#ffffff !important"
                            : "rgba(0, 0, 0, 0.6) !important",
                          color: darkMode ? "#ffffff !important" : "rgba(0, 0, 0, 0.6) !important",
                          opacity: "1 !important",
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
                        "& .MuiInputBase-input.Mui-disabled": {
                          WebkitTextFillColor: darkMode
                            ? "#ffffff !important"
                            : "rgba(0, 0, 0, 0.6) !important",
                          color: darkMode ? "#ffffff !important" : "rgba(0, 0, 0, 0.6) !important",
                          opacity: "1 !important",
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

          {/* Cambio de Contraseña - Solo para usuarios que no sean docentes ni administradores */}
          {canChangePassword && (
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
          )}
        </Grid>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}

export default Profile;
