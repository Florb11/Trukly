import { createContext, useContext, useState } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("trukly_mobile_token"));
  const [usuario, setUsuario] = useState(() => {
    try { return JSON.parse(localStorage.getItem("trukly_mobile_user")) || null; } catch { return null; }
  });

  const login = (nextToken, nextUser) => {
    localStorage.setItem("trukly_mobile_token", nextToken);
    localStorage.setItem("trukly_mobile_user", JSON.stringify(nextUser));
    setToken(nextToken);
    setUsuario(nextUser);
  };

  const logout = () => {
    localStorage.removeItem("trukly_mobile_token");
    localStorage.removeItem("trukly_mobile_user");
    setToken(null);
    setUsuario(null);
  };

  return <AuthContext.Provider value={{ token, usuario, login, logout }}>{children}</AuthContext.Provider>;
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() { return useContext(AuthContext); }
