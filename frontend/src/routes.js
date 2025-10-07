import Dashboard from "layouts/dashboard";
import Billing from "layouts/billing";
import IndividualAnalysis from "layouts/individual";
import Notifications from "layouts/notifications";

// @mui icons
import Icon from "@mui/material/Icon";

const routes = [
  {
    type: "collapse",
    name: "Reporte general",
    key: "dashboard",
    icon: <Icon fontSize="small">dashboard</Icon>,
    route: "/dashboard",
    component: <Dashboard />,
  },
  {
    type: "collapse",
    name: "Análisis individual",
    key: "individual",
    icon: <Icon fontSize="small">person_search</Icon>,
    route: "/individual",
    component: <IndividualAnalysis />,
  },
  {
    type: "collapse",
    name: "Resultados completos",
    key: "billing",
    icon: <Icon fontSize="small">receipt_long</Icon>,
    route: "/resultados-completos",
    component: <Billing />,
  },
  {
    type: "collapse",
    name: "Carga de datos",
    key: "notifications",
    icon: <Icon fontSize="small">notifications</Icon>,
    route: "/subir-archivos",
    component: <Notifications />,
  },
];

export default routes;
