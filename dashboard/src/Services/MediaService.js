import axiosInstance from "Http/httpClient"

export const uploadSource = async (data) => {
  try {
    return await axiosInstance.post("/media", data);
  } catch (err) {
      console.error("Failed to upload video source: ", data, err);
      return err.response;
  }
};