export default function HorasViajeResumen({ horas, compacto = false }) {
  if (!horas) return <p>Horas en viaje: información pendiente de actualizar en el servidor.</p>;
  return <article className="admin-perfil-card ch-stats-section">
    <h2>Horas en viaje · {horas.mes}</h2>
    <p><strong>{horas.duracion}</strong> confirmadas · {horas.viajes_confirmados} viajes con ambos controles</p>
    <p>Promedio del período: {horas.promedio || "Sin datos"} · {horas.viajes_en_curso} en curso</p>
    <p>Tiempo entre salida y regreso; incluye paradas y descansos. Las horas se reparten entre los meses que abarca cada viaje.</p>
    {(horas.viajes_sin_registro > 0 || horas.viajes_incompletos > 0 || horas.viajes_inconsistentes > 0) &&
      <p>Sin registro: {horas.viajes_sin_registro} · Incompletos: {horas.viajes_incompletos} · A revisar: {horas.viajes_inconsistentes}. No suman horas confirmadas.</p>}
    {horas.segundos_superpuestos > 0 && <p>Hay viajes con horarios superpuestos: ese tiempo se contó una sola vez.</p>}
    {!compacto && <div className="ch-stats-history">{(horas.historial || []).map((viaje) =>
      <div key={viaje.id_viaje} className="ch-stats-history__item"><div className="ch-stats-history__content">
        <strong>#{viaje.id_viaje} · {viaje.origen} → {viaje.destino}</strong>
        <span>Inicio: {viaje.inicio?.replace("T", " ") || "Sin registro"} · Regreso: {viaje.regreso?.replace("T", " ") || "Sin registro"}</span>
        <small>{viaje.estado === "confirmado" ? `${viaje.duracion_mes} en este mes (${viaje.duracion} en total)` : viaje.estado === "en_curso" ? `En curso: ${viaje.transcurrido} al consultar` : viaje.estado === "sin_registro" ? "Sin registro horario" : "Registro incompleto o inconsistente: revisar controles"}</small>
      </div></div>)}{!horas.historial?.length && <p>No hay viajes para este período.</p>}</div>}
  </article>;
}
