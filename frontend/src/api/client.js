import axios from "axios";
import { UNSAFE_ErrorResponseImpl } from "react-router-dom";

let accessToken = null;
let logoutHandler = null;

export const api = axios.create({
  baseURL: "http://localhost:8000/",
  withCredentials: true,
  xsrfCookieName: "csrfToken",
  xsrfHeaderName: "X-CSRFToken",
});

export const setAccessToken = (token) => (accessToken = token);
export const setLogoutHandler = (callback) => (logoutHandler = callback);

api.interceptors.request.use(
  (config) => {
    if (accessToken) config.headers.Authorization = `Bearer ${accessToken}`;
    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (originalRequest.url.includes("auth/refresh-token/")) {
      return Promise.reject(error);
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const response = await axios.post(
          "http://localhost:8000/auth/refresh-token/",
          {},
          { withCredentials: true },
        );
        const newToken = response.data.accessToken;
        setAccessToken(newToken);

        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return api.request(originalRequest);
      } catch (refreshError) {
        setAccessToken(null);
        if (logoutHandler) logoutHandler();
        axios.post(
          "http://localhost:8000/auth/logout/",
          {},
          { withCredentials: true },
        );
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  },
);
