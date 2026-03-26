import { api } from "./client";

export const registerUser = (email, password, confirm_password) =>
  api.post("auth/register/", { email, password, confirm_password });

export const loginUser = (email, password) =>
  api.post("auth/login/", { email, password });

export const logoutUser = () => api.post("auth/logout/");

export const refreshUserToken = () => api.post("auth/refresh-token/");

export const resendActivationEmail = (email) =>
  api.post("auth/resend-activation/", { email });

export const activateAccountUser = (uidb64, token) =>
  api.get(`auth/activate/${uidb64}/${token}/`);
