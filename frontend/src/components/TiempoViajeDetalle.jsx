import "./TiempoViajeDetalle.css";

const ESTADOS = {
  confirmado: { etiqueta: "Confirmado", nota: "Tiempo entre salida y regreso, incluidas paradas y descansos." },
  en_curso: { etiqueta: "En curso", nota: "Tiempo transcurrido al consultar. Las horas se confirman al registrar el regreso." },
  aceptado: { etiqueta: "Pendiente de salida", nota: "El viaje está aceptado. El conteo comenzará con el QR de salida." },
  incompleto: { etiqueta: "Registro incompleto", nota: "Falta uno de los controles. Este viaje no suma horas confirmadas." },
  inconsistente: { etiqueta: "Requiere revisión", nota: "Los controles tienen inconsistencias. Este viaje no suma horas confirmadas." },
  sin_registro: { etiqueta: "Sin controles", nota: "No hay controles de salida y regreso registrados para confirmar la duración." },
};

function ControlHorario({ etiqueta, valor }) {
  const [fecha, hora] = (valor || "").split("T");
  return <div><dt>{etiqueta}</dt><dd>{valor ? <><time dateTime={valor}>{fecha.split("-").reverse().join("/")}</time><small>{hora?.slice(0, 8)}</small></> : "Sin registro"}</dd></div>;
}

export default function TiempoViajeDetalle({ tiempo }) {
  const estado = tiempo?.estado || "sin_registro";
  const info = ESTADOS[estado] || { etiqueta: "Sin confirmar", nota: "No se pudo confirmar la duración del viaje." };
  const enCurso = estado === "en_curso";
  return <section className="tiempo-viaje" aria-label="Horas en viaje">
    <header className="tiempo-viaje__cabecera"><h3>Horas en viaje</h3><span className={`tiempo-viaje__estado tiempo-viaje__estado--${estado}`}>{info.etiqueta}</span></header>
    <div className="tiempo-viaje__duracion"><span>{enCurso ? "Tiempo transcurrido" : "Duración confirmada"}</span><strong>{enCurso ? tiempo?.transcurrido || "Sin registro" : tiempo?.duracion || "Sin duración confirmada"}</strong></div>
    <dl className="tiempo-viaje__controles"><ControlHorario etiqueta="Inicio del viaje" valor={tiempo?.inicio} /><ControlHorario etiqueta="Regreso del viaje" valor={tiempo?.regreso} /></dl>
    <p className="tiempo-viaje__nota">{info.nota}</p>
  </section>;
}
