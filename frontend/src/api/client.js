import axios from "axios";

// variable to store access token
let accessToken = null;

// create axios instance and export it
export const api = axios.create({
  baseURL: "http://localhost:8000/", // localhost django
  xsrfCookieName: "csrftoken", // csrf cookie name
  xsrfHeaderName: "X-CSRFToken", // csrf header name
  withCredentials: true, // include cookies in requests
});

// function to set access token and export it
export const setAccessToken = (token) => (accessToken = token);

// =============  Promises Management  ===================

// interceptor to add access token to requests if exists
// interceptors.request >> request is about to be sent
api.interceptors.request.use(
  // resolved promise
  (config) => {
    // check if access token exists
    if (accessToken) {
      // add access token to headers
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },

  // catching errors
  (error) => Promise.reject(error),
);

// interceptor to get refresh token
// if access token is expired or invalid
api.interceptors.request.use(
  // resolved promise
  (response) => response,

  // rejected promise
  async (error) => {
    // get original request config
    const originalRequest = error.config;

    // check if error response status is 401 and original request has not been retried
    // response?.status >> optional chaining (only if response exists)
    // _retry >> custom property to avoid infinite loop
    if (error.response?.status === 401 && !originalRequest._retry) {
      // set _retry to true
      originalRequest._retry = true;

      // try to get new access token using refresh token endpoint
      try {
        const refreshResponse = await axios.post(
          "http://localhost:8000/auth/refresh-token/",
          {}, // no need data
          { withCredentials: true }, // include cookies in requests
        );

        // get new access token if post request is successful
        // accessToken from server response
        const newAccessToken = refreshResponse.data.accessToken;

        // set new access token
        setAccessToken(newAccessToken);

        // add new access token to headers
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;

        // retry original request
        return api(originalRequest);
      } catch (error) {
        // reject original request
        return Promise.reject(error);
      }
    }
  },
);
