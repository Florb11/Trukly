import { signOut } from "firebase/auth";
import { auth } from "../firebase";

export const fetchConToken = async (url, opciones = {}) => {
  const token = localStorage.getItem("token") || sessionStorage.getItem("token");

  const respuesta = await fetch(url, {
    ...opciones,
    headers: {
      "Content-Type": "application/json",
      ...(opciones.headers || {}),
      Authorization: `Bearer ${token}`,
    },
  });

  const texto = await respuesta.text();

  let data;

  try {
    data = texto ? JSON.parse(texto) : {};
  } catch {
    data = {
      mensaje:
        "El servidor no devolvió JSON. Revisar si la ruta existe o si Flask tiró un error.",
      detalle: texto,
    };
  }

  const tokenActual = localStorage.getItem("token") || sessionStorage.getItem("token");
  if ([401, 422].includes(respuesta.status) && token === tokenActual) {
    localStorage.removeItem("token");
    localStorage.removeItem("usuario");
    sessionStorage.removeItem("token");
    sessionStorage.removeItem("usuario");

    await signOut(auth).catch(() => {});
    window.location.href = "/login?sesionExpirada=true";
    return null;
  }

  return { respuesta, data };
};
