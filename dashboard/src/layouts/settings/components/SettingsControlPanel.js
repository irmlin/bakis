import * as React from 'react';
import {
  Unstable_NumberInput as BaseNumberInput,
  numberInputClasses,
} from '@mui/base/Unstable_NumberInput';
import {styled, useTheme} from '@mui/system';
import {useEffect, useState} from "react";
import {FormControl, InputLabel, ListSubheader, Select} from "@mui/material";
import MenuItem from "@mui/material/MenuItem";
import Box from "@mui/material/Box";
import MDButton from "../../../Components/MDButton";
import MDBox from "../../../Components/MDBox";
import {
  addRecipient, deleteRecipient,
  getRecipients,
  getSensitivityThreshold,
  updateSensitivityThreshold
} from "../../../Services/SettingsService";
import {getLiveStreams} from "../../../Services/MediaService";
import TextField from "@mui/material/TextField";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import IconButton from "@mui/material/IconButton";
import DeleteIcon from "@mui/icons-material/Delete";
import ListItemText from "@mui/material/ListItemText";
import Divider from "@mui/material/Divider";
import {showNotification, useMaterialUIController} from "../../../Context/MaterialUIContextProvider";


export default function SettingsControlPanel() {

  const [threshold, setThreshold] = useState('');
  const [email, setEmail] = useState('');
  const [emails, setEmails] = useState([]);

  const [controller, dispatch] = useMaterialUIController();

  const theme = useTheme();
  const THR_ITEM_HEIGHT = 48;
  const THR_ITEM_PADDING_TOP = 8;
  const thresholdMenuProps = {
    PaperProps: {
      style: {
        maxHeight: THR_ITEM_HEIGHT * 4.5 + THR_ITEM_PADDING_TOP,
        width: 250,
      },
    },
  };

  const thresholdMenuItems = [];
  for (let i = 0; i <= 1.01; i += 0.01) {
    let i_fixed = i.toFixed(2);
    thresholdMenuItems.push(
      <MenuItem key={i_fixed} style={{fontWeight: theme.typography.fontWeightRegular, height: 30}}
        value={i_fixed}>{i_fixed}
      </MenuItem>
    );
  }

  const onThresholdChange = (event) => {
    setThreshold(event.target.value);
  }

  useEffect(() => {
      const fetchThreshold = async () => {
          const response = await getSensitivityThreshold();
          if (response) {
              if (response.status === 200) {
                  setThreshold(response.data.car_crash_threshold.toFixed(2));
              } else {
                  console.error('Error on fetching threshold: ', response);
                  showNotification(dispatch, "error", "An error occurred while fetching sensitivity threshold!")
              }
          } else {
              console.error('No response from the server while fetching threshold!');
              showNotification(dispatch, "error", "No response from the server while fetching sensitivity threshold!")
          }
      }

      fetchThreshold().then(r => {});
  }, [])

  useEffect(() => {
      const fetchEmails = async () => {
          const response = await getRecipients();
          if (response) {
              if (response.status === 200) {
                  setEmails(response.data);
              } else {
                  console.error('Error on fetching emails: ', response);
                  showNotification(dispatch, "error", "An error occurred while fetching recipients list!")
              }
          } else {
              console.error('No response from the server while fetching emails!');
              showNotification(dispatch, "error", "No response from the server while fetching recipients list!")
          }
      }

      fetchEmails().then(r => {});
  }, [])

  const onSaveThreshold = async() => {
    const formData = new FormData();
    formData.append('threshold', threshold);
    const response = await updateSensitivityThreshold(formData);
    if (response) {
        if (response.status === 200) {
          showNotification(dispatch, "success", "Sensitivity threshold saved!")
        } else {
            console.error('Error on updating threshold: ', response);
            showNotification(dispatch, "error", "An error occurred while updating sensitivity threshold!")
        }
    } else {
        console.error('No response from the server while updating threshold!');
        showNotification(dispatch, "error", "No response from the server while updating sensitivity threshold!")
    }
  }

  const onEmailChange = (event) => {
    setEmail(event.target.value);
  }

  const onAddEmail = async () => {
    const formData = new FormData();
    formData.append('email', email);
    const response = await addRecipient(formData);
    if (response) {
      if (response.status === 200) {
        setEmails(prevState => [...prevState, response.data]);
        showNotification(dispatch, "success", "Recipients list has been updated!")
      } else {
          console.error('Error on updating recipients list: ', response);
          showNotification(dispatch, "error", "An error occurred while updating recipients list!")
      }
    } else {
      console.error('No response from the server while adding recipient!');
      showNotification(dispatch, "error", "No response from the server while updating recipients list!")
    }
  }

  const onDeleteEmail = async(emailToDelete) => {
    const response = await deleteRecipient(emailToDelete.id);
    if (response) {
      if (response.status === 200) {
        const updatedEmails = emails.filter(em => em.id !== emailToDelete.id);
        setEmails(updatedEmails);
      } else {
          console.error('Error on deleting recipient: ', response);
          showNotification(dispatch, "error", "An error occurred while removing recipient!")
      }
    } else {
      console.error('No response from the server while deleting recipient!');
      showNotification(dispatch, "error", "No response from the server while removing recipient!")
    }
  }

  return (
    <MDBox sx={{ml: 5}}>
      <MDBox sx={{mb: 5}}>
        <FormControl sx={{width: 300}}>
          <InputLabel id="threshold-select">Sensitivity Threshold</InputLabel>
          <Select
            labelId="threshold-select"
            id="threshold-select"
            value={threshold}
            label="Sensitivity Threshold"
            onChange={onThresholdChange}
            MenuProps={thresholdMenuProps}
          >
            {thresholdMenuItems}
          </Select>
          <MDButton
            onClick={onSaveThreshold}
            variant="contained"
            color="info"
          >
            Save
          </MDButton>
        </FormControl>
      </MDBox>
      <Divider />
      <MDBox sx={{display: "flex", height: 200, alignItems: "center"}}>
        <FormControl sx={{width: 300, mr: 3}}>
          <TextField
            label="Recipient Email"
            variant="outlined"
            value={email}
            onChange={onEmailChange}
          />
          <MDButton
            onClick={onAddEmail}
            variant="contained"
            color="info"
          >
            Add recipient
          </MDButton>
        </FormControl>
        <List dense={true}
          sx={{
            width: '100%',
            maxWidth: 300,
            bgcolor: 'background.paper',
            position: 'relative',
            overflowY: 'auto',
            overflowX: 'hidden',
            maxHeight: "100%",
            // height: '100%',
            '& ul': { padding: 0 },
          }}
          subheader={<ListSubheader>Current Recipients</ListSubheader>}
        >
          {emails.map((value, key) => (
            <ListItem
              key={key}
              secondaryAction={
                <IconButton edge="start" aria-label="delete" onClick={e => onDeleteEmail(value)}>
                  <DeleteIcon />
                </IconButton>
              }
            >
              <ListItemText
                primary={value.email}
              />
            </ListItem>
          ))}
        </List>
      </MDBox>
    </MDBox>
  );
}
