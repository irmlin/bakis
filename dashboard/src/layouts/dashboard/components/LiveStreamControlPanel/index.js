import MDBox from "Components/MDBox";
import MDButton from "Components/MDButton";
import {useRef, useState} from "react";
import {Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle} from "@mui/material";
import MDInput from "../../../../Components/MDInput";
import {uploadSource} from "../../../../Services/MediaService";


export default function LiveStreamControlPanel() {

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
        // const url = URL.createObjectURL(file);
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

        try {
            console.log(formData);
            const response = await uploadSource(formData);

            // Check if the request was successful
            if (response.status === 200) {
                console.log('Video uploaded successfully:', response);
            } else {
                // Handle error
                console.error('Error uploading video:', response);
            }
        } catch (error) {
            console.error('Error uploading video:', error);
        }
    }

    return (
        <>
            <MDBox mt={4.5}>
                <MDButton
                  onClick={onSelectVideoSourceButtonClick}
                  variant="outlined"
                  color="dark"
                >
                  Select video source for analysis
                </MDButton>
            </MDBox>
            <Dialog
              open={sourceDialogOpen}
              onClose={onSourceDialogClose}
            >
                <DialogTitle>Select Video Source for Analysis</DialogTitle>
                <DialogContent>
                    <DialogContentText>
                        Upload new video source
                    </DialogContentText>
                    <MDInput label="Source title" fullWidth onChange={onTitleTextfieldChange} />
                    <MDInput label="Source description" fullWidth onChange={onDescriptionTextfieldChange} />
                    <input
                        type="file"
                        onChange={handleFileChange}
                        accept=".mov,.mp4,.avi"
                    />
                    {/*<button onClick={handleChoose}>Choose</button>*/}
                </DialogContent>
                <DialogActions>
                    <MDButton
                        onClick={onStartAnalysisButtonClick}
                        variant="outlined"
                        color="dark"
                    >
                    Start analysis
                    </MDButton>
                </DialogActions>
            </Dialog>
        </>
    );
}