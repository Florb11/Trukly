export const fetchConToken = async (url, opciones = {}) => {
  const token = localStorage.getItem("token");

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

  if (respuesta.status === 401 || respuesta.status === 422) {
    localStorage.removeItem("token");
    localStorage.removeItem("usuario");

    window.location.href = "/login?sesionExpirada=true";
    return null;
  }

  return { respuesta, data };
};