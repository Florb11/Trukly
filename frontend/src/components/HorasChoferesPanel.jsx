import { useState } from "react";
import { FaClock, FaSearch, FaUser, FaChevronDown } from "react-icons/fa";

const fechaControl = (valor) => {
  if (!valor) return "Sin registro";
  const [fecha, hora] = valor.split("T");
  const [anio, mes, dia] = fecha.split("-");
  return `${dia}/${mes}/${anio} · ${hora?.slice(0, 8) || ""}`;
};

const duracionExacta = (segundos) => {
  if (segundos == null) return "Sin confirmar";
  return `${Math.floor(segundos / 3600)} h ${String(Math.floor(segundos % 3600 / 60)).padStart(2, "0")} min ${String(Math.floor(segundos % 60)).padStart(2, "0")} s`;
};

export default function HorasChoferesPanel({ choferes, nombreMes }) {
  const [busqueda, setBusqueda] = useState("");
  const [soloActividad, setSoloActividad] = useState(true);
  const filas = choferes || [];
  const conActividad = (chofer) => chofer.viajes_confirmados + chofer.viajes_en_curso + chofer.viajes_incompletos + chofer.viajes_inconsistentes + chofer.viajes_sin_registro > 0;
  const visibles = filas.filter((chofer) => `${chofer.nombre} ${chofer.apellido}`.toLocaleLowerCase().includes(busqueda.trim().toLocaleLowerCase()) && (!soloActividad || conActividad(chofer)));
  return <div className="estadisticas-horas">
    <div className="estadisticas-seccion__heading"><div><h2>Horas en viaje por chofer</h2><p>Controles de salida y regreso de {nombreMes}.</p></div><span className="estadisticas-horas__conteo">{filas.filter(conActividad).length} choferes con actividad</span></div>
    <div className="estadisticas-horas__herramientas">
      <label className="estadisticas-horas__buscar"><FaSearch aria-hidden="true" /><input aria-label="Buscar chofer por nombre" placeholder="Buscar chofer por nombre..." value={busqueda} onChange={(event) => setBusqueda(event.target.value)} /></label>
      <label className="estadisticas-horas__filtro"><input type="checkbox" checked={soloActividad} onChange={(event) => setSoloActividad(event.target.checked)} />Solo con actividad</label>
    </div>
    <p className="estadisticas-horas__nota"><FaClock aria-hidden="true" /> Se cuenta el tiempo entre controles, incluidas paradas y descansos. Cada mes incluye su parte del viaje.</p>
    {!choferes ? <p className="estadisticas-feedback">Información pendiente de actualizar en el servidor.</p> : !visibles.length ? <p className="estadisticas-feedback">{filas.length ? "No hay choferes que coincidan con los filtros." : "No hay choferes registrados."}</p> :
      <div className="estadisticas-horas__lista">{visibles.map((chofer) => {
        const incidencias = chofer.viajes_sin_registro + chofer.viajes_incompletos + chofer.viajes_inconsistentes;
        return <article className="estadisticas-chofer" key={chofer.id_usuario}>
          <div className="estadisticas-chofer__cabecera"><div className="estadisticas-chofer__identidad"><span className="estadisticas-chofer__avatar"><FaUser aria-hidden="true" /></span><div><h3>{chofer.nombre} {chofer.apellido}</h3><p>{conActividad(chofer) ? `${chofer.viajes_confirmados} viajes confirmados` : "Sin actividad en este mes"}</p></div></div>
            {chofer.viajes_en_curso > 0 && <span className="estadisticas-badge estadisticas-badge--curso">{chofer.viajes_en_curso} en curso</span>}
          </div>
          <dl className="estadisticas-chofer__metricas"><div><dt>Horas confirmadas</dt><dd>{chofer.duracion}</dd></div><div><dt>Promedio por viaje</dt><dd>{chofer.promedio || "Sin datos"}</dd></div></dl>
          {incidencias > 0 && <p className="estadisticas-chofer__aviso">Sin registro: {chofer.viajes_sin_registro} · Incompletos: {chofer.viajes_incompletos} · A revisar: {chofer.viajes_inconsistentes}. No suman al total.</p>}
          {chofer.segundos_superpuestos > 0 && <p className="estadisticas-chofer__aviso">Hay horarios superpuestos; ese tiempo se cuenta una sola vez.</p>}
          {conActividad(chofer) && <details className="estadisticas-horas-detalle">
            <summary>Ver viajes y controles <FaChevronDown aria-hidden="true" /></summary>
            <div className="estadisticas-horas-detalle__contenido"><p>Las horas del mes se suman con segundos; el resumen se muestra en horas y minutos.</p>
              {(chofer.historial || []).map((viaje) => <div key={viaje.id_viaje} className="estadisticas-horas-detalle__viaje">
                <div className="estadisticas-horas-detalle__ruta"><strong>Viaje #{viaje.id_viaje}</strong><span>{viaje.origen} → {viaje.destino}</span></div>
                <dl className="estadisticas-horas-detalle__controles"><div><dt>Inicio</dt><dd>{fechaControl(viaje.inicio)}</dd></div><div><dt>Regreso</dt><dd>{fechaControl(viaje.regreso)}</dd></div></dl>
                <p className="estadisticas-horas-detalle__duracion">{viaje.estado === "confirmado" ? `${viaje.duracion_mes} en el mes · Duración total: ${duracionExacta(viaje.segundos_confirmados)}` : viaje.estado === "en_curso" ? `En curso: ${viaje.transcurrido} al consultar · No suma al total` : `${viaje.estado.replaceAll("_", " ")} · No suma al total`}</p>
              </div>)}
              {!chofer.historial?.length && <p>No hay controles disponibles para este período.</p>}
            </div>
          </details>}
        </article>;
      })}</div>}
  </div>;
}
