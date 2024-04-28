import axiosInstance from "Http/httpClient"


export const getAccidents = async () => {
  try {
    return await axiosInstance.get(`/accident`);
  } catch (err) {
      console.error("Failed to fetch all accidents!: ", err);
      return err.response;
  }
}


export const getAccidentImage = async (accident_id) => {
  try {
    return await axiosInstance.get(`/accident/image/${accident_id}`);
  } catch (err) {
    console.error("Failed to fetch image for accident ID: ", accident_id, err);
    return err.response;
  }
}

export const downloadAccidentVideo = async (accident_id) => {
  try {
    return await axiosInstance.get(`/accident/video/download/${accident_id}`,
      {responseType: "blob"},
      // headers: {Accept: 'video/mp4;charset=UTF-8'}}
);
  } catch (err) {
    console.error("Failed to download video for accident ID: ", accident_id, err);
    return err.response;
  }
}
