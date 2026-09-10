import { createContext, useContext, useState } from "react";

const AuthContext = createContext();

const obtenerStorageActivo = () => (
  localStorage.getItem("token") ? localStorage : sessionStorage
);

export function AuthProvider({ children }) {
  const [storageActivo, setStorageActivo] = useState(obtenerStorageActivo);
  const [token, setToken] = useState(
    localStorage.getItem("token") || sessionStorage.getItem("token")
  );

  const [usuario, setUsuario] = useState(() => {
    const usuarioGuardado = (
      localStorage.getItem("usuario") || sessionStorage.getItem("usuario")
    );

    if (!usuarioGuardado) {
      return null;
    }

    try {
      return JSON.parse(usuarioGuardado);
    } catch {
      localStorage.removeItem("usuario");
      sessionStorage.removeItem("usuario");
      return null;
    }
  });

  const login = (tokenRecibido, usuarioRecibido, recordar = true) => {
    const storage = recordar ? localStorage : sessionStorage;

    localStorage.removeItem("token");
    localStorage.removeItem("usuario");
    sessionStorage.removeItem("token");
    sessionStorage.removeItem("usuario");

    storage.setItem("token", tokenRecibido);
    storage.setItem("usuario", JSON.stringify(usuarioRecibido));

    setStorageActivo(storage);
    setToken(tokenRecibido);
    setUsuario(usuarioRecibido);
  };

  const actualizarUsuario = (usuarioActualizado) => {
    storageActivo.setItem("usuario", JSON.stringify(usuarioActualizado));
    setUsuario(usuarioActualizado);
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("usuario");
    sessionStorage.removeItem("token");
    sessionStorage.removeItem("usuario");

    setStorageActivo(localStorage);
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
