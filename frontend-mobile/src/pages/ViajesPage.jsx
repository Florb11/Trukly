import { useCallback, useEffect, useRef, useState } from "react";
import { FaHistory, FaMapMarkerAlt, FaRoute, FaCheckCircle } from "react-icons/fa";
import { Link } from "react-router-dom";
import { apiFetch } from "../utils/api";

export default function ViajesPage() {
  const [viajes, setViajes] = useState([]);
  const [estado, setEstado] = useState("activos");
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [aceptando, setAceptando] = useState(null);
  const ocupado = useRef(false);

  const cargarViajes = useCallback(async (signal) => {
    try {
      const result = await apiFetch("/api/choferes/mis-viajes", { signal });
      if (signal?.aborted) return;
      if (!result?.response.ok) throw new Error(result?.data.mensaje || "No se pudieron cargar los viajes");
      setViajes(Array.isArray(result.data) ? result.data : []);
    } catch (err) {
      if (!signal?.aborted) setError(err.message);
    } finally {
      if (!signal?.aborted) setCargando(false);
    }
  }, []);
  useEffect(() => {
    const controller = new AbortController();
    const id = requestAnimationFrame(() => cargarViajes(controller.signal));
    return () => { cancelAnimationFrame(id); controller.abort(); };
  }, [cargarViajes]);

  const aceptar = async (idViaje) => {
    if (ocupado.current) return;
    ocupado.current = true;
    setAceptando(idViaje); setError(""); setMensaje("");
    try {
      const result = await apiFetch(`/api/choferes/viajes/${idViaje}/aceptar`, { method: "PUT", signal: AbortSignal.timeout(20000) });
      if (!result) return;
      if (!result.response.ok) throw new Error(result.data.mensaje || "No se pudo aceptar el viaje");
      setViajes((actuales) => actuales.map((viaje) => viaje.id_viaje === idViaje ? { ...viaje, ...result.data.viaje } : viaje));
      setMensaje("Viaje aceptado. Escaneá el QR de salida cuando comience el viaje; las horas todavía no empezaron a contar.");
    } catch (err) {
      setError(["AbortError", "TimeoutError", "TypeError"].includes(err.name) ? "No se pudo confirmar la aceptación. Volvé a abrir Mis viajes para comprobar su estado antes de reintentar." : err.message);
    } finally { ocupado.current = false; setAceptando(null); }
  };
  const visibles = viajes.filter((viaje) => estado === "todos" || (estado === "activos" ? ["pendiente", "aceptado", "en curso"].includes(viaje.estado?.toLowerCase()) : viaje.estado?.toLowerCase() === "finalizado"));
  return <section className="page-stack">
    <header className="page-heading with-action"><div><span>MIS ASIGNACIONES</span><h1>Viajes</h1><p>Aceptá tu asignación y registrá salida y regreso con QR.</p></div><Link className="icon-button" to="/historial" aria-label="Ver historial de movimientos"><FaHistory /></Link></header>
    <div className="segmented"><button className={estado === "activos" ? "active" : ""} onClick={() => setEstado("activos")}>Activos</button><button className={estado === "finalizados" ? "active" : ""} onClick={() => setEstado("finalizados")}>Finalizados</button><button className={estado === "todos" ? "active" : ""} onClick={() => setEstado("todos")}>Todos</button></div>
    {error && <p className="feedback error" role="alert">{error}</p>}{mensaje && <p className="feedback ok" role="status">{mensaje}</p>}
    {cargando ? <p className="empty">Cargando viajes...</p> : visibles.length === 0 ? <p className="empty">No hay viajes en esta categoría.</p> : <div className="trip-list">{visibles.map((viaje) => <article key={viaje.id_viaje}>
      <div className="trip-card-top"><span>Viaje #{viaje.id_viaje}</span><span className={`status ${viaje.estado?.replace(" ", "-")}`}>{viaje.estado}</span></div>
      <h2>{viaje.origen}</h2><div className="route-line"><i /><span /></div><h2>{viaje.destino}</h2>
      <div className="trip-meta"><span><FaMapMarkerAlt /> {viaje.recorrido || 0} km</span><span><FaRoute /> {viaje.fecha_salida}</span></div>
      {viaje.estado === "pendiente" && <button className="button primary wide" disabled={aceptando !== null} onClick={() => aceptar(viaje.id_viaje)}><FaCheckCircle /> {aceptando === viaje.id_viaje ? "Aceptando..." : "Aceptar viaje"}</button>}
      {["aceptado", "en curso"].includes(viaje.estado) && <Link className="button primary wide" to="/escanear">{viaje.estado === "aceptado" ? "Escanear QR de salida" : "Escanear QR de regreso"}</Link>}
    </article>)}</div>}
  </section>;
}
