import AuthContext from "../contexts/AuthContext";
import { useContext } from "react";

export function useAuthContext() {
  return useContext(AuthContext);
}
