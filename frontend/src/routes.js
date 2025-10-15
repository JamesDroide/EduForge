import Dashboard from "layouts/dashboard";
import Billing from "layouts/billing";
import IndividualAnalysis from "layouts/individual";
import Notifications from "layouts/notifications";
import SignIn from "layouts/authentication/sign-in";
import Profile from "layouts/profile";

// @mui icons
import Icon from "@mui/material/Icon";

// Componente para proteger rutas
import PrivateRoute from "components/PrivateRoute";

const routes = [
  {
    type: "collapse",
    name: "Reporte general",
    key: "dashboard",
    icon: <Icon fontSize="small">dashboard</Icon>,
    route: "/dashboard",
    component: (
      <PrivateRoute>
        <Dashboard />
      </PrivateRoute>
    ),
  },
  {
    type: "collapse",
    name: "Análisis individual",
    key: "individual",
    icon: <Icon fontSize="small">person_search</Icon>,
    route: "/individual",
    component: (
      <PrivateRoute>
        <IndividualAnalysis />
      </PrivateRoute>
    ),
  },
  {
    type: "collapse",
    name: "Resultados completos",
    key: "billing",
    icon: <Icon fontSize="small">receipt_long</Icon>,
    route: "/resultados-completos",
    component: (
      <PrivateRoute>
        <Billing />
      </PrivateRoute>
    ),
  },
  {
    type: "collapse",
    name: "Carga de datos",
    key: "notifications",
    icon: <Icon fontSize="small">notifications</Icon>,
    route: "/subir-archivos",
    component: (
      <PrivateRoute>
        <Notifications />
      </PrivateRoute>
    ),
  },
  {
    type: "divider",
    key: "divider-1",
  },
  {
    type: "collapse",
    name: "Mi Perfil",
    key: "profile",
    icon: <Icon fontSize="small">person</Icon>,
    route: "/perfil",
    component: (
      <PrivateRoute>
        <Profile />
      </PrivateRoute>
    ),
  },
  {
    type: "public",
    name: "Sign In",
    key: "sign-in",
    icon: <Icon fontSize="small">login</Icon>,
    route: "/authentication/sign-in",
    component: <SignIn />,
  },
];

export default routes;
