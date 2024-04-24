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

import {useRef, useState} from "react";

// @mui material components
import Grid from "@mui/material/Grid";

// Material Dashboard 2 React components
import MDBox from "Components/MDBox";
import MDButton from "Components/MDButton";

// Material Dashboard 2 React example components
import DashboardLayout from "Examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "Examples/Navbars/DashboardNavbar";
import Footer from "Examples/Footer";
import ReportsBarChart from "Examples/Charts/BarCharts/ReportsBarChart";
import ReportsLineChart from "Examples/Charts/LineCharts/ReportsLineChart";
import ComplexStatisticsCard from "Examples/Cards/StatisticsCards/ComplexStatisticsCard";

// Data
import reportsBarChartData from "layouts/dashboard/data/reportsBarChartData";
import reportsLineChartData from "layouts/dashboard/data/reportsLineChartData";

// Dashboard components
import Projects from "layouts/dashboard/components/Projects";
import OrdersOverview from "layouts/dashboard/components/OrdersOverview";
import VideoPlayer from "Components/Media/VideoPlayer";
import LiveStreamControlPanel from "./components/LiveStreamControlPanel";
import LiveStreamPanel from "./components/LiveStreamPanel";
import StreamStatusChart from "./components/StreamStatusChart";

export default function Dashboard() {
  const { sales,  tasks } = reportsLineChartData;
  const [newSourceTrigger, onNewSourceTrigger] = useState(true);

  // Video player settings
  // const playerRef = useRef(null);
  // const videoPlayerOptions = {
  //   autoplay: false,
  //   controls: true,
  //   responsive: true,
  //   fluid: true,
  //   sources: [{
  //     src: 'video2.mp4',
  //     type: 'video/mp4'
  //   }]
  // };

  // const handlePlayerReady = (player) => {
  //   playerRef.current = player;
  //
  //   // You can handle player events here, for example:
  //   player.on('waiting', () => {
  //     // console.log('waiting')
  //     // videojs.log('player is waiting');
  //   });
  //
  //   player.on('dispose', () => {
  //     // console.log('disposing')
  //     // videojs.log('player will dispose');
  //   });
  // };

  // For demo purposes
  // const [modelData1, updateModelData1] = useState({
  //   crash: null,
  //   noCrash: null
  // });
  //
  // const [modelData2, updateModelData2] = useState({
  //   crash: null,
  //   noCrash: null
  // });

  return (
    <DashboardLayout>
      <DashboardNavbar />

      {/*<StreamStatusChart*/}
      {/*  color="dark"*/}
      {/*  title="420 completed tasks title"*/}
      {/*  description="69 Last Campaign Performance"*/}
      {/*  input={modelData1}*/}
      {/*  id="1"*/}
      {/*/>*/}
      {/*<StreamStatusChart*/}
      {/*  color="dark"*/}
      {/*  title="420 completed tasks title"*/}
      {/*  description="69 Last Campaign Performance"*/}
      {/*  input={modelData2}*/}
      {/*  id="2"*/}
      {/*/>*/}

      {/*<MDButton*/}
      {/*  onClick={() => {*/}
      {/*    updateModelData1({crash: 1, noCrash: 0.2});*/}
      {/*  }}*/}
      {/*  variant="outlined"*/}
      {/*  color="dark"*/}
      {/*>*/}
      {/*  Stop the cap*/}
      {/*</MDButton>*/}

      <LiveStreamControlPanel
        newSourceTrigger={newSourceTrigger}
        onNewSourceTrigger={onNewSourceTrigger}
      />
      <LiveStreamPanel
        newSourceTrigger={newSourceTrigger}
      />

      <MDBox mt={4.5}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6} lg={4}>
            <MDBox mb={3}>
              {/*<VideoPlayer options={videoPlayerOptions} onReady={handlePlayerReady} />*/}
            </MDBox>
          </Grid>
        </Grid>
      </MDBox>

      <MDBox py={3}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6} lg={3}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                color="dark"
                icon="weekend"
                title="Bookings"
                count={281}
                percentage={{
                  color: "success",
                  amount: "+55%",
                  label: "than lask week",
                }}
              />
            </MDBox>
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                icon="leaderboard"
                title="Today's Users"
                count="2,300"
                percentage={{
                  color: "success",
                  amount: "+3%",
                  label: "than last month",
                }}
              />
            </MDBox>
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                color="success"
                icon="store"
                title="Revenue"
                count="34k"
                percentage={{
                  color: "success",
                  amount: "+1%",
                  label: "than yesterday",
                }}
              />
            </MDBox>
          </Grid>
          <Grid item xs={12} md={6} lg={3}>
            <MDBox mb={1.5}>
              <ComplexStatisticsCard
                color="primary"
                icon="person_add"
                title="Followers"
                count="+91"
                percentage={{
                  color: "success",
                  amount: "",
                  label: "Just updated",
                }}
              />
            </MDBox>
          </Grid>
        </Grid>
        <MDBox mt={4.5}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6} lg={4}>
              <MDBox mb={3}>
                <ReportsBarChart
                  color="info"
                  title="website views"
                  description="Last Campaign Performance"
                  date="campaign sent 2 days ago"
                  chart={reportsBarChartData}
                />
              </MDBox>
            </Grid>
            {/*<Grid item xs={12} md={6} lg={4}>*/}
            {/*  <MDBox mb={3}>*/}
            {/*    <ReportsLineChart*/}
            {/*      color="success"*/}
            {/*      title="daily sales"*/}
            {/*      description={*/}
            {/*        <>*/}
            {/*          (<strong>+15%</strong>) increase in today sales.*/}
            {/*        </>*/}
            {/*      }*/}
            {/*      date="updated 4 min ago"*/}
            {/*      chart={sales}*/}
            {/*    />*/}
            {/*  </MDBox>*/}
            {/*</Grid>*/}
            {/*<Grid item xs={12} md={6} lg={4}>*/}
            {/*  <MDBox mb={3}>*/}
            {/*    <ReportsLineChart*/}
            {/*      color="dark"*/}
            {/*      title="completed tasks"*/}
            {/*      description="Last Campaign Performance"*/}
            {/*      date="just updated"*/}
            {/*      chart={tasks}*/}
            {/*    />*/}
            {/*  </MDBox>*/}
            {/*</Grid>*/}
          </Grid>
        </MDBox>
        <MDBox>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6} lg={8}>
              <Projects />
            </Grid>
            <Grid item xs={12} md={6} lg={4}>
              <OrdersOverview />
            </Grid>
          </Grid>
        </MDBox>
      </MDBox>
      <Footer />
    </DashboardLayout>
  );
}