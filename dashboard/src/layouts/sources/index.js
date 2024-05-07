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
import DataTable from "Examples/Tables/DataTable";

import {useEffect, useState} from "react";
import {getFilteredSources} from "../../Services/MediaService";


function Sources() {

  const columns = [
      { Header: "title", accessor: "title", width: "20%", align: "left" },
      { Header: "description", accessor: "description", align: "left" },
      { Header: "added", accessor: "added", align: "left" },
      { Header: "status", accessor: "status", align: "left" },
      { Header: "type", accessor: "type", align: "left" },
      { Header: "accidents detected", accessor: "numAccidents", align: "left" },
    ];

  const sourceTypeMap = {"VIDEO": "Video", "STREAM": "Stream"}

  const [sources, setSources] = useState([]);
  const [rows, setRows] = useState([]);
  const [skip, setSkip] = useState(0);
  const [limit, setLimit] = useState(10);


  const ITEM_HEIGHT = 48;
  const ITEM_PADDING_TOP = 8;
  const MenuProps = {
    PaperProps: {
      style: {
        maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
        width: 250,
      },
    },
  };

  function createRows() {
    if (!sources) {
      return [];
    }

    return sources.map((source, index) => (
      {
        title: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            {source["title"]}
          </MDTypography>
        ),
        description: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            {source["description"]}
          </MDTypography>
        ),
        added: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            {source["created_at"]}
          </MDTypography>
        ),
        status: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            {source["status"]}
          </MDTypography>
        ),
        type: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            {source["source_type"]}
          </MDTypography>
        ),
        numAccidents: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            {source["num_accidents"]}
          </MDTypography>
        ),
      }
    ));
  }

  function shiftUtcDateToLocal(utcDateString) {
    let offsetMinutes = new Date().getTimezoneOffset();
    let offsetMilliseconds = offsetMinutes * 60 * 1000; // Convert offset to milliseconds
    let localDate = new Date(new Date(utcDateString).getTime() - offsetMilliseconds);
    return localDate.toLocaleString("en-ZA", {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    });
  }

  function getQueryParams(pagination) {
    const queryParams = new URLSearchParams();
    if (pagination)
      if (skip)
        queryParams.append("skip", skip);
    if (pagination)
      if (limit)
        queryParams.append("limit", limit);
    return queryParams;
  }


  useEffect(() => {
    const fetchSources = async () => {
        const response = await getFilteredSources(getQueryParams(false));
        console.log(response);
        if (response) {
            if (response.status === 200) {
              const updatedResponse = response.data.map((source) => ({...source,
                created_at: shiftUtcDateToLocal(source.created_at)}))
              setSources(updatedResponse);
            } else {
                console.error('Error on fetching all accidents: ', response);
            }
        } else {
            console.error('No response from the server while fetching all accidents!');
        }
    };
      fetchSources().then(r => {});
  }, [])

  useEffect(() => {
    setRows(createRows());
  }, [sources]);



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
                  Video Sources
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

export default Sources;
