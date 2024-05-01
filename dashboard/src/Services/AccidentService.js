import axiosInstance from "Http/httpClient"


export const getFilteredAccidents = async (skip, limit, datetime_from, datetime_to, source_ids) => {
  try {
    return await axiosInstance.get(`/accident`, {
      params: {
        skip,
        limit,
        datetime_from,
        datetime_to,
        source_ids
      }
    });
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
