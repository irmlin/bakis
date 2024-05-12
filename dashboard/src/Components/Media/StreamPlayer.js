import {useRef, useEffect, useState} from 'react';
import MDAlert from "../MDAlert";
import MDTypography from "../MDTypography";
import MDButton from "../MDButton";
import DeleteIcon from '@mui/icons-material/Delete';
import IconButton from "@mui/material/IconButton";
import {CircularProgress, Dialog, DialogActions, DialogTitle} from "@mui/material";
import StreamStatusChart from "../../layouts/dashboard/components/StreamStatusChart";
import Card from "@mui/material/Card";
import MDBox from "../MDBox";
import {useAuthorizationContext} from "../../Context/AuthorizationContextProvider";

export const StreamPlayer = (props) => {

  const [frame, setFrame] = useState("");
  const [streamEndMessage, setStreamEndMessage] = useState("");
  const [streamEndAlertVisible, setStreamEndAlertVisible] = useState(false);
  const [removeConfirmDialogOpen, setRemoveConfirmDialogOpen] = useState(false);
  const [modelScores, setModelScores] = useState([]);
  const hitCountForChartUpdate = 30;
  let counter = 0;
  const [loading, setLoading] = useState(true);
  let firstFrameReceived = false;

  const wsRef = useRef(null);
  const {streamInfo, onStreamRemove} = props;

  const [username, allowed] = useAuthorizationContext();

  useEffect(() => {
    if (!wsRef.current) {
      const ws = wsRef.current = new WebSocket(streamInfo.wsUrl);
      ws.onmessage = (event) => {
        if (event.data instanceof Blob) {
          if (!firstFrameReceived) {
            firstFrameReceived = true;
            setLoading(false);
          }
          setFrame(URL.createObjectURL(event.data));
        } else {
          const parsed = JSON.parse(event.data);
          if ("scores" in parsed) {
            if (counter % hitCountForChartUpdate === 0) {
              setModelScores(parsed.scores);
              counter = 0;
            }
            counter = counter + 1;
          } else if ("detail" in parsed) {
            setStreamEndMessage(parsed.detail);
            setStreamEndAlertVisible(true);
          } else {
            console.log('Unexpected data received from socket: ', parsed);
          }
        }
      };
      ws.onerror = (e) => console.error(e);
      ws.onopen = () => console.log("Websocket opened!", streamInfo.id);
      ws.onclose = () => {
        console.log("Closing socket!", streamInfo.id);
        // wsRef.current.close();
        // wsRef.current = null;
      }
    }
    return () => {
      const ws = wsRef.current;
      if (ws) {
        ws.close();
        wsRef.current = null;
        console.log("useEffect ended, setting trigger!", streamInfo.id);
      }
    };
  }, [])

  const onConfirmRemoveButtonClick = async () => {
    await onStreamRemove();
    closeRemoveConfirmDialog();
  }

  const closeRemoveConfirmDialog = () => {
    setRemoveConfirmDialogOpen(false);
  }

  const openRemoveConfirmDialog = () => {
    setRemoveConfirmDialogOpen(true);
  }

  return (
    <Card sx={{height: "100%"}}>
      {
        loading ? (
          <MDBox mb={5} mt={5} display="flex" justifyContent="center">
            <CircularProgress color={'info'}/>
          </MDBox>
        ) : (
          <>
            <div style={{padding: "1rem"}}>
              <div style={{position: "relative"}}>
                <img src={frame} style={{width: '100%', height: '100%', opacity: streamEndAlertVisible ? "50%" : "100"}} alt="Video"/>
                {streamEndAlertVisible && (
                  <div>
                    <MDAlert
                      color="dark"
                      style={{width: '100%', bottom: 0, left: 0, position: "absolute", marginBottom: 4}}
                    >
                      {streamEndMessage}
                    </MDAlert>
                  </div>
                )}
              </div>
              <StreamStatusChart
                color="dark"
                title="Completed tasks title"
                description="Last Campaign Performance"
                modelScores={modelScores}
                size={30}
              />
              <div style={{paddingTop: 7, display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
                <MDBox>
                  <MDTypography variant="h6" textTransform="capitalize">
                    {streamInfo.title}
                  </MDTypography>
                  <MDTypography
                    component="div"
                    variant="button"
                    color="text"
                    fontWeight="light"
                  >
                    {streamInfo.description}
                  </MDTypography>
                </MDBox>
                {
                  allowed &&
                  <IconButton color="error" size="large" onClick={openRemoveConfirmDialog}>
                    <DeleteIcon/>
                  </IconButton>
                }

              </div>
            </div>
            <Dialog
              open={removeConfirmDialogOpen}
              onClose={closeRemoveConfirmDialog}
            >
              <DialogTitle>{streamEndAlertVisible ? "Clear" : "Terminate stream for video"} source <i>{streamInfo.title}?</i></DialogTitle>
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
          </>
        )
      }
    </Card>
  );
}

export default StreamPlayer;
