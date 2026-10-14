import { getMessaging, getToken, deleteToken, isSupported } from "firebase/messaging";
import { app } from "../firebase";
import { apiFetch } from "./api";

export async function activarPush(pedirPermiso = true) {
  if (!await isSupported()) throw new Error("Este dispositivo no admite notificaciones push.");
  if (!import.meta.env.VITE_FIREBASE_VAPID_KEY) throw new Error("Falta configurar la clave VAPID de Firebase.");
  const permiso = pedirPermiso ? await Notification.requestPermission() : Notification.permission;
  if (permiso !== "granted") throw new Error("Habilitá las notificaciones en los ajustes del navegador o de la app.");
  const registro = await navigator.serviceWorker.ready;
  const token = await getToken(getMessaging(app), { vapidKey: import.meta.env.VITE_FIREBASE_VAPID_KEY, serviceWorkerRegistration: registro });
  const resultado = await apiFetch("/api/notificaciones/dispositivo", {
    method: "POST", body: JSON.stringify({ token }), signal: AbortSignal.timeout(20000),
  });
  if (!resultado?.response.ok) throw new Error(resultado?.data.mensaje || "No se pudo registrar el dispositivo.");
  localStorage.setItem("trukly_push_token", token);
}

export async function desactivarPush() {
  const token = localStorage.getItem("trukly_push_token");
  if (!token) return;
  await deleteToken(getMessaging(app));
  localStorage.removeItem("trukly_push_token");
  try {
    await apiFetch("/api/notificaciones/dispositivo", { method: "DELETE", body: JSON.stringify({ token }), signal: AbortSignal.timeout(10000) });
  } catch { /* Firebase ya invalido el token; el backend lo limpiara al enviar. */ }
}
