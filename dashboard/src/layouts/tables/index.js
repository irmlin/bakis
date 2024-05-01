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
import {getAccidents, getFilteredAccidents} from "../../Services/AccidentService";
import {CircularProgress, FormControl, InputLabel, OutlinedInput, Select} from "@mui/material";
import ImageLoader from "./components/ImageLoader";
import DownloadableVideo from "./components/DownloadableVideo";

import {DesktopDatePicker, LocalizationProvider, TimePicker} from '@mui/x-date-pickers';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs'
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import dayjs from "dayjs";
import {DemoContainer, DemoItem} from "@mui/x-date-pickers/internals/demo";
import {Label} from "@mui/icons-material";
import MDButton from "../../Components/MDButton";
import {getAllSources} from "../../Services/MediaService";
import MenuItem from "@mui/material/MenuItem";
import Checkbox from "@mui/material/Checkbox";
import ListItemText from "@mui/material/ListItemText";


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
  const [dateFrom, setDateFrom] = useState(new dayjs());
  const [dateTo, setDateTo] = useState(new dayjs());
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

  useEffect(() => {
    const fetchAccidents = async () => {
        const response = await getFilteredAccidents(skip, limit);
        if (response) {
            if (response.status === 200) {
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
    const fetchAllSources = async () => {
        const response = await getAllSources();
        if (response) {
            if (response.status === 200) {
              console.log(response.data);
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
      const response = await getFilteredAccidents(skip, limit,
        dateFrom ? dateFrom.toISOString() : null,
        dateTo ? dateTo.toISOString() : null,
        (selectedSources && selectedSources.length) ?
          selectedSources.map((source) => source.id) : null
      );
      if (response) {
          if (response.status === 200) {
            setAccidents(response.data);
          } else {
              console.error('Error on fetching filtered accidents: ', response);
          }
      } else {
          console.error('No response from the server while fetching filtered accidents!');
      }
  };

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
              onChange={onDateFromChange}
              timezone={"system"}
            />
            <DateTimePicker
              ampm={false}
              timeSteps={{minutes: 1}}
              value={dateTo}
              onChange={onDateToChange}
              timezone={"system"}
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
            Filter
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
