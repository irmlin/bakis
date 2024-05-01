import axiosInstance from "Http/httpClient"


export const getFilteredAccidents = async (skip, limit, datetime_from, datetime_to, source_ids_array) => {
  try {
    const queryParams = new URLSearchParams();
    queryParams.append("skip", skip);
    queryParams.append("limit", limit);
    if (datetime_to)
      queryParams.append("datetime_to", datetime_to);
    if (datetime_from)
      queryParams.append("datetime_from", datetime_from);
    if (source_ids_array) {
      for (const id of source_ids_array) {
        queryParams.append('source_ids', id);
      }
    }

    return await axiosInstance.get(`/accident`, {
      params: queryParams
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
