# Trukly Mobile

PWA independiente para choferes. Comparte la API y la base de datos con el frontend web, pero tiene su propio build, rutas, manifest y despliegue.

## Desarrollo local

```bash
npm install
npm run dev
```

La API se toma de `VITE_API_URL`. Si no está definida, usa `http://localhost:5000`.

## Despliegue en Vercel

Crear un segundo proyecto de Vercel conectado al mismo repositorio y configurar:

- Root Directory: `frontend-mobile`
- Framework Preset: Vite
- Build Command: `npm run build`
- Output Directory: `dist`
- Variable de entorno: `VITE_API_URL` con la URL HTTPS del backend

El proyecto web existente conserva `frontend` como Root Directory. La URL del proyecto mobile es la que debe ingresarse en PWABuilder para generar el paquete Android.

## QR de viaje

El lector acepta cualquiera de estos contenidos:

```text
TRUKLY:VIAJE:24
24
https://mobile.example.com/escanear?viaje=24
```

El backend valida que el viaje pertenezca al chofer y decide si puede registrar check-in o check-out según su estado.
