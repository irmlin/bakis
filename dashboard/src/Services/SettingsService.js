import axiosInstance from "Http/httpClient"


export const updateSensitivityThreshold = async (data) => {
  try {
    return await axiosInstance.put(`/settings/threshold`, data
);
  } catch (err) {
    console.error("Failed to update sensitivity threshold: ", err);
    return err.response;
  }
}


export const getSensitivityThreshold = async () => {
  try {
    return await axiosInstance.get(`/settings/threshold`,
);
  } catch (err) {
    console.error("Failed to get sensitivity threshold: ", err);
    return err.response;
  }
}

export const getRecipients = async () => {
  try {
    return await axiosInstance.get(`/settings/recipient`,
);
  } catch (err) {
    console.error("Failed to get recipients: ", err);
    return err.response;
  }
}

export const addRecipient = async (data) => {
  try {
    return await axiosInstance.post(`/settings/recipient`, data
);
  } catch (err) {
    console.error("Failed to add recipient: ", err);
    return err.response;
  }
}

export const deleteRecipient = async (recipient_id) => {
  try {
    console.log(recipient_id)
    return await axiosInstance.delete(`/settings/recipient/${recipient_id}`
);
  } catch (err) {
    console.error("Failed to delete recipient: ", err);
    return err.response;
  }
}