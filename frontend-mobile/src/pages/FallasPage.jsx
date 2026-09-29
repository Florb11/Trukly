import { useEffect, useState } from "react";
import { FaPlus, FaRoute, FaTools, FaTruck } from "react-icons/fa";
import { apiFetch } from "../utils/api";

export default function FallasPage() {
  const [reportes, setReportes] = useState([]);
  const [viajeActivo, setViajeActivo] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [modal, setModal] = useState(false);
  const [descripcion, setDescripcion] = useState("");
  const [feedback, setFeedback] = useState(null);
  const [guardando, setGuardando] = useState(false);

  const cargar = async () => {
    const [resultadoReportes, resultadoViajes] = await Promise.all([
      apiFetch("/api/choferes/mis-reportes"),
      apiFetch("/api/choferes/mis-viajes"),
    ]);
    if (resultadoReportes?.response.ok) {
      setReportes(Array.isArray(resultadoReportes.data) ? resultadoReportes.data : []);
    }
    if (resultadoViajes?.response.ok) {
      const viajes = Array.isArray(resultadoViajes.data) ? resultadoViajes.data : [];
      setViajeActivo(viajes.find((viaje) => viaje.estado?.toLowerCase() === "en curso") || null);
    }
    setCargando(false);
  };
  useEffect(() => { const id = requestAnimationFrame(cargar); return () => cancelAnimationFrame(id); }, []);

  const crear = async (event) => {
    event.preventDefault();
    if (!viajeActivo) return;
    setGuardando(true);
    const result = await apiFetch("/api/reportes", {
      method: "POST",
      body: JSON.stringify({
        Camion_id_camion: viajeActivo.Camion_id_camion,
        descripcion: descripcion.trim(),
      }),
    });
    if (result?.response.ok) {
      setFeedback({ type: "ok", text: "Reporte creado correctamente." });
      setModal(false);
      setDescripcion("");
      await cargar();
    } else setFeedback({ type: "error", text: result?.data.mensaje || "No se pudo crear el reporte." });
    setGuardando(false);
  };

  return (
    <section className="page-stack">
      <header className="page-heading with-action"><div><span>MANTENIMIENTO</span><h1>Reportar falla</h1><p>Registrá problemas de tu unidad asignada.</p></div><button className="icon-button" onClick={() => setModal(true)} disabled={!viajeActivo || cargando} aria-label="Nuevo reporte"><FaPlus /></button></header>
      {feedback && <p className={`feedback ${feedback.type}`}>{feedback.text}</p>}
      {cargando ? <p className="empty compact">Buscando tu viaje actual...</p> : viajeActivo ? (
        <article className="assigned-truck">
          <div><FaTruck /><span>UNIDAD EN VIAJE</span></div>
          <h2>{viajeActivo.camion?.marca || "Camión"} {viajeActivo.camion?.modelo || `#${viajeActivo.Camion_id_camion}`}</h2>
          <p>{viajeActivo.camion?.matricula || `Unidad #${viajeActivo.Camion_id_camion}`}</p>
          <small><FaRoute /> Viaje #{viajeActivo.id_viaje}: {viajeActivo.origen} → {viajeActivo.destino}</small>
        </article>
      ) : <p className="feedback info">Necesitás tener un viaje en curso para reportar una falla.</p>}
      {reportes.length === 0 ? <p className="empty">No tenés reportes registrados.</p> : <div className="failure-list">{reportes.map((reporte) => <article key={reporte.id_reporte}><div><FaTools /><span>Reporte #{reporte.id_reporte}</span><b className={`status ${reporte.estado}`}>{reporte.estado}</b></div><h2>{reporte.descripcion}</h2><p>Camión #{reporte.Camion_id_camion}</p><small>{reporte.fecha_hora}</small></article>)}</div>}
      {modal && viajeActivo && <div className="modal-backdrop" onMouseDown={() => setModal(false)}><form className="modal-sheet" onSubmit={crear} onMouseDown={(event) => event.stopPropagation()}><span>NUEVA FALLA</span><h2>Crear reporte</h2><div className="modal-unit"><FaTruck /><div><small>Unidad asignada</small><strong>{viajeActivo.camion?.marca || "Camión"} {viajeActivo.camion?.modelo || `#${viajeActivo.Camion_id_camion}`}</strong><span>{viajeActivo.camion?.matricula || `Viaje #${viajeActivo.id_viaje}`}</span></div></div><label>Descripción<textarea maxLength="200" value={descripcion} onChange={(event) => setDescripcion(event.target.value)} placeholder="Contanos qué problema detectaste" required /></label><div><button type="button" className="button secondary" onClick={() => setModal(false)}>Cancelar</button><button className="button primary" disabled={guardando}>{guardando ? "Enviando..." : "Enviar"}</button></div></form></div>}
    </section>
  );
}
