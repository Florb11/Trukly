const CACHE_NAME = "trukly-mobile-v2";
const APP_SHELL = ["/", "/manifest.webmanifest", "/pwa-192.png", "/pwa-512.png"];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL)));
  self.skipWaiting();
});

self.addEventListener("push", (event) => {
  const payload = event.data?.json() || {};
  const datos = payload.data || payload.notification || {};
  event.waitUntil((async () => {
    await self.registration.showNotification(datos.title || "Trukly", {
      body: datos.body || "Tenes un nuevo aviso.", icon: "/pwa-192.png", badge: "/pwa-192.png",
    });
    const ventanas = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
    ventanas.forEach((ventana) => ventana.postMessage({ tipo: "trukly-push" }));
  })());
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  event.waitUntil((async () => {
    const url = new URL("/notificaciones", self.location.origin).href;
    const ventanas = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
    const ventana = ventanas.find((item) => new URL(item.url).origin === self.location.origin);
    if (ventana) { await ventana.navigate(url); await ventana.focus(); }
    else await self.clients.openWindow(url);
  })());
});

self.addEventListener("activate", (event) => {
  event.waitUntil(caches.keys().then((keys) => Promise.all(
    keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key)),
  )));
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  if (event.request.method !== "GET" || url.pathname.startsWith("/api/")) return;

  if (event.request.mode === "navigate") {
    event.respondWith(fetch(event.request).catch(() => caches.match("/")));
    return;
  }

  event.respondWith(caches.match(event.request).then((cached) => cached || fetch(event.request).then((response) => {
    if (response.ok && url.origin === self.location.origin) {
      caches.open(CACHE_NAME).then((cache) => cache.put(event.request, response.clone()));
    }
    return response;
  })));
});
