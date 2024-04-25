import {useRef, useEffect, useState} from 'react';
import MDAlert from "../MDAlert";
import MDTypography from "../MDTypography";
import MDButton from "../MDButton";
import Icon from "@mui/material/Icon";
import DeleteIcon from '@mui/icons-material/Delete';
import IconButton from "@mui/material/IconButton";
import {CircularProgress, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle} from "@mui/material";
import MDInput from "../MDInput";
import StreamStatusChart from "../../layouts/dashboard/components/StreamStatusChart";
import Card from "@mui/material/Card";
import MDBox from "../MDBox";

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
            if (counter === hitCountForChartUpdate) {
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

  const onConfirmRemoveButtonClick = () => {
    onStreamRemove();
    closeRemoveConfirmDialog();
  }

  const closeRemoveConfirmDialog = () => {
    setRemoveConfirmDialogOpen(false);
  }

  const openRemoveConfirmDialog = () => {
    setRemoveConfirmDialogOpen(true);
  }

  // useEffect(() => {
  //   // Make sure Video.js player is only initialized once
  //   if (!playerRef.current) {
  //     // The Video.js player needs to be _inside_ the component el for React 18 Strict Mode.
  //     const videoElement = document.createElement("video-js");
  //     videoElement.classList.add('vjs-big-play-centered');
  //     videoRef.current.appendChild(videoElement);
  //     const player = playerRef.current = videojs(videoElement, playerOptions, () => {
  //       // videojs.log('player is ready');
  //       onReady && onReady(player);
  //     });
  //     const ws = wsRef.current = new WebSocket(wsUrl);
  //     player.src({src: "sample.jpg", type: "image/jpeg"})
  //
  //     ws.onmessage = (event) => {
  //       player.src( URL.createObjectURL(event.data));
  //
  //       // const blob = new Blob([event.data], { type: 'image/jpeg' });
  //       // const blobUrl = URL.createObjectURL(event.data);
  //       // player.src({ src: blobUrl });
  //     };
  //
  //   // You could update an existing player in the `else` block here
  //   // on prop change, for example:
  //   } else {
  //     console.log('fuck')
  //     const player = playerRef.current;
  //     player.autoplay(playerOptions.autoplay);
  //     player.src(playerOptions.sources);
  //   }
  // }, [videoRef]);

  // // Dispose the Video.js player when the functional component unmounts
  // useEffect(() => {
  //   const player = playerRef.current;
  //   const ws = wsRef.current;
  //
  //   return () => {
  //     if (player && !player.isDisposed()) {
  //       console.log("Disposing stream player.");
  //       player.dispose();
  //       playerRef.current = null;
  //     }
  //     if (ws) {
  //       console.log("Closing web socket con.");
  //       ws.close();
  //       wsRef.current = null;
  //     }
  //   };
  // }, [playerRef]);

  return (
    <Card sx={{height: "100%"}}>
      {
        loading ? (
          <MDBox mb={5} mt={5} display="flex" justifyContent="center">
            <CircularProgress color={'info'}/>
          </MDBox>
        ) : (
          <>
            <div style={{position: "relative", padding: "1rem"}}>
              <img src={frame} style={{top: 0, left: 0, width: '100%', height: '100%', objectFit: 'contain'}}
                   alt="Video"/>
              {/*{streamEndAlertVisible && (*/}
              {/*  <MDAlert*/}
              {/*    color="dark"*/}
              {/*    style={{position: 'absolute', bottom: 0, left: 0, width: '100%', margin: 0}}*/}
              {/*  >*/}
              {/*    {streamEndMessage}*/}
              {/*  </MDAlert>*/}
              {/*)}*/}
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
                <IconButton color="error" size="large" onClick={openRemoveConfirmDialog}>
                  <DeleteIcon/>
                </IconButton>
              </div>
            </div>
            <Dialog
              open={removeConfirmDialogOpen}
              onClose={closeRemoveConfirmDialog}
            >
              <DialogTitle>Terminate stream for <i>{streamInfo.title}?</i></DialogTitle>
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
