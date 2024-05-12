import axiosInstance from "Http/httpClient"


export const login = async (data) => {
  try {
    return await axiosInstance.post("/auth/login", data);
  } catch (err) {
      console.error("Failed to upload video source: ", data, err);
      return err.response;
  }
};

export const getUser = async () => {
  try {
    return await axiosInstance.get("/auth/user");
  } catch (err) {
      console.error("Failed to fetch user information!", err);
      return err.response;
  }
};