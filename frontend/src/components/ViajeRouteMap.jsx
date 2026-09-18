import { useEffect } from "react";
import L from "leaflet";
import { CircleMarker, GeoJSON, MapContainer, TileLayer, useMap, useMapEvents } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { geoapifyTileUrl } from "../utils/geoapify";

function MapActions({ origin, destination, route, onPick }) {
  const map = useMap();
  useMapEvents({ click: (event) => onPick(event.latlng) });

  useEffect(() => {
    if (route) {
      map.fitBounds(L.geoJSON(route).getBounds(), { padding: [28, 28] });
    } else if (origin && destination) {
      map.fitBounds([[origin.lat, origin.lon], [destination.lat, destination.lon]], { padding: [28, 28] });
    } else if (origin || destination) {
      const point = origin || destination;
      map.setView([point.lat, point.lon], 13);
    }
  }, [map, origin, destination, route]);

  return null;
}

function ViajeRouteMap({ origin, destination, route, onPick }) {
  return (
    <MapContainer center={[-38.4, -63.6]} zoom={4} className="viaje-modal__map" scrollWheelZoom={false}>
      <TileLayer
        url={geoapifyTileUrl}
        attribution='Powered by <a href="https://www.geoapify.com/">Geoapify</a> | © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | © <a href="https://openmaptiles.org/">OpenMapTiles</a>'
      />
      {route && <GeoJSON key={`${origin?.lat}-${origin?.lon}-${destination?.lat}-${destination?.lon}`} data={route} style={{ color: "#1683bd", weight: 5 }} />}
      {origin && <CircleMarker center={[origin.lat, origin.lon]} radius={9} pathOptions={{ color: "#147d64", fillColor: "#1fa785", fillOpacity: 1 }} />}
      {destination && <CircleMarker center={[destination.lat, destination.lon]} radius={9} pathOptions={{ color: "#bc4b2b", fillColor: "#e26742", fillOpacity: 1 }} />}
      <MapActions origin={origin} destination={destination} route={route} onPick={onPick} />
    </MapContainer>
  );
}

export default ViajeRouteMap;
