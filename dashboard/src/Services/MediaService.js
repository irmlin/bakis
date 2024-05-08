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
    return await axiosInstance.get(`/media/source/inference/${video_id}`);
  } catch (err) {
      console.error("Failed to start stream for source ID: ", video_id, err);
      return err.response;
  }
};

export const getLiveStreams = async () => {
  try {
    return await axiosInstance.get(`/media/source/stream`);
  } catch (err) {
      console.error("Failed to fetch all live streams: ", err);
      return err.response;
  }
}

export const getFilteredSources = async (queryParams) => {
  try {
    return await axiosInstance.get(`/media/source`, {params: queryParams});
  } catch (err) {
      console.error("Failed to fetch all sources: ", err);
      return err.response;
  }
}

export const removeLiveStream = async (source_id) => {
  try {
    return await axiosInstance.put(`/media/source/stream/${source_id}`);
  } catch (err) {
      console.error("Failed to start stream for source ID: ", source_id, err);
      return err.response;
  }
};

export const deleteSource = async (sourceId) => {
  try {
    return await axiosInstance.delete(`/media/source/${sourceId}`);
  } catch (err) {
      console.error("Failed to delete source with ID: ", sourceId, err);
      return err.response;
  }
};
