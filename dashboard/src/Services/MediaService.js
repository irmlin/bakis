import axiosInstance from "Http/httpClient"

export const uploadSource = async (data) => {
  try {
    return await axiosInstance.post("/media", data);
  } catch (err) {
      console.error("Failed to upload video source: ", data, err);
      return err.response;
  }
};

export const startStream = async (video_id) => {
  try {
    return await axiosInstance.get(`/media/video/inference/${video_id}`);
  } catch (err) {
      console.error("Failed to start stream for source ID: ", video_id, err);
      return err.response;
  }
};

export const getLiveStreams = async () => {
  try {
    return await axiosInstance.get(`/media/video/stream`);
  } catch (err) {
      console.error("Failed to fetch all live streams: ", err);
      return err.response;
  }
}
