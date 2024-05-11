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
import {deleteSource, getFilteredSources} from "../../Services/MediaService";
import IconButton from "@mui/material/IconButton";
import DeleteIcon from "@mui/icons-material/Delete";
import {Dialog, DialogActions, DialogTitle} from "@mui/material";
import MDButton from "../../Components/MDButton";
import ClearIcon from "@mui/icons-material/Clear";
import {showNotification, useMaterialUIController} from "../../Context/MaterialUIContextProvider";
import {useAuthorizationContext} from "../../Context/AuthorizationContextProvider";


function Sources() {

  const columns = [
      { Header: "title", accessor: "title", align: "left" },
      { Header: "description", accessor: "description", align: "left" },
      { Header: "added", accessor: "added", align: "left" },
      { Header: "status", accessor: "status", align: "left" },
      { Header: "type", accessor: "type", align: "left" },
      { Header: "accidents detected", accessor: "numAccidents", align: "left" },
      { Header: "", accessor: "deleteSource", align: "left", verticalAlign: "middle" },
    ];

  const sourceTypeMap = {"VIDEO": "Video", "STREAM": "Stream"}

  const [sources, setSources] = useState([]);
  const [rows, setRows] = useState([]);
  const [skip, setSkip] = useState(0);
  const [limit, setLimit] = useState(10);
  const [removeConfirmDialogOpen, setRemoveConfirmDialogOpen] = useState(false);
  const [activeSourceId, setActiveSourceId] = useState(null);
  const [dialogTitle, setDialogTitle] = useState("");

  const [controller, dispatch] = useMaterialUIController();
  const [allowed] = useAuthorizationContext();

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

    return sources.map((source, index) => {
        const deleteSourceElement = allowed ? (
            <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
                <IconButton color="dark" size="large" onClick={() => onDeleteButtonClick(source["id"])}>
                    <ClearIcon/>
                </IconButton>
            </MDTypography>
        ) : null;

        return {
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
            deleteSource: deleteSourceElement,
        };
    })
  }

  const onDeleteButtonClick = (sourceId) => {
    let title = "";
    if (sources) {
      let s = sources.filter(ss => ss.id === sourceId);
      if (s)
        title = s[0].title;
    }
    setDialogTitle(`Delete video source \"${title}\" and all of its data permanently?`);
    setActiveSourceId(sourceId);
    openRemoveConfirmDialog();
  }

  const closeRemoveConfirmDialog = () => {
    setRemoveConfirmDialogOpen(false);
  }

  const openRemoveConfirmDialog = () => {
    setRemoveConfirmDialogOpen(true);
  }

  const onDeleteSource = async () => {
    if (!activeSourceId)
      return;
    const response = await deleteSource(activeSourceId);
    if (response) {
        if (response.status === 200) {
          const updatedSources = sources.filter(s => s.id !== activeSourceId);
          setSources(updatedSources);
          setActiveSourceId(null);
        } else {
            console.error('Error on deleting source: ', response);
            showNotification(dispatch, "error", "An error occurred while deleting source!")
        }
    } else {
        console.error('No response from the server while deleting source!');
        showNotification(dispatch, "error", "No response from the server while deleting source!")
    }
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

  const onConfirmRemoveButtonClick = async () => {
    await onDeleteSource();
    closeRemoveConfirmDialog();
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
                showNotification(dispatch, "error", "An error occurred while fetching video sources data!")
            }
        } else {
            console.error('No response from the server while fetching all accidents!');
            showNotification(dispatch, "error", "No response from the server while fetching video sources data!")
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
      <Dialog
        open={removeConfirmDialogOpen}
        onClose={closeRemoveConfirmDialog}
      >
        <DialogTitle>{dialogTitle}</DialogTitle>
        <DialogActions>
          <MDButton
            onClick={onConfirmRemoveButtonClick}
            variant="contained"
            color="error"
          >
            YES
          </MDButton>
          <MDButton
            onClick={closeRemoveConfirmDialog}
            variant="contained"
            color="info"
          >
            CANCEL
          </MDButton>
        </DialogActions>
      </Dialog>
    </DashboardLayout>
  );
}

export default Sources;
