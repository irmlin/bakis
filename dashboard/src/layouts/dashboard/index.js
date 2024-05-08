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
import reportsLineChartData from "layouts/dashboard/data/reportsLineChartData";

import LiveStreamControlPanel from "./components/LiveStreamControlPanel";
import LiveStreamPanel from "./components/LiveStreamPanel";

export default function Dashboard() {
  const [newSourceTrigger, onNewSourceTrigger] = useState(true);

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <LiveStreamControlPanel
        newSourceTrigger={newSourceTrigger}
        onNewSourceTrigger={onNewSourceTrigger}
      />
      <LiveStreamPanel
        newSourceTrigger={newSourceTrigger}
      />
    </DashboardLayout>
  );
}