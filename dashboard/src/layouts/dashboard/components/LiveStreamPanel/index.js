import {useEffect, useState} from "react";
import {getLiveStreams, removeLiveStream} from "Services/MediaService";
import {StreamPlayer} from "Components/Media/StreamPlayer";
import Grid from "@mui/material/Grid";
import MDBox from "../../../../Components/MDBox";
import ComplexStatisticsCard from "../../../../Examples/Cards/StatisticsCards/ComplexStatisticsCard";


export default function LiveStreamPanel(props) {

    const { newSourceTrigger } = props;
    const [liveStreams, setLiveStreams] = useState([]);

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
            } else {
                console.error('Error on removing live stream: ', response);
            }
        } else {
            console.error('No response from the server while removing stream!');
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
                }
            } else {
                console.error('No response from the server while fetching all streams!');
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