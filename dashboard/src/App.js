/**
=========================================================
* Material Dashboard 2 React - v2.2.0
=========================================================

* Product Page: https://www.creative-tim.com/product/material-dashboard-react
* Copyright 2023 Creative Tim (https://www.creative-tim.com)

Coded by www.creative-tim.com

 =========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
*/

import {useEffect, useMemo, useState} from "react";

// react-router components
import {Navigate, Route, Routes, useLocation} from "react-router-dom";

// @mui material components
import CssBaseline from "@mui/material/CssBaseline";
import Icon from "@mui/material/Icon";
import AccountCircleIcon from '@mui/icons-material/AccountCircleOutlined';
import LogoutIcon from '@mui/icons-material/Logout';

// Material Dashboard 2 React components
import MDBox from "Components/MDBox";

// Material Dashboard 2 React example components
import Sidenav from "Examples/Sidenav";

// Material Dashboard 2 React themes
import theme from "Assets/theme";
import themeRTL from "Assets/theme/theme-rtl";

// Material Dashboard 2 React Dark Mode themes
import themeDark from "Assets/theme-dark";
import themeDarkRTL from "Assets/theme-dark/theme-rtl";

// RTL plugins
import rtlPlugin from "stylis-plugin-rtl";
import {CacheProvider} from "@emotion/react";
import createCache from "@emotion/cache";

// Material Dashboard 2 React routes
import routes from "routes";

// Material Dashboard 2 React contexts
import {
  setMiniSidenav,
  setNotificationOpen,
  setOpenConfigurator,
  useMaterialUIController
} from "Context/MaterialUIContextProvider";

// Images
import brandWhite from "Assets/images/logo-ct.png";
import brandDark from "Assets/images/logo-ct-dark.png";
import {ThemeProvider} from "@mui/system";
import MDSnackbar from "./Components/MDSnackbar";
import {useAuthorizationContext} from "./Context/AuthorizationContextProvider";
import IconButton from "@mui/material/IconButton";
import Menu from "@mui/material/Menu";
import NotificationItem from "./Examples/Items/NotificationItem";
import {navbarIconButton} from "./Examples/Navbars/DashboardNavbar/styles";

export default function App() {
  const [controller, dispatch] = useMaterialUIController();
  const [username, allowed] = useAuthorizationContext();
  const {
    miniSidenav,
    direction,
    layout,
    openConfigurator,
    sidenavColor,
    transparentSidenav,
    whiteSidenav,
    darkMode,
    notificationOpen,
    notificationColor,
    notificationTitle,
    notificationContent
  } = controller;
  const [onMouseEnter, setOnMouseEnter] = useState(false);
  const [rtlCache, setRtlCache] = useState(null);
  const { pathname } = useLocation();

  // Cache for the rtl
  useMemo(() => {
    const cacheRtl = createCache({
      key: "rtl",
      stylisPlugins: [rtlPlugin],
    });

    setRtlCache(cacheRtl);
  }, []);

  // Open sidenav when mouse enter on mini sidenav
  const handleOnMouseEnter = () => {
    if (miniSidenav && !onMouseEnter) {
      setMiniSidenav(dispatch, false);
      setOnMouseEnter(true);
    }
  };

  const onNotificationClose = () => {
    setNotificationOpen(dispatch, false)
  }

  // Close sidenav when mouse leave mini sidenav
  const handleOnMouseLeave = () => {
    if (onMouseEnter) {
      setMiniSidenav(dispatch, true);
      setOnMouseEnter(false);
    }
  };

  // Change the openConfigurator state
  const handleConfiguratorOpen = () => setOpenConfigurator(dispatch, !openConfigurator);

  // Setting the dir attribute for the body element
  useEffect(() => {
    document.body.setAttribute("dir", direction);
  }, [direction]);

  // Setting page scroll to 0 when changing the route
  useEffect(() => {
    document.documentElement.scrollTop = 0;
    document.scrollingElement.scrollTop = 0;
  }, [pathname]);

  const getRoutes = (allRoutes) =>
    allRoutes.map((route) => {
      if (route.collapse) {
        return getRoutes(route.collapse);
      }

      if (route.route) {
        return <Route exact path={route.route} element={route.component} key={route.key} />;
      }

      return null;
    });

  const onLogoutButtonClick = () => {
    localStorage.setItem('token', '');
    localStorage.setItem('admin', false);
    localStorage.setItem('username', 'guest');
    window.location = "/authentication/sign-in";
  }

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

  const [openMenu, setOpenMenu] = useState(false);
  const handleOpenMenu = (event) => setOpenMenu(event.currentTarget);
  const handleCloseMenu = () => setOpenMenu(false);

  const iconsStyle = ({ palette: { dark, white, text }, functions: { rgba } }) => ({
    color: () => {
      return white.main;
    },
  });

  const renderMenu = () => (
    <Menu
      anchorEl={openMenu}
      anchorReference={null}
      anchorOrigin={{
        vertical: "bottom",
        horizontal: "left",
      }}
      open={Boolean(openMenu)}
      onClose={handleCloseMenu}
      sx={{ mt: 2, p: 0}}
    >
      <IconButton onClick={onLogoutButtonClick} sx={{ p: 0, m: 0, height: 20}}>
        <NotificationItem icon={<LogoutIcon></LogoutIcon>} title={"Logout (" + username + ")"} />
      </IconButton>
    </Menu>
  );

  return direction === "rtl" ? (
    <CacheProvider value={rtlCache}>
      <ThemeProvider theme={darkMode ? themeDarkRTL : themeRTL}>
        <CssBaseline />
        {layout === "dashboard" && (
          <>
            <Sidenav
              color={sidenavColor}
              brand={(transparentSidenav && !darkMode) || whiteSidenav ? brandDark : brandWhite}
              brandName="Material Dashboard 2"
              routes={routes}
              onMouseEnter={handleOnMouseEnter}
              onMouseLeave={handleOnMouseLeave}
            />
            {/*<Configurator />*/}
            {/*{configsButton}*/}
          </>
        )}
        {/*{layout === "vr" && <Configurator />}*/}
        <Routes>
          {getRoutes(routes)}
          <Route path="*" element={<Navigate to="/dashboard" />} />
        </Routes>
      </ThemeProvider>
    </CacheProvider>
  ) : (
    <ThemeProvider theme={darkMode ? themeDark : theme}>
      <CssBaseline />
      {layout === "dashboard" && (
        <>
          <Sidenav
            color={sidenavColor}
            // brand={(transparentSidenav && !darkMode) || whiteSidenav ? brandDark : camLogo}
            brandName={"Vehicle collision detection system"}
            routes={routes}
            onMouseEnter={handleOnMouseEnter}
            onMouseLeave={handleOnMouseLeave}
          />
          {/*<Configurator />*/}
          {/*{configsButton}*/}
        </>
      )}
      {/*{layout === "vr" && <Configurator />}*/}
      <Routes>
        {getRoutes(routes)}
        <Route path="*" element={<Navigate to="/authentication/sign-in" />} />
      </Routes>
      <MDSnackbar
        color={notificationColor}
        title={"System Message"}
        content={notificationContent}
        open={notificationOpen}
        onClose={onNotificationClose}
        close={onNotificationClose}
        // bgWhite
        dateTime={""}
      />
      {
        window.location.pathname !== "/authentication/sign-in" &&
        <MDBox
          py={1}
          px={2}
          mt={3}
          mr={3}
          borderRadius="lg"
          position="fixed"
          top={0}
          right={0}
          zIndex={3}
          color={"white"}
        >
          <IconButton
            size="small"
            disableRipple
            color="inherit"
            sx={navbarIconButton}
            aria-controls="notification-menu"
            aria-haspopup="true"
            variant="contained"
            onClick={handleOpenMenu}
          >
            <AccountCircleIcon color={"secondary"} fontSize={"large"} sx={{mr: 1}}/>
          </IconButton>
          {renderMenu()}
        </MDBox>
      }
    </ThemeProvider>
  );
}
