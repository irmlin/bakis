import {useEffect, useState} from "react";
import {getLiveStreams} from "../../../../Services/MediaService";
import {downloadAccidentVideo, getAccidentImage} from "../../../../Services/AccidentService";
import {CircularProgress} from "@mui/material";
import MDButton from "../../../../Components/MDButton";


export default function DownloadableVideo({accidentId}) {

  const [imgSrc, setImgSrc] = useState(null);

  const onDownloadVideoButtonClick = async () => {
    const response = await downloadAccidentVideo(accidentId);
    if (response) {
        if (response.status === 200) {
          const disposition = response.headers['content-disposition'];
          console.log(response.headers)
          console.log(disposition)
          let filename = disposition.split(/;(.+)/)[1].split(/=(.+)/)[1];
          if (filename.toLowerCase().startsWith("utf-8''"))
             filename = decodeURIComponent(filename.replace("utf-8''", ''));
          else
             filename = filename.replace(/['"]/g, '');
          const url = window.URL.createObjectURL(response.data);
          const a = document.createElement("a");
          a.href = url;
          a.download = filename;
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
          document.body.removeChild(a);
        } else {
            console.error('Error downloading accident video: ', response);
        }
    } else {
        console.error('No response from the server while downloading accident video!');
    }
  }

  return (
    <>
      <MDButton
        onClick={onDownloadVideoButtonClick}
        variant="contained"
        color="info"
      >
        Download
      </MDButton>
    </>
  );
}