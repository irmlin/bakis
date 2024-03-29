import {useEffect, useState} from "react";


export default function LiveStreamPanel(props) {

    const { newSourceTrigger } = props;
    const [liveStreams, setLiveStreams] = useState([]);

    useEffect(() => {

    }, [newSourceTrigger])

    return (
        <>

        </>
    );
}