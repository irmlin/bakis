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

// @mui material components
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";

// Material Dashboard 2 React components
import MDBox from "Components/MDBox";
import MDTypography from "Components/MDTypography";

// Material Dashboard 2 React example components
import DashboardLayout from "Examples/LayoutContainers/DashboardLayout";
import DashboardNavbar from "Examples/Navbars/DashboardNavbar";
import Footer from "Examples/Footer";
import DataTable from "Examples/Tables/DataTable";

import {useEffect, useState} from "react";
import {getAccidents} from "../../Services/AccidentService";
import {CircularProgress} from "@mui/material";
import ImageLoader from "./components/ImageLoader";
import DownloadableVideo from "./components/DownloadableVideo";

function Accidents() {

  const columns = [
      { Header: "detected", accessor: "detected", width: "45%", align: "left" },
      { Header: "type", accessor: "type", align: "left" },
      { Header: "type", accessor: "video", align: "left" },
      { Header: "image", accessor: "image", align: "center" },
    ];

  const accidentTypeMap = {"CAR_CRASH": "Car Crash"}

  const [accidents, setAccidents] = useState([]);
  const [rows, setRows] = useState([]);

    function createRows() {
      if (!accidents) {
        return [];
      }

      return accidents.map((accident, index) => (
        {
          detected: (
            <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
              {accident["created_at"]}
            </MDTypography>
          ),
          type: (
            <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
              {accidentTypeMap[accident["type"]] || accident["type"]}
            </MDTypography>
          ),
          video: (
            <DownloadableVideo accidentId={accident.id}/>
          ),
          image: (
            <ImageLoader accidentId={accident.id}/>
          )
        }
      ));
    }

    useEffect(() => {
      const fetchAccidents = async () => {
          const response = await getAccidents();
          if (response) {
              if (response.status === 200) {
                console.log(accidents);
                setAccidents(response.data);
              } else {
                  console.error('Error on fetching all accidents: ', response);
              }
          } else {
              console.error('No response from the server while fetching all accidents!');
          }
      };
        fetchAccidents().then(r => {});
    }, [])


    useEffect(() => {
      setRows(createRows());
    }, [accidents]);


  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox pt={6} pb={3}>
        <Grid container spacing={6}>
          <Grid item xs={12}>
            <Card>
              <MDBox
                mx={2}
                mt={-3}
                py={3}
                px={2}
                variant="gradient"
                bgColor="info"
                borderRadius="lg"
                coloredShadow="info"
              >
                <MDTypography variant="h6" color="white">
                  Accidents
                </MDTypography>
              </MDBox>
              <MDBox pt={3}>
                <DataTable
                  table={{ columns, rows }}
                  isSorted={false}
                  entriesPerPage={false}
                  showTotalEntries={false}
                  noEndBorder
                />
              </MDBox>
            </Card>
          </Grid>
        </Grid>
      </MDBox>
    </DashboardLayout>
  );
}

export default Accidents;
