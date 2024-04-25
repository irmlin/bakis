import {useEffect, useState} from "react";
import {getLiveStreams} from "../../../../Services/MediaService";
import {getAccidentImage} from "../../../../Services/AccidentService";
import {CircularProgress} from "@mui/material";


export default function ImageLoader({accidentId}) {

  const [imgSrc, setImgSrc] = useState(null);

  useEffect(() => {
      const fetchImage = async () => {
          const response = await getAccidentImage(accidentId);
          if (response) {
              if (response.status === 200) {
                setImgSrc(response.data);
              } else {
                  console.error('Error on fetching accident image: ', response);
              }
          } else {
              console.error('No response from the server while fetching accident image!');
          }
      }

      fetchImage().then(r => {});
  }, [])

  return (
    <>
      {
        imgSrc ? (
          <img src={`data:image/jpeg;base64,${imgSrc}`}></img>
        ) : (
          <CircularProgress color={"info"} size={20}/>
        )
      }
    </>
  );
}