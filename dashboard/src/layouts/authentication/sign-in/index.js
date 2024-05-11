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

import { useState } from "react";

// react-router-dom components
import { Link } from "react-router-dom";

// @mui material components
import Card from "@mui/material/Card";
import Switch from "@mui/material/Switch";
import Grid from "@mui/material/Grid";
import MuiLink from "@mui/material/Link";

// @mui icons
import FacebookIcon from "@mui/icons-material/Facebook";
import GitHubIcon from "@mui/icons-material/GitHub";
import GoogleIcon from "@mui/icons-material/Google";

// Material Dashboard 2 React components
import MDBox from "Components/MDBox";
import MDTypography from "Components/MDTypography";
import MDInput from "Components/MDInput";
import MDButton from "Components/MDButton";

// Authentication layout components
import BasicLayout from "layouts/authentication/components/BasicLayout";

// Images
import bgImage from "Assets/images/bg-sign-in-basic.jpeg";
import {showNotification, useMaterialUIController} from "../../../Context/MaterialUIContextProvider";
import {login} from "../../../Services/AuthService";

function Basic() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [controller, dispatch] = useMaterialUIController();

  const onUsernameChange = (event) => {
    setUsername(event.target.value);
  }

  const onPasswordChange = (event) => {
    setPassword(event.target.value);
  }

  function validateFields() {
    return username && password;
  }

  const handleLogin = async () => {
    if (!validateFields()) {
      showNotification(dispatch, "error", "Username and Password fields are required!")
      return;
    }
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    const response = await login(formData);
    if (response) {
      if (response.status === 200) {
        // parse response, save token in storage
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('admin', true);
        window.location = "/dashboard";
      } else {
        showNotification(dispatch, "error", response.data.detail);
      }
    } else {
      showNotification(dispatch, "error", "No response from the server while logging in!")
    }
  }


  return (
    <BasicLayout image={bgImage}>
      <Card>
        <MDBox
          variant="gradient"
          bgColor="info"
          borderRadius="lg"
          coloredShadow="info"
          mx={2}
          mt={-3}
          p={2}
          mb={1}
          textAlign="center"
        >
          <MDTypography variant="h4" fontWeight="medium" color="white" mt={1}>
            Admin Login
          </MDTypography>
        </MDBox>
        <MDBox pt={4} pb={3} px={3}>
          <MDBox component="form" role="form">
            <MDBox mb={2}>
              <MDInput type="email" label="Username" fullWidth onChange={onUsernameChange}/>
            </MDBox>
            <MDBox mb={2}>
              <MDInput type="password" label="Password" fullWidth onChange={onPasswordChange}/>
            </MDBox>
            <MDBox mt={4} mb={1}>
              <MDButton variant="gradient" color="info" fullWidth onClick={handleLogin}>
                Login
              </MDButton>
            </MDBox>
            <MDBox mt={3} mb={1} textAlign="center">
              <MDTypography variant="button" color="text">
                Don&apos;t have an account?{" "}
                <MDTypography
                  component={Link}
                  to="/authentication/sign-up"
                  variant="button"
                  color="info"
                  fontWeight="medium"
                  textGradient
                >
                  Sign up
                </MDTypography>
              </MDTypography>
            </MDBox>
          </MDBox>
        </MDBox>
      </Card>
    </BasicLayout>
  );
}

export default Basic;
