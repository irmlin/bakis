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

import {useState} from "react";

// Material Dashboard 2 React example components
import DashboardLayout from "Examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "Examples/Navbars/DashboardNavbar";
 import Card from "@mui/material/Card";
 import MDBox from "../../Components/MDBox";
 import SettingsControlPanel from "./components/SettingsControlPanel";

export default function Settings() {

  return (
    <DashboardLayout>
      <DashboardNavbar />
        <Card sx={{height: "100%"}}>
          {/*<MDBox mb={5} mt={5} display="flex" justifyContent="center">*/}
          <MDBox mb={5} mt={5}>
            <SettingsControlPanel/>
          </MDBox>
        </Card>
    </DashboardLayout>
  );
}