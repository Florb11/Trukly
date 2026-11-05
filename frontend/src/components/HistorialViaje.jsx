import { useEffect, useState } from "react";
import { fetchConToken } from "../utils/fetchConToken";
import "./HistorialViaje.css";

const acciones = { viaje_creado: "Creó el viaje", viaje_editado: "Editó el viaje",
  viaje_aceptado: "Aceptó el viaje", viaje_iniciado: "Registró la salida por QR",
  viaje_finalizado: "Registró el regreso por QR",
  viaje_cancelado: "Canceló el viaje", carga_agregada: "Agregó una carga",
  carga_editada: "Editó una carga", carga_eliminada: "Quitó una carga" };
const campos = { origen: "Origen", destino: "Destino", fecha_salida: "Salida", fecha_llegada: "Llegada estimada",
  estado: "Estado", recorrido: "Recorrido", observaciones: "Observaciones",
  Chofer_Usuario_idUsuario: "Chofer", Camion_id_camion: "Camión" };

export default function HistorialViaje({ idViaje }) {
  const [cambios, setCambios] = useState(null);
  const [error, setError] = useState("");
  const [intento, setIntento] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    fetchConToken(`${import.meta.env.VITE_API_URL || "http://localhost:5000"}/api/operador/viajes/${idViaje}/historial`, {
      signal: AbortSignal.any([controller.signal, AbortSignal.timeout(20000)]),
    }).then((r) => {
      if (!r || controller.signal.aborted) return;
      if (!r.respuesta.ok) throw new Error("No se pudo cargar el historial.");
      setCambios(r.data);
    }).catch(() => { if (!controller.signal.aborted) setError("No se pudo cargar el historial."); });
    return () => controller.abort();
  }, [idViaje, intento]);
  return <section className="historial-viaje">
    <h3>Historial de cambios</h3>
    {error ? <p role="alert">{error} <button type="button" onClick={() => { setError(""); setIntento((n) => n + 1); }}>Reintentar</button></p>
      : cambios === null ? <p>Cargando historial...</p>
      : !cambios.length ? <p>No hay cambios registrados. Los cambios anteriores a esta función no están disponibles.</p>
      : <ol>{cambios.map((c) => <li key={c.id_cambio}>
          <strong>{c.actor_nombre}</strong><span>{acciones[c.accion] || c.accion}</span>
          <time dateTime={c.fecha_hora}>{new Date(c.fecha_hora).toLocaleString("es-AR")}</time>
          {c.datos.motivo && <p>Motivo: {c.datos.motivo}</p>}
          {c.accion === "viaje_editado" && <p>Campos actualizados: {Object.keys(c.datos.cambios).map((campo) => campos[campo]).filter(Boolean).join(", ") || "Sin modificaciones"}.</p>}
        </li>)}</ol>}
  </section>;
}
