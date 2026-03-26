import { createContext, useState, useEffect } from "react";
import { refreshUserToken } from "../api/auth";
import { setLogoutHandler, setAccessToken } from "../api/client";
import { useNavigate } from "react-router-dom";
import { loginUser } from "../api/auth";

// container of context
const AuthContext = createContext();

// component to wrap the app
export function AuthProvider({ children }) {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const handleLogout = () => {
    setUser(null);
    setIsAuthenticated(false);
    navigate("/login");
  };

  const login = async (email, password) => {
    try {
      const response = await loginUser(email, password);
      setAccessToken(response.data.accessToken);
      setUser(response.data.user);
      setIsAuthenticated(true);
      return response;
    } catch (error) {
      return error.response;
    }
  };

  // check if refreshToken exists
  useEffect(() => {
    setLogoutHandler(handleLogout);

    const checkAuth = async () => {
      try {
        const response = await refreshUserToken();
        setUser(response.data.user);
        setIsAuthenticated(true);
        setAccessToken(response.data.accessToken);
      } catch {
        setIsAuthenticated(false);
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };
    checkAuth();
  }, []); // eslint-disable-line

  return (
    <AuthContext.Provider
      value={{
        user,
        setUser,
        login,
        isAuthenticated,
        setIsAuthenticated,
        isLoading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export default AuthContext;
