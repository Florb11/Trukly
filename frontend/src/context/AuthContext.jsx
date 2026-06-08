import { createContext, useContext, useState } from "react";

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem("token"));

  const [usuario, setUsuario] = useState(() => {
    const usuarioGuardado = localStorage.getItem("usuario");

    if (!usuarioGuardado) {
      return null;
    }

    try {
      return JSON.parse(usuarioGuardado);
    } catch (error) {
      localStorage.removeItem("usuario");
      return null;
    }
  });

  const login = (tokenRecibido, usuarioRecibido) => {
    localStorage.setItem("token", tokenRecibido);
    localStorage.setItem("usuario", JSON.stringify(usuarioRecibido));

    setToken(tokenRecibido);
    setUsuario(usuarioRecibido);
  };

  const actualizarUsuario = (usuarioActualizado) => {
    localStorage.setItem("usuario", JSON.stringify(usuarioActualizado));
    setUsuario(usuarioActualizado);
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("usuario");

    setToken(null);
    setUsuario(null);
  };

  const estaLogueado = !!token;

  return (
    <AuthContext.Provider
      value={{
        token,
        usuario,
        login,
        logout,
        estaLogueado,
        actualizarUsuario,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}