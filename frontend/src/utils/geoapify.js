const apiKey = import.meta.env.VITE_GEOAPIFY_API_KEY;

export const hasGeoapifyKey = Boolean(apiKey);

const coordinateLabel = (lat, lon) => `${lat.toFixed(5)}, ${lon.toFixed(5)}`;

const geoapifyError = (message, status, detail = "", cause) => {
  const error = new Error(message, cause ? { cause } : undefined);
  error.status = status;
  error.detail = detail;
  return error;
};

const routeErrorMessage = (error) => {
  const detail = `${error.detail || ""} ${error.message || ""}`.toLowerCase();

  if (error.status === 401 || error.status === 403) {
    return "El servicio de mapas no está disponible en este momento.";
  }
  if (error.status === 429) {
    return "El servicio de mapas está ocupado. Intentá nuevamente en unos minutos.";
  }
  if (error.status >= 500 || !error.status) {
    return "No pudimos calcular la ruta en este momento. Intentá nuevamente.";
  }
  if (/too far|distance|maximum|max distance|exceed|long route/.test(detail)) {
    return "La ruta es demasiado extensa para calcularla. Elegí un origen y un destino más cercanos.";
  }
  if (/no suitable edges|not routable|unreachable|inaccessible/.test(detail)) {
    return "Uno de los puntos no es accesible para camiones. Elegí una ubicación cercana sobre una calle o ruta.";
  }
  if (/no route|route not found|no path|disconnected|different continent/.test(detail)) {
    return "No encontramos una ruta terrestre entre estas ubicaciones.";
  }
  if (/coordinate|waypoint|latitude|longitude|lat\/lon/.test(detail)) {
    return "No pudimos reconocer una de las ubicaciones. Volvé a seleccionarla.";
  }
  if (error.status === 400) {
    return "No pudimos calcular una ruta con las ubicaciones elegidas. Probá seleccionando puntos cercanos sobre una calle o ruta.";
  }
  return "No pudimos calcular la ruta en este momento. Intentá nuevamente.";
};

const getJson = async (url, signal) => {
  if (!apiKey) throw new Error("Falta configurar la clave de Geoapify.");

  let response;
  try {
    response = await fetch(url, { signal });
  } catch (error) {
    if (error.name === "AbortError") throw error;
    throw geoapifyError(
      "No se pudo conectar con Geoapify. Revisá la conexión y los dominios permitidos para la clave.",
      undefined,
      "",
      error,
    );
  }
  if (response.status === 401 || response.status === 403) {
    throw geoapifyError(
      `Geoapify rechazó la clave (HTTP ${response.status}). Revisá la clave y permití localhost en Geoapify.`,
      response.status,
    );
  }
  if (response.status === 429) {
    throw geoapifyError(
      "Geoapify alcanzó el límite de consultas. Intentá de nuevo más tarde.",
      response.status,
    );
  }
  if (!response.ok) {
    let detail = "";
    try {
      const body = await response.json();
      detail = body.message || body.error || "";
    } catch {
      // Geoapify no siempre devuelve JSON para los errores.
    }

    throw geoapifyError(
      detail
        ? `No se pudo consultar Geoapify (HTTP ${response.status}): ${detail}`
        : `No se pudo consultar Geoapify (HTTP ${response.status}).`,
      response.status,
      detail,
    );
  }
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
  if (!Number.isFinite(lat) || !Number.isFinite(lon)) {
    throw new Error("El punto seleccionado no tiene coordenadas validas.");
  }

  const params = new URLSearchParams({
    lat: String(lat),
    lon: String(lon),
    format: "json",
    lang: "es",
    apiKey,
  });
  try {
    const data = await getJson(
      `https://api.geoapify.com/v1/geocode/reverse?${params}`,
      signal,
    );
    return data.results?.[0]?.formatted || coordinateLabel(lat, lon);
  } catch (error) {
    if (error.name === "AbortError") throw error;
    if (error.status === 400) return coordinateLabel(lat, lon);
    throw error;
  }
};

export const getTruckRoute = async (origin, destination, signal) => {
  const params = new URLSearchParams({
    waypoints: `${origin.lat},${origin.lon}|${destination.lat},${destination.lon}`,
    mode: "truck",
    units: "metric",
    apiKey,
  });
  let data;
  try {
    data = await getJson(
      `https://api.geoapify.com/v1/routing?${params}`,
      signal,
    );
  } catch (error) {
    if (error.name === "AbortError") throw error;
    console.error("Error calculando ruta con Geoapify:", error);
    throw new Error(routeErrorMessage(error), { cause: error });
  }
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
