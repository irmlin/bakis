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
import {exportAccidentsExcel, exportAccidentsPdf, getFilteredAccidents} from "../../Services/AccidentService";
import {FormControl, InputLabel, OutlinedInput, Select} from "@mui/material";
import ImageLoader from "./components/ImageLoader";
import DownloadableVideo from "./components/DownloadableVideo";

import {LocalizationProvider} from '@mui/x-date-pickers';
import {AdapterDayjs} from '@mui/x-date-pickers/AdapterDayjs'
import {DateTimePicker} from '@mui/x-date-pickers/DateTimePicker';
import MDButton from "../../Components/MDButton";
import {getAllSources} from "../../Services/MediaService";
import MenuItem from "@mui/material/MenuItem";
import Checkbox from "@mui/material/Checkbox";
import ListItemText from "@mui/material/ListItemText";
import TextField from "@mui/material/TextField";


function Accidents() {

  const columns = [
      { Header: "detected", accessor: "detected", width: "20%", align: "left" },
      { Header: "camera/video", accessor: "camera", align: "left" },
      { Header: "type", accessor: "type", align: "left" },
      { Header: "video", accessor: "video", align: "left" },
      { Header: "image", accessor: "image", align: "center" },
    ];

  const accidentTypeMap = {"CAR_CRASH": "Car Crash"}

  const [accidents, setAccidents] = useState([]);
  const [rows, setRows] = useState([]);
  const [dateFrom, setDateFrom] = useState(null);
  const [dateTo, setDateTo] = useState(null);
  const [selectedSources, setSelectedSources] = useState([]);
  const [allSources, setAllSources] = useState([]);
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

  const onDateFromChange = (newDate) => {
    setDateFrom(newDate);
  };

  const onDateToChange = (newDate) => {
    setDateTo(newDate);
  };

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
        camera: (
          <MDTypography component="a" href="#" variant="caption" color="text" fontWeight="medium">
            {accident["video"]["title"]}
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

  useEffect(() => {
    const fetchAccidents = async () => {
        const response = await getFilteredAccidents(skip, limit);
        if (response) {
            if (response.status === 200) {
              const updatedResponse = response.data.map((accident) => ({...accident,
                created_at: shiftUtcDateToLocal(accident.created_at)}))
              setAccidents(updatedResponse);
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
    const fetchAllSources = async () => {
        const response = await getAllSources();
        if (response) {
            if (response.status === 200) {
              setAllSources(response.data);
            } else {
                console.error('Error on fetching all sources: ', response);
            }
        } else {
            console.error('No response from the server while fetching all sources!');
        }
    };
      fetchAllSources().then(r => {});
  }, [])


  useEffect(() => {
    setRows(createRows());
  }, [accidents]);

  const onFilterButtonClick = async () => {
      const response = await getFilteredAccidents(getQueryParams(true));
      if (response) {
          if (response.status === 200) {
              const updatedResponse = response.data.map((accident) => ({...accident,
                created_at: shiftUtcDateToLocal(accident.created_at)}))
              setAccidents(updatedResponse);
          } else {
              console.error('Error on fetching filtered accidents: ', response);
          }
      } else {
          console.error('No response from the server while fetching filtered accidents!');
      }
  };

  const onExportPdfButtonClick = async () => {
      const response = await exportAccidentsPdf(getQueryParams(false));
      if (response) {
          if (response.status === 200) {
            const disposition = response.headers['content-disposition'];
            let filename = disposition.split(/;(.+)/)[1].split(/=(.+)/)[1];
            if (filename.toLowerCase().startsWith("utf-8''"))
               filename = decodeURIComponent(filename.replace("utf-8''", ''));
            else
               filename = filename.replace(/['"]/g, '');
            const url = window.URL.createObjectURL(response.data);
            const a = document.createElement("a");
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
          } else {
              console.error('Error on downloading PDF: ', response);
          }
      } else {
          console.error('No response from the server while downloading PDF!');
      }
  };


  const onExportExcelButtonClick = async () => {
      const response = await exportAccidentsExcel(getQueryParams(false));
      if (response) {
          if (response.status === 200) {
            const disposition = response.headers['content-disposition'];
            let filename = disposition.split(/;(.+)/)[1].split(/=(.+)/)[1];
            if (filename.toLowerCase().startsWith("utf-8''"))
               filename = decodeURIComponent(filename.replace("utf-8''", ''));
            else
               filename = filename.replace(/['"]/g, '');
            const url = window.URL.createObjectURL(response.data);
            const a = document.createElement("a");
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
          } else {
              console.error('Error on downloading excel: ', response);
          }
      } else {
          console.error('No response from the server while downloading excel!');
      }
  };


  function getQueryParams(pagination) {
    const queryParams = new URLSearchParams();
    if (pagination)
      if (skip)
        queryParams.append("skip", skip);
    if (pagination)
      if (limit)
        queryParams.append("limit", limit);
    if (dateTo)
      queryParams.append("datetime_to", dateTo.toISOString());
    if (dateFrom)
      queryParams.append("datetime_from", dateFrom.toISOString());
    const sourceIdsArray = (selectedSources && selectedSources.length) ?
      (selectedSources.map((source) => source.id)) : null;
    if (sourceIdsArray) {
      for (const id of sourceIdsArray) {
        queryParams.append('source_ids', id);
      }
    }

    return queryParams;
  }


  const onSelectSourcesChange = (event) => {
    const selected = event.target.value;
    console.log(selected)
    setSelectedSources([...selected])
  };

  return (
    <DashboardLayout>
      <DashboardNavbar />
      <MDBox pt={6} pb={3}>
        <MDBox mb={5} sx={{ display: 'flex'}}>
          <LocalizationProvider dateAdapter={AdapterDayjs}>
            <DateTimePicker
              ampm={false}
              timeSteps={{minutes: 1}}
              value={dateFrom}
              label={"Filter by Date - from"}
              onChange={onDateFromChange}
              timezone={"system"}
              format="YYYY-MM-DD HH:mm"
              renderInput={(props) => <TextField {...props} />}
            />
            <DateTimePicker
              ampm={false}
              timeSteps={{minutes: 1}}
              value={dateTo}
              label={"Filter by Date - to"}
              onChange={onDateToChange}
              timezone={"system"}
              format="YYYY-MM-DD HH:mm"
              renderInput={(props) => <TextField {...props} />}
            />
          </LocalizationProvider>
          <FormControl sx={{ width: 300 }}>
            <InputLabel id="sources-multiple-select">Filter by Video Source</InputLabel>
            <Select
              labelId="sources-multiple-select"
              id="sources-multiple-select"
              multiple
              value={selectedSources}
              onChange={onSelectSourcesChange}
              input={<OutlinedInput label="Filter by Video Source" />}
              renderValue={(selected) => selected.map((source) => source.title).join(', ')}
              MenuProps={MenuProps}
            >
              {allSources.map((source) => (
                <MenuItem key={source.id} value={source}>
                  <Checkbox checked={selectedSources.map((source) => source.id).indexOf(source.id) > -1} />
                  <ListItemText primary={source.title} />
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <MDButton
            onClick={onFilterButtonClick}
            variant="contained"
            color="info"
          >
            Apply Filter
          </MDButton>
          <MDButton
            onClick={onExportPdfButtonClick}
            variant="contained"
            color="info"
          >
            Export to PDF
          </MDButton>
          <MDButton
            onClick={onExportExcelButtonClick}
            variant="contained"
            color="info"
          >
            Export to Excel
          </MDButton>
        </MDBox>
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
