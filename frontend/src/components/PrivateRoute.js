import { Navigate } from "react-router-dom";
import PropTypes from "prop-types";
import { useAuth } from "context/AuthContext";

// Componente para proteger rutas que requieren autenticación
function PrivateRoute({ children, requireAdmin = false }) {
  const { isAuthenticated, isAdmin, loading } = useAuth();

  // Mostrar loading mientras se verifica la autenticación
  if (loading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh'
      }}>
        Cargando...
      </div>
    );
  }

  // Si no está autenticado, redirigir al login
  if (!isAuthenticated()) {
    return <Navigate to="/authentication/sign-in" replace />;
  }

  // Si requiere admin y no lo es, redirigir al dashboard
  if (requireAdmin && !isAdmin()) {
    return <Navigate to="/dashboard" replace />;
  }

  // Si todo está bien, mostrar el componente
  return children;
}

PrivateRoute.propTypes = {
  children: PropTypes.node.isRequired,
  requireAdmin: PropTypes.bool,
};

export default PrivateRoute;

