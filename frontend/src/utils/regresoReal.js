export function regresoReal(viaje) {
  const valor = viaje.fecha_regreso_real || (viaje.tiempo_viaje?.estado === "confirmado" ? viaje.tiempo_viaje.regreso : null);
  if (!valor) return "Sin registro";
  // Los controles históricos y actuales usan el reloj guardado, sin zona.
  const partes = valor.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}:\d{2}:\d{2})/);
  return partes ? `${partes[3]}/${partes[2]}/${partes[1]} ${partes[4]}` : "Sin registro";
}
