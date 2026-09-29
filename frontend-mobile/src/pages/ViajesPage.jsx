import { useEffect, useState } from "react";
import { FaMapMarkerAlt, FaRoute } from "react-icons/fa";
import { apiFetch } from "../utils/api";

export default function ViajesPage() {
  const [viajes, setViajes] = useState([]);
  const [estado, setEstado] = useState("activos");
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const id = requestAnimationFrame(async () => {
      const result = await apiFetch("/api/choferes/mis-viajes");
      if (result?.response.ok) setViajes(Array.isArray(result.data) ? result.data : []);
      else setError(result?.data.mensaje || "No se pudieron cargar los viajes");
      setCargando(false);
    });
    return () => cancelAnimationFrame(id);
  }, []);

  const visibles = viajes.filter((viaje) => estado === "todos" || (estado === "activos" ? ["pendiente", "en curso"].includes(viaje.estado?.toLowerCase()) : viaje.estado?.toLowerCase() === "finalizado"));
  return (
    <section className="page-stack">
      <header className="page-heading"><span>MIS ASIGNACIONES</span><h1>Viajes</h1><p>Consultá recorridos y estados.</p></header>
      <div className="segmented"><button className={estado === "activos" ? "active" : ""} onClick={() => setEstado("activos")}>Activos</button><button className={estado === "finalizados" ? "active" : ""} onClick={() => setEstado("finalizados")}>Finalizados</button><button className={estado === "todos" ? "active" : ""} onClick={() => setEstado("todos")}>Todos</button></div>
      {error && <p className="feedback error">{error}</p>}
      {cargando ? <p className="empty">Cargando viajes...</p> : visibles.length === 0 ? <p className="empty">No hay viajes en esta categoría.</p> : <div className="trip-list">{visibles.map((viaje) => <article key={viaje.id_viaje}><div className="trip-card-top"><span>Viaje #{viaje.id_viaje}</span><span className={`status ${viaje.estado?.replace(" ", "-")}`}>{viaje.estado}</span></div><h2>{viaje.origen}</h2><div className="route-line"><i /><span /></div><h2>{viaje.destino}</h2><div className="trip-meta"><span><FaMapMarkerAlt /> {viaje.recorrido || 0} km</span><span><FaRoute /> {viaje.fecha_salida}</span></div></article>)}</div>}
    </section>
  );
}
