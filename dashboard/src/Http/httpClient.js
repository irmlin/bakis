import axios from "axios";
import {showNotification, useMaterialUIController} from "../Context/MaterialUIContextProvider";

const axiosInstance = axios.create({
    baseURL:
        `http://${process.env.REACT_APP_BACKEND_IP}:8000/api`,
    headers: {
        "Content-Type": "multipart/form-data",
    },
});

axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

axiosInstance.interceptors.response.use(response => {
   return response;
}, error => {
  if (error.response.status === 401) {
   localStorage.setItem('admin', false);
   localStorage.setItem('username', 'guest');
   if (window.location.pathname !== "/authentication/sign-in")
      window.location = "/authentication/sign-in";
   console.log(error.response.detail);
  }
  return error;
});

export default axiosInstance;