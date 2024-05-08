import {useEffect, useState} from "react";
import {getLiveStreams, removeLiveStream} from "Services/MediaService";
import {StreamPlayer} from "Components/Media/StreamPlayer";
import Grid from "@mui/material/Grid";
import MDBox from "../../../../Components/MDBox";
import ComplexStatisticsCard from "../../../../Examples/Cards/StatisticsCards/ComplexStatisticsCard";
import {showNotification, useMaterialUIController} from "../../../../Context";


export default function LiveStreamPanel(props) {

    const { newSourceTrigger } = props;
    const [liveStreams, setLiveStreams] = useState([]);

    const [controller, dispatch] = useMaterialUIController();

    const isObjectInArray = (array, id) => {
        return array.some(obj => obj && obj.id === id);
    };

    const handleRemoveStream = async (streamId) => {
        const response = await removeLiveStream(streamId);
        if (response) {
            if (response.status === 200) {
                setLiveStreams(prevStreams => {
                    const indexToRemove = prevStreams.findIndex(stream => stream && stream.id === streamId);
                    if (indexToRemove !== -1) {
                      const updatedStreams = [...prevStreams];
                      updatedStreams[indexToRemove] = null;
                      return updatedStreams;
                    }
                    return prevStreams;
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
                    const newStreams = response.data.filter(obj => obj && !isObjectInArray(liveStreams, obj.id));
                    for (const stream of newStreams) {
                        stream["wsUrl"] = `ws://localhost:8000/api/media/source/stream/${stream.id}`;
                    }
                    setLiveStreams([...liveStreams, ...newStreams]);
                } else {
                    console.error('Error on fetching live streams: ', response);
                    showNotification(dispatch, "error", "An error occurred while fetching live video streams!")
                }
            } else {
                console.error('No response from the server while fetching all streams!');
                showNotification(dispatch, "error", "No response from the server while fetching live video streams!")
            }
        }

        fetchLiveVideos().then(r => {});
    }, [newSourceTrigger])

    return (
        <Grid container spacing={3}>
            { liveStreams &&
                liveStreams.map((stream, index) => (
                  stream && (
                      <Grid item xs={12} md={6} lg={6} key={index}>
                          <div>
                              <StreamPlayer streamInfo={stream}
                                            onStreamRemove={() => handleRemoveStream(stream.id)}
                              />
                          </div>
                      </Grid>
                  )
                ))
            }
        </Grid>
    );
}