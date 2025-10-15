/**
=========================================================
* EduForge - User Management Page
=========================================================
*/

import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";

// @mui material components
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import Icon from "@mui/material/Icon";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import IconButton from "@mui/material/IconButton";
import Switch from "@mui/material/Switch";
import MenuItem from "@mui/material/MenuItem";

// Material Dashboard 2 React components
import MDBox from "components/MDBox";
import MDTypography from "components/MDTypography";
import MDInput from "components/MDInput";
import MDButton from "components/MDButton";
import MDAlert from "components/MDAlert";

// API configuration
import { API_BASE_URL } from "config/api";

// Material Dashboard 2 React context
import { useMaterialUIController } from "context";

function UserManagement() {
  const navigate = useNavigate();
  const [controller] = useMaterialUIController();
  const { darkMode } = controller;

  // Verificar si el usuario tiene acceso al panel de administración
  useEffect(() => {
    const adminToken = localStorage.getItem("admin_token");
    if (!adminToken) {
      navigate("/admin-panel/login");
    }
  }, [navigate]);

  // Función para obtener el token de administrador
  const getAdminToken = () => {
    return localStorage.getItem("admin_token");
  };

  // Función para cerrar sesión del panel de administración
  const handleLogout = () => {
    localStorage.removeItem("admin_token");
    localStorage.removeItem("admin_user");
    navigate("/admin-panel/login");
  };

  // Estados para la lista de usuarios
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // Estados para el diálogo de crear/editar usuario
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogMode, setDialogMode] = useState("create"); // "create" o "edit"
  const [selectedUser, setSelectedUser] = useState(null);
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    rol: "docente",
    is_active: true,
  });

  // Estados para el diálogo de cambiar contraseña
  const [openPasswordDialog, setOpenPasswordDialog] = useState(false);
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  // Función para obtener la lista de usuarios
  const fetchUsers = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/admin/users`, {
        headers: {
          Authorization: `Bearer ${getAdminToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error("Error al cargar los usuarios");
      }

      const data = await response.json();
      setUsers(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  // Cargar usuarios al montar el componente
  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  // Función para abrir el diálogo de crear usuario
  const handleCreateUser = () => {
    setDialogMode("create");
    setFormData({
      username: "",
      email: "",
      password: "",
      rol: "docente",
      is_active: true,
    });
    setOpenDialog(true);
  };

  // Función para abrir el diálogo de editar usuario
  const handleEditUser = (user) => {
    setDialogMode("edit");
    setSelectedUser(user);
    setFormData({
      username: user.username,
      email: user.email,
      password: "",
      rol: user.rol,
      is_active: user.is_active,
    });
    setOpenDialog(true);
  };

  // Función para guardar usuario (crear o editar)
  const handleSaveUser = async () => {
    setError("");
    setSuccess("");

    // Validaciones
    if (!formData.username || !formData.email) {
      setError("Por favor, completa todos los campos requeridos");
      return;
    }

    if (dialogMode === "create" && !formData.password) {
      setError("La contraseña es requerida para crear un usuario");
      return;
    }

    if (dialogMode === "create" && formData.password.length < 6) {
      setError("La contraseña debe tener al menos 6 caracteres");
      return;
    }

    setLoading(true);

    try {
      const url =
        dialogMode === "create"
          ? `${API_BASE_URL}/admin/users`
          : `${API_BASE_URL}/admin/users/${selectedUser.id}`;

      const method = dialogMode === "create" ? "POST" : "PUT";

      const body =
        dialogMode === "create"
          ? formData
          : {
              username: formData.username,
              email: formData.email,
              rol: formData.rol,
              is_active: formData.is_active,
            };

      const response = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${getAdminToken()}`,
        },
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Error al guardar el usuario");
      }

      setSuccess(
        dialogMode === "create" ? "Usuario creado exitosamente" : "Usuario actualizado exitosamente"
      );
      setOpenDialog(false);
      fetchUsers();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Función para abrir el diálogo de cambiar contraseña
  const handleOpenPasswordDialog = (user) => {
    setSelectedUser(user);
    setNewPassword("");
    setConfirmPassword("");
    setOpenPasswordDialog(true);
  };

  // Función para cambiar la contraseña de un usuario
  const handleChangePassword = async () => {
    setError("");
    setSuccess("");

    if (!newPassword || !confirmPassword) {
      setError("Por favor, completa todos los campos");
      return;
    }

    if (newPassword !== confirmPassword) {
      setError("Las contraseñas no coinciden");
      return;
    }

    if (newPassword.length < 6) {
      setError("La contraseña debe tener al menos 6 caracteres");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        `${API_BASE_URL}/admin/users/${selectedUser.id}/change-password`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${getAdminToken()}`,
          },
          body: JSON.stringify({ new_password: newPassword }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Error al cambiar la contraseña");
      }

      setSuccess("Contraseña cambiada exitosamente");
      setOpenPasswordDialog(false);
      setNewPassword("");
      setConfirmPassword("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Función para activar/desactivar usuario
  const handleToggleActive = async (user) => {
    setError("");
    setSuccess("");
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/admin/users/${user.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${getAdminToken()}`,
        },
        body: JSON.stringify({
          username: user.username,
          email: user.email,
          rol: user.rol,
          is_active: !user.is_active,
        }),
      });

      if (!response.ok) {
        throw new Error("Error al cambiar el estado del usuario");
      }

      setSuccess(`Usuario ${!user.is_active ? "activado" : "desactivado"} exitosamente`);
      fetchUsers();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Función para eliminar usuario
  const handleDeleteUser = async (user) => {
    if (!window.confirm(`¿Estás seguro de eliminar al usuario ${user.username}?`)) {
      return;
    }

    setError("");
    setSuccess("");
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/admin/users/${user.id}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${getAdminToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error("Error al eliminar el usuario");
      }

      setSuccess("Usuario eliminado exitosamente");
      fetchUsers();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <MDBox
      width="100vw"
      minHeight="100vh"
      sx={{
        backgroundColor: darkMode ? "#1a2035" : "#f0f2f5",
        pt: 3,
        pb: 3,
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        overflowY: "auto",
      }}
    >
      {/* Header del Panel de Administración */}
      <MDBox display="flex" justifyContent="space-between" alignItems="center" px={3} mb={3}>
        <MDBox>
          <MDTypography variant="h3" color={darkMode ? "white" : "dark"} mb={1}>
            Panel de Administración - EduForge
          </MDTypography>
          <MDTypography variant="body2" color="text">
            Sistema de gestión de usuarios - Acceso restringido
          </MDTypography>
        </MDBox>
        <MDButton
          variant="gradient"
          color="error"
          onClick={handleLogout}
          startIcon={<Icon>logout</Icon>}
        >
          Cerrar Sesión
        </MDButton>
      </MDBox>

      <MDBox px={3}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
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
                display="flex"
                justifyContent="space-between"
                alignItems="center"
              >
                <MDTypography variant="h4" fontWeight="medium" color="white">
                  Gestión de Usuarios
                </MDTypography>
                <MDButton
                  variant="contained"
                  color="white"
                  onClick={handleCreateUser}
                  startIcon={<Icon>add</Icon>}
                >
                  Crear Usuario
                </MDButton>
              </MDBox>

              <MDBox p={3}>
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

                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>
                          <MDTypography
                            variant="caption"
                            fontWeight="bold"
                            color={darkMode ? "white" : "dark"}
                          >
                            Usuario
                          </MDTypography>
                        </TableCell>
                        <TableCell>
                          <MDTypography
                            variant="caption"
                            fontWeight="bold"
                            color={darkMode ? "white" : "dark"}
                          >
                            Correo
                          </MDTypography>
                        </TableCell>
                        <TableCell>
                          <MDTypography
                            variant="caption"
                            fontWeight="bold"
                            color={darkMode ? "white" : "dark"}
                          >
                            Rol
                          </MDTypography>
                        </TableCell>
                        <TableCell>
                          <MDTypography
                            variant="caption"
                            fontWeight="bold"
                            color={darkMode ? "white" : "dark"}
                          >
                            Estado
                          </MDTypography>
                        </TableCell>
                        <TableCell align="center">
                          <MDTypography
                            variant="caption"
                            fontWeight="bold"
                            color={darkMode ? "white" : "dark"}
                          >
                            Acciones
                          </MDTypography>
                        </TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {loading && users.length === 0 ? (
                        <TableRow>
                          <TableCell colSpan={5} align="center">
                            <MDTypography variant="body2" color={darkMode ? "white" : "text"}>
                              Cargando usuarios...
                            </MDTypography>
                          </TableCell>
                        </TableRow>
                      ) : users.length === 0 ? (
                        <TableRow>
                          <TableCell colSpan={5} align="center">
                            <MDTypography variant="body2" color={darkMode ? "white" : "text"}>
                              No hay usuarios registrados
                            </MDTypography>
                          </TableCell>
                        </TableRow>
                      ) : (
                        users.map((user) => (
                          <TableRow key={user.id}>
                            <TableCell>
                              <MDTypography variant="body2" color={darkMode ? "white" : "text"}>
                                {user.username}
                              </MDTypography>
                            </TableCell>
                            <TableCell>
                              <MDTypography variant="body2" color={darkMode ? "white" : "text"}>
                                {user.email}
                              </MDTypography>
                            </TableCell>
                            <TableCell>
                              <MDTypography
                                variant="caption"
                                color={user.rol === "administrador" ? "error" : "info"}
                                fontWeight="medium"
                              >
                                {user.rol === "administrador" ? "Administrador" : "Docente"}
                              </MDTypography>
                            </TableCell>
                            <TableCell>
                              <Switch
                                checked={user.is_active}
                                onChange={() => handleToggleActive(user)}
                                color="success"
                              />
                            </TableCell>
                            <TableCell align="center">
                              <IconButton
                                size="small"
                                color="info"
                                onClick={() => handleEditUser(user)}
                                title="Editar usuario"
                              >
                                <Icon>edit</Icon>
                              </IconButton>
                              <IconButton
                                size="small"
                                color="warning"
                                onClick={() => handleOpenPasswordDialog(user)}
                                title="Cambiar contraseña"
                              >
                                <Icon>lock</Icon>
                              </IconButton>
                              <IconButton
                                size="small"
                                color="error"
                                onClick={() => handleDeleteUser(user)}
                                title="Eliminar usuario"
                              >
                                <Icon>delete</Icon>
                              </IconButton>
                            </TableCell>
                          </TableRow>
                        ))
                      )}
                    </TableBody>
                  </Table>
                </TableContainer>
              </MDBox>
            </Card>
          </Grid>
        </Grid>
      </MDBox>

      {/* Diálogo para crear/editar usuario */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <MDTypography variant="h5">
            {dialogMode === "create" ? "Crear Nuevo Usuario" : "Editar Usuario"}
          </MDTypography>
        </DialogTitle>
        <DialogContent>
          <MDBox pt={2}>
            <MDBox mb={2}>
              <MDInput
                type="text"
                label="Nombre de Usuario"
                fullWidth
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                disabled={loading}
              />
            </MDBox>
            <MDBox mb={2}>
              <MDInput
                type="email"
                label="Correo Electrónico"
                fullWidth
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                disabled={loading}
              />
            </MDBox>
            {dialogMode === "create" && (
              <MDBox mb={2}>
                <MDInput
                  type="password"
                  label="Contraseña"
                  fullWidth
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  disabled={loading}
                />
              </MDBox>
            )}
            <MDBox mb={2}>
              <MDInput
                select
                label="Rol"
                fullWidth
                value={formData.rol}
                onChange={(e) => setFormData({ ...formData, rol: e.target.value })}
                disabled={loading}
              >
                <MenuItem value="docente">Docente</MenuItem>
                <MenuItem value="administrador">Administrador</MenuItem>
              </MDInput>
            </MDBox>
            <MDBox display="flex" alignItems="center">
              <Switch
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                color="success"
              />
              <MDTypography variant="button" ml={1}>
                Usuario Activo
              </MDTypography>
            </MDBox>
          </MDBox>
        </DialogContent>
        <DialogActions>
          <MDButton onClick={() => setOpenDialog(false)} color="secondary">
            Cancelar
          </MDButton>
          <MDButton onClick={handleSaveUser} color="info" disabled={loading}>
            {loading ? "Guardando..." : "Guardar"}
          </MDButton>
        </DialogActions>
      </Dialog>

      {/* Diálogo para cambiar contraseña */}
      <Dialog
        open={openPasswordDialog}
        onClose={() => setOpenPasswordDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <MDTypography variant="h5">Cambiar Contraseña de {selectedUser?.username}</MDTypography>
        </DialogTitle>
        <DialogContent>
          <MDBox pt={2}>
            <MDBox mb={2}>
              <MDInput
                type="password"
                label="Nueva Contraseña"
                fullWidth
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                disabled={loading}
              />
            </MDBox>
            <MDBox mb={2}>
              <MDInput
                type="password"
                label="Confirmar Contraseña"
                fullWidth
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                disabled={loading}
              />
            </MDBox>
          </MDBox>
        </DialogContent>
        <DialogActions>
          <MDButton onClick={() => setOpenPasswordDialog(false)} color="secondary">
            Cancelar
          </MDButton>
          <MDButton onClick={handleChangePassword} color="warning" disabled={loading}>
            {loading ? "Cambiando..." : "Cambiar Contraseña"}
          </MDButton>
        </DialogActions>
      </Dialog>
    </MDBox>
  );
}

export default UserManagement;
