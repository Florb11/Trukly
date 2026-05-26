export const fetchConToken = async (url, opciones = {}) => {
  const token = localStorage.getItem("token");

  const respuesta = await fetch(url, {
    ...opciones,
    headers: {
      ...opciones.headers,
      Authorization: `Bearer ${token}`,
    },
  });

  const data = await respuesta.json();

  if (respuesta.status === 401 || respuesta.status === 422) {
    localStorage.removeItem("token");
    localStorage.removeItem("usuario");

    window.location.href = "/login?sesionExpirada=true";
    return null;
  }

  return { respuesta, data };
};