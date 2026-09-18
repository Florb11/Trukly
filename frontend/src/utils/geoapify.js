const apiKey = import.meta.env.VITE_GEOAPIFY_API_KEY;

export const hasGeoapifyKey = Boolean(apiKey);

const getJson = async (url, signal) => {
  if (!apiKey) throw new Error("Falta configurar la clave de Geoapify.");

  let response;
  try {
    response = await fetch(url, { signal });
  } catch (error) {
    if (error.name === "AbortError") throw error;
    throw new Error(
      "No se pudo conectar con Geoapify. Revisá la conexión y los dominios permitidos para la clave.",
      { cause: error },
    );
  }
  if (response.status === 401 || response.status === 403) {
    throw new Error(`Geoapify rechazó la clave (HTTP ${response.status}). Revisá la clave y permití localhost en Geoapify.`);
  }
  if (response.status === 429) {
    throw new Error("Geoapify alcanzó el límite de consultas. Intentá de nuevo más tarde.");
  }
  if (!response.ok) throw new Error(`No se pudo consultar Geoapify (HTTP ${response.status}).`);
  return response.json();
};

export const searchPlaces = async (query, signal) => {
  const params = new URLSearchParams({
    text: query,
    format: "json",
    lang: "es",
    limit: "6",
    apiKey,
  });
  const data = await getJson(
    `https://api.geoapify.com/v1/geocode/autocomplete?${params}`,
    signal,
  );
  return (data.results || []).filter(
    (place) => Number.isFinite(place.lat) && Number.isFinite(place.lon),
  );
};

export const reversePlace = async (lat, lon, signal) => {
  const params = new URLSearchParams({
    lat: String(lat),
    lon: String(lon),
    format: "json",
    lang: "es",
    apiKey,
  });
  const data = await getJson(
    `https://api.geoapify.com/v1/geocode/reverse?${params}`,
    signal,
  );
  return data.results?.[0]?.formatted || `${lat.toFixed(5)}, ${lon.toFixed(5)}`;
};

export const getTruckRoute = async (origin, destination, signal) => {
  const params = new URLSearchParams({
    waypoints: `${origin.lat},${origin.lon}|${destination.lat},${destination.lon}`,
    mode: "truck",
    units: "metric",
    apiKey,
  });
  const data = await getJson(
    `https://api.geoapify.com/v1/routing?${params}`,
    signal,
  );
  const feature = data.features?.[0];
  const meters = Number(feature?.properties?.distance);
  if (!feature || !Number.isFinite(meters)) {
    throw new Error("No se encontró una ruta entre los puntos elegidos.");
  }

  return { feature, kilometers: Math.round((meters / 1000) * 10) / 10 };
};

export const geoapifyTileUrl = apiKey
  ? `https://maps.geoapify.com/v1/tile/osm-bright/{z}/{x}/{y}.png?apiKey=${encodeURIComponent(apiKey)}`
  : "";
