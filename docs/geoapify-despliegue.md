# Ubicaciones y rutas con Geoapify

El formulario de nuevo viaje usa Geoapify para buscar direcciones, mostrar un
mapa y calcular la distancia estimada con el perfil de camión. La clave se usa
en el navegador, por lo que debe limitarse por dominio desde Geoapify.

## Cuenta y clave

1. Crear una cuenta gratuita en https://myprojects.geoapify.com/ (no requiere tarjeta).
2. Crear un proyecto y copiar su API key.
3. En Geoapify, restringir la clave a los dominios de Vercel usados por Trukly
   y a localhost para desarrollo. Habilitar Autocomplete, Reverse Geocoding,
   Routing y Map Tiles.

## Railway

Antes de desplegar el backend que incluye los nuevos campos, ejecutar una vez
`backend/database/migrations/2026_09_18_viaje_ubicaciones.sql` en la base MySQL
de Railway. La migración amplía las direcciones y agrega cuatro coordenadas
opcionales; conserva los viajes existentes. La CLI de Railway debe estar
autenticada o puede usarse cualquier cliente SQL conectado a esa base.

El backend no necesita la clave de Geoapify.

## Vercel

En Project Settings > Environment Variables del proyecto frontend agregar:

- `VITE_GEOAPIFY_API_KEY`: la clave del proyecto Geoapify.
- `VITE_API_URL`: la URL pública del backend Railway, por ejemplo
  `https://trukly-production.up.railway.app`.

Seleccionar Production y Preview si se usan ambas. Vercel incorpora estas
variables al compilar Vite. Tras agregarlas, crear un nuevo deployment; las
implementaciones existentes no reciben cambios de variables de entorno.
Si el proyecto de Vercel apunta al monorepo, configurar Root Directory como
`frontend`, Build Command como `npm run build` y Output Directory como `dist`.
`frontend/vercel.json` conserva las rutas del panel al recargar la página.

Para desarrollo local, poner las mismas variables en `frontend/.env`, que está
ignorado por Git.
