import { useCallback, useEffect, useMemo, useState } from "react";

import * as authService from "../services/authService";
import { getRefreshToken, getUsername } from "../services/tokenStorage";
import { AuthContext } from "./authContext";

export function AuthProvider({ children }) {
  // The refresh token decides the session: an expired access token is renewed automatically
  const [isAuthenticated, setIsAuthenticated] = useState(() => Boolean(getRefreshToken()));
  const [username, setUsername] = useState(() => getUsername());

  // The axios interceptor fires this event when a refresh fails
  useEffect(() => {
    const handleForcedLogout = () => {
      setIsAuthenticated(false);
      setUsername(null);
    };
    window.addEventListener("auth:logout", handleForcedLogout);
    return () => window.removeEventListener("auth:logout", handleForcedLogout);
  }, []);

  const login = useCallback(async (name, password) => {
    await authService.login(name, password);
    setUsername(name);
    setIsAuthenticated(true);
  }, []);

  const register = useCallback(async (data) => {
    await authService.register(data);
    setUsername(data.username);
    setIsAuthenticated(true);
  }, []);

  const logout = useCallback(async () => {
    await authService.logout();
    setIsAuthenticated(false);
    setUsername(null);
  }, []);

  const value = useMemo(
    () => ({ isAuthenticated, username, login, register, logout }),
    [isAuthenticated, username, login, register, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}