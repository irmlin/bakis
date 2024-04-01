import {useRef, useEffect, useState} from 'react';

export const StreamPlayer = (props) => {

  const [frame, setFrame] = useState("");
  const wsRef = useRef(null);
  const {wsUrl} = props;

  useEffect(() => {
    if (!wsRef.current) {
      const ws = wsRef.current = new WebSocket(wsUrl);
      ws.onmessage = (event) => {
        setFrame(URL.createObjectURL(event.data));
      };
      ws.onerror = (e) => console.error(e);
      ws.onopen = () => console.log("Websocket opened!");
    }
    return () => {
      const ws = wsRef.current;
      if (ws) {
        ws.close();
        wsRef.current = null;
        console.log("Closed web socket connection!");
      }
    };
  }, [])

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
    <div>
      <img src={frame} width={640} height={360}/>
    </div>
  );
}

export default StreamPlayer;