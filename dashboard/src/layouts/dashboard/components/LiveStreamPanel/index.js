import {useEffect, useState} from "react";
import {getLiveStreams} from "Services/MediaService";
import {StreamPlayer} from "Components/Media/StreamPlayer";


export default function LiveStreamPanel(props) {

    const { newSourceTrigger } = props;
    const [liveStreams, setLiveStreams] = useState([]);

    const isObjectInArray = (array, id) => {
        return array.some(obj => obj.id === id);
    };

    useEffect(() => {

        const fetchLiveVideos = async () => {
            const response = await getLiveStreams();
            if (response) {
                if (response.status === 200) {
                    console.log("Currently all streamed: ", response.data);
                    const newStreams = response.data.filter(obj => !isObjectInArray(liveStreams, obj.id));
                    for (const stream of newStreams) {
                        stream["wsUrl"] = `ws://localhost:8000/api/media/video/stream/${stream.id}`;
                    }
                    setLiveStreams([...liveStreams, ...newStreams]);
                    console.log('new streamed: ', newStreams);
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
        <>
            { liveStreams &&
                liveStreams.map((stream, index) => (
                    <div key={index}>
                        Streaminu {stream.id} is {stream.wsUrl}
                        <StreamPlayer wsUrl={stream.wsUrl}/>
                    </div>
                ))
            }
        </>
    );
}