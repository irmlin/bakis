import {useEffect, useState} from "react";
import {getLiveStreams, removeLiveStream} from "Services/MediaService";
import {StreamPlayer} from "Components/Media/StreamPlayer";
import Grid from "@mui/material/Grid";
import {showNotification, useMaterialUIController} from "../../../../Context/MaterialUIContextProvider";
import {getSensitivityThreshold} from "../../../../Services/SettingsService";


export default function LiveStreamPanel(props) {

    const { newSourceTrigger } = props;
    const [liveStreams, setLiveStreams] = useState([]);
    const [threshold, setThreshold] = useState(1.0);

    const [controller, dispatch] = useMaterialUIController();

    const isObjectInArray = (array, id) => {
        return array.some(obj => obj && obj.id === id);
    };

    const handleRemoveStream = async (streamId) => {
        const response = await removeLiveStream(streamId);
        console.log(response);
        if (response) {
            if (response.status === 200 || response.response.status === 400) {
                setLiveStreams(prevStreams => {
                    return prevStreams.filter(stream => stream && stream.id !== streamId);
                });
                showNotification(dispatch, "success", "Video stream has been removed!")
            } else {
                console.error('Error on removing live stream: ', response);
                showNotification(dispatch, "error", "An error occurred while attempting to terminate stream!")
            }
        } else {
            console.error('No response from the server while removing stream!');
            showNotification(dispatch, "error", "No response from the server while attempting to remove stream!")
        }
    };

    useEffect(() => {
        const fetchLiveVideos = async () => {
            const response = await getLiveStreams();
            if (response) {
                if (response.status === 200) {
                    setLiveStreams(prevStreams => {
                        const newStreams = response.data.filter(obj => obj && !isObjectInArray(prevStreams, obj.id));
                        for (const stream of newStreams) {
                            stream["wsUrl"] = `ws://localhost:8000/api/media/source/stream/${stream.id}`;
                        }
                        return [...prevStreams, ...newStreams];
                    });
                } else {
                    console.error('Error on fetching live streams: ', response);
                    showNotification(dispatch, "error", "An error occurred while fetching live video streams!")
                }
            } else {
                console.error('No response from the server while fetching all streams!');
                showNotification(dispatch, "error", "No response from the server while fetching live video streams!")
            }
        }

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
        fetchLiveVideos().then(r => {});
        const interval = setInterval(() => {
            fetchThreshold().then(r => {}); fetchLiveVideos().then(r => {});
            }, 10000);
        return () => {
          clearInterval(interval);
        }
    }, [newSourceTrigger])

    return (
        <Grid container spacing={3}>
            { liveStreams &&
                liveStreams.map((stream, index) => (
                  stream && (
                      <Grid item xs={12} md={6} lg={6} key={stream.id}>
                          <div>
                              <StreamPlayer streamInfo={stream}
                                            onStreamRemove={() => handleRemoveStream(stream.id)}
                                            threshold={threshold}
                              />
                          </div>
                      </Grid>
                  )
                ))
            }
        </Grid>
    );
}