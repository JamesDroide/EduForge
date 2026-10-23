import { useState, useEffect, useMemo } from "react";
import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import { ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import Icon from "@mui/material/Icon";
import MDBox from "components/MDBox";
import Sidenav from "examples/Sidenav";
import Configurator from "examples/Configurator";
import theme from "assets/theme";
import themeRTL from "assets/theme/theme-rtl";
import themeDark from "assets/theme-dark";
import themeDarkRTL from "assets/theme-dark/theme-rtl";
import rtlPlugin from "stylis-plugin-rtl";
import { CacheProvider } from "@emotion/react";
import createCache from "@emotion/cache";
import routes from "routes";
import { useMaterialUIController, setMiniSidenav, setOpenConfigurator } from "context";
import brandWhite from "assets/images/logo-ct.png";
import brandDark from "assets/images/logo-ct-dark.png";
import Billing from "layouts/billing";
import UploadData from "layouts/notifications";
import AdminLogin from "layouts/admin-panel/login";
import UserManagement from "layouts/user-management";
import { AuthProvider } from "context/AuthContext";
import PrivateRoute from "components/PrivateRoute";

export default function App() {
  const [controller, dispatch] = useMaterialUIController();
  const {
    miniSidenav,
    direction,
    layout,
    openConfigurator,
    sidenavColor,
    transparentSidenav,
    whiteSidenav,
    darkMode,
  } = controller;
  const [onMouseEnter, setOnMouseEnter] = useState(false);
  const [rtlCache, setRtlCache] = useState(null);
  const { pathname } = useLocation();

  const memoizedRtlCache = useMemo(() => {
    return createCache({
      key: "rtl",
      stylisPlugins: [rtlPlugin],
    });
  }, []);

  useEffect(() => {
    setRtlCache(memoizedRtlCache);
  }, [memoizedRtlCache]);

  const handleOnMouseEnter = () => {
    if (miniSidenav && !onMouseEnter) {
      setMiniSidenav(dispatch, false);
      setOnMouseEnter(true);
    }
  };

  const handleOnMouseLeave = () => {
    if (onMouseEnter) {
      setMiniSidenav(dispatch, true);
      setOnMouseEnter(false);
    }
  };

  const handleConfiguratorOpen = () => setOpenConfigurator(dispatch, !openConfigurator);

  useEffect(() => {
    document.body.setAttribute("dir", direction);
  }, [direction]);

  useEffect(() => {
    document.documentElement.scrollTop = 0;
    document.scrollingElement.scrollTop = 0;
  }, [pathname]);

  const getRoutes = useMemo(() => {
    const processRoutes = (allRoutes) =>
      allRoutes.map((route) => {
        if (route.collapse) {
          return processRoutes(route.collapse);
        }

        if (route.route) {
          return <Route exact path={route.route} element={route.component} key={route.key} />;
        }

        return null;
      });

    return processRoutes(routes);
  }, []);

  const configsButton = (
    <MDBox
      display="flex"
      justifyContent="center"
      alignItems="center"
      width="3.25rem"
      height="3.25rem"
      bgColor="white"
      shadow="sm"
      borderRadius="50%"
      position="fixed"
      right="2rem"
      bottom="2rem"
      zIndex={99}
      color="dark"
      sx={{ cursor: "pointer" }}
      onClick={handleConfiguratorOpen}
    >
      <Icon fontSize="small" color="inherit">
        settings
      </Icon>
    </MDBox>
  );

  return direction === "rtl" ? (
    <CacheProvider value={rtlCache}>
      <ThemeProvider theme={darkMode ? themeDarkRTL : themeRTL}>
        <CssBaseline />
        <AuthProvider>
          {/* El panel de administracion opera con sesion y layout aislados del Sidenav general */}
          {layout === "dashboard" && !pathname.startsWith("/admin-panel") && (
            <>
              <Sidenav
                color={sidenavColor}
                brand={(transparentSidenav && !darkMode) || whiteSidenav ? brandDark : brandWhite}
                brandName="EduForge"
                routes={routes}
                onMouseEnter={handleOnMouseEnter}
                onMouseLeave={handleOnMouseLeave}
              />
              <Configurator />
              {configsButton}
            </>
          )}
          {layout === "vr" && <Configurator />}
          <Routes>
            {getRoutes}
            <Route
              path="/upload-data"
              element={
                <PrivateRoute>
                  <UploadData />
                </PrivateRoute>
              }
            />
            <Route
              path="/billing"
              element={
                <PrivateRoute>
                  <Billing />
                </PrivateRoute>
              }
            />
            <Route path="/admin-panel/login" element={<AdminLogin />} />
            <Route path="/admin-panel/usuarios" element={<UserManagement />} />
            <Route path="/" element={<Navigate to="/authentication/sign-in" />} />
            <Route path="*" element={<Navigate to="/authentication/sign-in" />} />
          </Routes>
        </AuthProvider>
      </ThemeProvider>
    </CacheProvider>
  ) : (
    <ThemeProvider theme={darkMode ? themeDark : theme}>
      <CssBaseline />
      <AuthProvider>
        {layout === "dashboard" && !pathname.startsWith("/admin-panel") && (
          <>
            <Sidenav
              color={sidenavColor}
              brand={(transparentSidenav && !darkMode) || whiteSidenav ? brandDark : brandWhite}
              brandName="EduForge"
              routes={routes}
              onMouseEnter={handleOnMouseEnter}
              onMouseLeave={handleOnMouseLeave}
            />
            <Configurator />
            {configsButton}
          </>
        )}
        {layout === "vr" && <Configurator />}
        <Routes>
          {getRoutes}
          <Route
            path="/upload-data"
            element={
              <PrivateRoute>
                <UploadData />
              </PrivateRoute>
            }
          />
          <Route
            path="/billing"
            element={
              <PrivateRoute>
                <Billing />
              </PrivateRoute>
            }
          />
          <Route path="/admin-panel/login" element={<AdminLogin />} />
          <Route path="/admin-panel/usuarios" element={<UserManagement />} />
          <Route path="/" element={<Navigate to="/authentication/sign-in" />} />
          <Route path="*" element={<Navigate to="/authentication/sign-in" />} />
        </Routes>
      </AuthProvider>
    </ThemeProvider>
  );
}
