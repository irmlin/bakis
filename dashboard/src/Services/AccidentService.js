import axiosInstance from "Http/httpClient"


export const getFilteredAccidents = async (queryParams) => {
  try {
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
      {responseType: "blob",                 headers: {
                    Accept: 'video/mp4;charset=UTF-8'
                },},
      // headers: {Accept: 'video/mp4;charset=UTF-8'}}
);
  } catch (err) {
    console.error("Failed to download video for accident ID: ", accident_id, err);
    return err.response;
  }
}

// export const showAccidentVideo = async (accident_id) => {
//   try {
//     return await axiosInstance.get(`/accident/video/display/${accident_id}`,
//       {responseType: "blob"}
// );
//   } catch (err) {
//     console.error("Failed to download video for accident ID: ", accident_id, err);
//     return err.response;
//   }
// }

export const exportAccidentsPdf = async (queryParams) => {
  try {
    return await axiosInstance.get(`/accident/report/pdf`,
      {responseType: "blob", params: queryParams},
);
  } catch (err) {
    console.error("Failed to export accidents PDF: ", err);
    return err.response;
  }
}

export const exportAccidentsExcel = async (queryParams) => {
  try {
    return await axiosInstance.get(`/accident/report/excel`,
      {responseType: "blob", params: queryParams},
);
  } catch (err) {
    console.error("Failed to export accidents excel: ", err);
    return err.response;
  }
}