import { FaClock, FaChevronDown } from "react-icons/fa";
import "./HorasViajeResumen.css";

const fecha = (valor) => {
  if (!valor) return "Sin registro";
  const [dia, hora] = valor.split("T");
  return `${dia.split("-").reverse().join("/")} · ${hora?.slice(0, 8) || ""}`;
};

export default function HorasViajeResumen({ horas, compacto = false }) {
  if (!horas) return <article className="horas-resumen"><h2>Horas en viaje</h2><p>La información de horas todavía no está disponible.</p></article>;
  return <article className="horas-resumen">
    <header className="horas-resumen__heading"><div><h2>Horas en viaje</h2><p>Período: {horas.mes}</p></div><FaClock aria-hidden="true" /></header>
    <dl className="horas-resumen__metricas">
      <div><dt>Horas confirmadas</dt><dd>{horas.duracion}</dd></div>
      <div><dt>Viajes confirmados</dt><dd>{horas.viajes_confirmados}</dd></div>
      <div><dt>Promedio por viaje</dt><dd>{horas.promedio || "Sin datos"}</dd></div>
      <div><dt>Viajes en curso</dt><dd>{horas.viajes_en_curso}</dd></div>
    </dl>
    <p className="horas-resumen__nota">Tiempo entre salida y regreso, incluidas paradas y descansos. Se suma a cada mes la parte del viaje que le corresponde.</p>
    {(horas.viajes_sin_registro > 0 || horas.viajes_incompletos > 0 || horas.viajes_inconsistentes > 0) &&
      <p className="horas-resumen__aviso">Sin registro: {horas.viajes_sin_registro} · Incompletos: {horas.viajes_incompletos} · A revisar: {horas.viajes_inconsistentes}. No suman horas confirmadas.</p>}
    {horas.segundos_superpuestos > 0 && <p className="horas-resumen__aviso">Hay horarios superpuestos: ese tiempo se contó una sola vez.</p>}
    {!compacto && <details className="horas-resumen__detalle"><summary>Ver viajes y controles del mes <FaChevronDown aria-hidden="true" /></summary>
      <div className="horas-resumen__historial">{(horas.historial || []).map((viaje) =>
        <section key={viaje.id_viaje} className="horas-resumen__viaje">
          <h3>Viaje #{viaje.id_viaje}</h3><p className="horas-resumen__ruta">{viaje.origen} → {viaje.destino}</p>
          <dl className="horas-resumen__controles"><div><dt>Inicio</dt><dd>{fecha(viaje.inicio)}</dd></div><div><dt>Regreso</dt><dd>{fecha(viaje.regreso)}</dd></div></dl>
          <p className="horas-resumen__duracion">{viaje.estado === "confirmado" ? `${viaje.duracion_mes} en este mes · ${viaje.duracion} en total` : viaje.estado === "en_curso" ? `En curso: ${viaje.transcurrido} al consultar` : viaje.estado === "aceptado" ? "Aceptado · Pendiente de QR de salida; todavía no suma horas" : viaje.estado === "sin_registro" ? "Sin registro horario" : "Registro incompleto o inconsistente: revisar controles"}</p>
        </section>)}{!horas.historial?.length && <p>No hay viajes para este período.</p>}</div>
    </details>}
  </article>;
}
