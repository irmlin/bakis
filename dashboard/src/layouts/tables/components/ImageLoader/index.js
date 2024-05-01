import {useEffect, useState} from "react";
import {getLiveStreams} from "../../../../Services/MediaService";
import {getAccidentImage} from "../../../../Services/AccidentService";
import {CircularProgress} from "@mui/material";


export default function ImageLoader({accidentId}) {

  const [imgSrc, setImgSrc] = useState(null);
  const [originalSize, setOriginalSize] = useState({ width: 0, height: 0 });
  const W_RESIZE = 800;
  const H_RESIZE = 300;

  useEffect(() => {
      const fetchImage = async () => {
          const response = await getAccidentImage(accidentId);
          if (response) {
              if (response.status === 200) {
                setImgSrc(response.data);
                getImageSize(response.data);
              } else {
                  console.error('Error on fetching accident image: ', response);
              }
          } else {
              console.error('No response from the server while fetching accident image!');
          }
      }

      fetchImage().then(r => {});
  }, [])

    const getImageSize = (base64String) => {
    const img = new Image();
    img.onload = () => {
      setOriginalSize({ width: img.width, height: img.height });
    };
    img.src = `data:image/jpeg;base64,${base64String}`;
  };

  const calculateResizedDimensions = () => {
    if (originalSize.width === 0 || originalSize.height === 0) {
      return {};
    }

    if (originalSize.width > originalSize.height) {
      return {
        width: W_RESIZE,
        height: (W_RESIZE * originalSize.height) / originalSize.width,
      };
    } else {
      return {
        width: (H_RESIZE * originalSize.width) / originalSize.height,
        height: H_RESIZE,
      };
    }
  };

  const resizedDimensions = calculateResizedDimensions();

  return (
    <>
      {
        imgSrc ? (
          <img
            src={`data:image/jpeg;base64,${imgSrc}`}
            style={{ width: resizedDimensions.width, height: resizedDimensions.height }}
          ></img>
        ) : (
          <CircularProgress color={"info"} size={20}/>
        )
      }
    </>
  );
}