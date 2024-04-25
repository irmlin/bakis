import MDBox from "Components/MDBox";
import MDButton from "Components/MDButton";
import {useState} from "react";
import {Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle} from "@mui/material";
import MDInput from "Components/MDInput";
import {startStream, uploadSource} from "Services/MediaService";


export default function LiveStreamControlPanel(props) {

    const { newSourceTrigger, onNewSourceTrigger } = props;

    const [sourceDialogOpen, setSourceDialogOpen] = useState(false);
    const [source, setSource] = useState({
        "file": null,
        "title": "",
        "description": ""
    });

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
        return source.file && source.title && source.description;
    }

    const startStreamInServer = async (video_id) => {
        const responseStartStream = await startStream(video_id);
        if (responseStartStream) {
            if (responseStartStream.status === 200) {
                onSourceDialogClose();
                console.log(`Video ID ${video_id} is now being streamed.`)
                onNewSourceTrigger(!newSourceTrigger);
            } else {
                console.error('Error on triggering stream: ', responseStartStream);
            }
        } else {
            console.error('No response from the server while triggering stream!');
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
        formData.append('video_file', source.file);

        const responseUpload = await uploadSource(formData);
        if (responseUpload) {
            if (responseUpload.status === 200) {
                console.log(`Video ID ${responseUpload.data.id} uploaded successfully:`);
                await startStreamInServer(responseUpload.data.id);
            } else {
                console.error('Error uploading video:', responseUpload);
            }
        } else {
            console.error('No response from the server while uploading video!');
        }
    }

    return (
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
                    <MDBox mb={1} mt={1}>
                        <MDInput label="Video Source Title" fullWidth onChange={onTitleTextfieldChange} />
                    </MDBox>
                    <MDBox mb={1}>
                        <MDInput label="Video Source Description" fullWidth onChange={onDescriptionTextfieldChange} />
                    </MDBox>
                    <input
                        type="file"
                        onChange={handleFileChange}
                        accept=".mov,.mp4,.avi"
                    />
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