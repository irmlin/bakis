import MDBox from "Components/MDBox";
import MDButton from "Components/MDButton";
import {useState} from "react";
import {
    Dialog,
    DialogActions,
    DialogContent,
    DialogContentText,
    DialogTitle,
    FormControl, FormControlLabel, FormLabel, Radio,
    RadioGroup
} from "@mui/material";
import MDInput from "Components/MDInput";
import {startStream, uploadSource} from "Services/MediaService";
import {
    showNotification,
    useMaterialUIController
} from "Context/MaterialUIContextProvider";
import Divider from "@mui/material/Divider";
import {useAuthorizationContext} from "../../../../Context/AuthorizationContextProvider";


export default function LiveStreamControlPanel(props) {

    const sourceTypes = {VIDEO: "VIDEO", STREAM: "STREAM"}

    const { newSourceTrigger, onNewSourceTrigger } = props;

    const [username, allowed] = useAuthorizationContext();

    const [sourceDialogOpen, setSourceDialogOpen] = useState(false);
    const [source, setSource] = useState({
        "file": null,
        "title": "",
        "description": "",
        "type": sourceTypes.VIDEO,
        "streamUrl": ""
    });
    const [controller, dispatch] = useMaterialUIController();

    const onSelectVideoSourceButtonClick = () => {
        setSourceDialogOpen(true);
    };

    const onSourceDialogClose = () => {
        setSourceDialogOpen(false);
    }

    const handleFileChange = (event) => {
        const file = event.target.files[0];
        setSource({
            ...source,
            file: file
        });
    };

    const onTitleTextfieldChange = (event) => {
        setSource({
            ...source,
            title: event.target.value
        });
    };

    const onDescriptionTextfieldChange = (event) => {
        setSource({
            ...source,
            description: event.target.value
        });
    };

    function validateForm() {
        if (!source.title) {
            showNotification(dispatch, "error", "Source title field is required!")
            return false;
        }
        else if (!source.description) {
            showNotification(dispatch, "error", "Source description field is required!")
            return false;
        }
        else if (source.type === sourceTypes.VIDEO && !source.file) {
            showNotification(dispatch, "error", "Please select a video file!")
            return false;
        }
        else if (source.type === sourceTypes.STREAM && !source.streamUrl) {
            showNotification(dispatch, "error", "Stream URL field is required!");
            return false;
        }
        return true;
    }

    const startStreamInServer = async (video_id) => {
        const responseStartStream = await startStream(video_id);
        if (responseStartStream) {
            if (responseStartStream.status === 200) {
                onSourceDialogClose();
                console.log(`Video ID ${video_id} is now being streamed.`)
                showNotification(dispatch, "success", "Video source is now streaming!")
                onNewSourceTrigger(!newSourceTrigger);
            } else {
                console.error('Error on triggering stream: ', responseStartStream);
                showNotification(dispatch, "error", "An error occurred while starting the stream!")
            }
        } else {
            console.error('No response from the server while triggering stream!');
            showNotification(dispatch, "error", "No response from the server!")
        }
    }

    const onStartAnalysisButtonClick = async () => {
        if (!validateForm()) {
            return;
        }
        // FormData object to send form data
        const formData = new FormData();

        // Add form fields and files to the FormData object
        formData.append('title', source.title);
        formData.append('description', source.description);
        formData.append('source_type', source.type);
        if (source.type === sourceTypes.VIDEO)
            formData.append('video_file', source.file);
        else
            formData.append('stream_url', source.streamUrl);
        console.log(source.streamUrl)
        const responseUpload = await uploadSource(formData);
        if (responseUpload) {
            if (responseUpload.status === 200) {
                console.log(`Video ID ${responseUpload.data.id} uploaded successfully:`);
                await startStreamInServer(responseUpload.data.id);
            } else {
                console.error('Error uploading video:', responseUpload);
                showNotification(dispatch, "error", responseUpload.response.data.detail)
            }
        } else {
            console.error('No response from the server while uploading video!');
            showNotification(dispatch, "error", "No response from the server!")
        }
    }

    const onTypeSelectChange = (event) => {
        setSource({
            ...source,
            type: event.target.value
        });
    }

    const onStreamUrlTextfieldChange = (event) => {
        setSource({
            ...source,
            streamUrl: event.target.value
        });
    }

    return (
        allowed &&
        <>
            <MDBox mt={2} mb={4}>
                <MDButton
                  onClick={onSelectVideoSourceButtonClick}
                  variant="contained"
                  color="info"
                >
                  ADD VIDEO SOURCE
                </MDButton>
            </MDBox>
            <Dialog
              open={sourceDialogOpen}
              onClose={onSourceDialogClose}
              fullWidth
            >
                <DialogTitle>Select Video Source for Analysis</DialogTitle>
                <DialogContent>
                    <Divider sx={{mt: 0, mb: 0}} variant={"fullWidth"} />
                    <FormControl>
                      <FormLabel id="source-type-radio-group" disabled sx={{fontSize:16, fontWeight:"bold"}}>Source Type</FormLabel>
                      <RadioGroup
                        aria-labelledby="source-type-radio-group"
                        name="source-type-radio-group"
                        value={source.type}
                        onChange={onTypeSelectChange}
                        row
                        sx={{mb: 2}}
                      >
                        <FormControlLabel value={sourceTypes.VIDEO} control={<Radio />} label="Video" />
                        <FormControlLabel value={sourceTypes.STREAM} control={<Radio />} label="Stream" />
                      </RadioGroup>
                    </FormControl>
                    <MDBox mb={2}>
                        <MDInput label="Video Source Title" value={source.title} fullWidth onChange={onTitleTextfieldChange} />
                    </MDBox>
                    <MDBox mb={2}>
                        <MDInput label="Video Source Description" value={source.description} fullWidth onChange={onDescriptionTextfieldChange} />
                    </MDBox>
                    {
                        source && source.type === sourceTypes.VIDEO ? (
                            <MDBox>
                                <input
                                    type="file"
                                    onChange={handleFileChange}
                                    accept=".mov,.mp4,.avi"
                                />
                            </MDBox>
                        ) : (
                            <MDBox>
                                <MDInput label="Stream URL" value={source.streamUrl} fullWidth onChange={onStreamUrlTextfieldChange} />
                            </MDBox>
                        )
                    }
                </DialogContent>
                <DialogActions>
                    <MDButton
                        onClick={onStartAnalysisButtonClick}
                        variant="contained"
                        color="success"
                    >
                    Start analysis
                    </MDButton>
                </DialogActions>
            </Dialog>
        </>
    );
}