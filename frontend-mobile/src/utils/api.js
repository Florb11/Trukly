export const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

export async function apiFetch(path, options = {}) {
  const token = localStorage.getItem("trukly_mobile_token");
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
  const text = await response.text();
  let data;
  try { data = text ? JSON.parse(text) : {}; } catch { data = { mensaje: "Respuesta inválida del servidor" }; }

  if ([401, 422].includes(response.status) && token) {
    localStorage.removeItem("trukly_mobile_token");
    localStorage.removeItem("trukly_mobile_user");
    window.location.href = "/login?sesionExpirada=true";
    return null;
  }
  return { response, data };
}
