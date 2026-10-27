import { createContext, useContext, useState, useEffect } from "react";
import PropTypes from "prop-types";
import { API_ENDPOINTS } from "config/api";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedToken = localStorage.getItem("token");
    const storedUser = localStorage.getItem("user");

    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    try {
      const response = await fetch(API_ENDPOINTS.LOGIN, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
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
            `Error de comunicación con el servidor (HTTP ${response.status} en ${API_ENDPOINTS.LOGIN})`
        );
      }

      if (!payload || !payload.access_token) {
        throw new Error("Respuesta inválida del servidor de autenticación");
      }

      localStorage.setItem("token", payload.access_token);
      localStorage.setItem("user", JSON.stringify(payload.user));

      setToken(payload.access_token);
      setUser(payload.user);

      return { success: true, user: payload.user };
    } catch (error) {
      console.error("Error en login:", error);
      return { success: false, error: error.message };
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setToken(null);
    setUser(null);
  };

  const isAuthenticated = () => {
    return !!token && !!user;
  };

  const isAdmin = () => {
    return user?.rol === "administrador";
  };

  const getToken = () => {
    return token;
  };

  const updateUser = (updatedUserData) => {
    setUser((prevUser) => {
      const newUser = { ...(prevUser || {}), ...updatedUserData };
      localStorage.setItem("user", JSON.stringify(newUser));
      return newUser;
    });
  };

  const value = {
    user,
    token,
    loading,
    login,
    logout,
    isAuthenticated,
    isAdmin,
    getToken,
    updateUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

AuthProvider.propTypes = {
  children: PropTypes.node.isRequired,
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth debe ser usado dentro de un AuthProvider");
  }
  return context;
};

export default AuthContext;
