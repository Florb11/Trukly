import { useEffect, useState } from "react";
import { FaPlus, FaTools } from "react-icons/fa";
import { apiFetch } from "../utils/api";

export default function FallasPage() {
  const [reportes, setReportes] = useState([]);
  const [modal, setModal] = useState(false);
  const [form, setForm] = useState({ camion: "", descripcion: "" });
  const [feedback, setFeedback] = useState(null);
  const [guardando, setGuardando] = useState(false);

  const cargar = async () => {
    const result = await apiFetch("/api/choferes/mis-reportes");
    if (result?.response.ok) setReportes(Array.isArray(result.data) ? result.data : []);
  };
  useEffect(() => { const id = requestAnimationFrame(cargar); return () => cancelAnimationFrame(id); }, []);

  const crear = async (event) => {
    event.preventDefault();
    setGuardando(true);
    const result = await apiFetch("/api/reportes", { method: "POST", body: JSON.stringify({ Camion_id_camion: Number(form.camion), descripcion: form.descripcion.trim() }) });
    if (result?.response.ok) {
      setFeedback({ type: "ok", text: "Reporte creado correctamente." });
      setModal(false);
      setForm({ camion: "", descripcion: "" });
      await cargar();
    } else setFeedback({ type: "error", text: result?.data.mensaje || "No se pudo crear el reporte." });
    setGuardando(false);
  };

  return (
    <section className="page-stack">
      <header className="page-heading with-action"><div><span>MANTENIMIENTO</span><h1>Reportar falla</h1><p>Registrá problemas de una unidad.</p></div><button className="icon-button" onClick={() => setModal(true)} aria-label="Nuevo reporte"><FaPlus /></button></header>
      {feedback && <p className={`feedback ${feedback.type}`}>{feedback.text}</p>}
      {reportes.length === 0 ? <p className="empty">No tenés reportes registrados.</p> : <div className="failure-list">{reportes.map((reporte) => <article key={reporte.id_reporte}><div><FaTools /><span>Reporte #{reporte.id_reporte}</span><b className={`status ${reporte.estado}`}>{reporte.estado}</b></div><h2>{reporte.descripcion}</h2><p>Camión #{reporte.Camion_id_camion}</p><small>{reporte.fecha_hora}</small></article>)}</div>}
      {modal && <div className="modal-backdrop" onMouseDown={() => setModal(false)}><form className="modal-sheet" onSubmit={crear} onMouseDown={(event) => event.stopPropagation()}><span>NUEVA FALLA</span><h2>Crear reporte</h2><label>ID del camión<input type="number" min="1" value={form.camion} onChange={(event) => setForm({ ...form, camion: event.target.value })} required /></label><label>Descripción<textarea maxLength="200" value={form.descripcion} onChange={(event) => setForm({ ...form, descripcion: event.target.value })} required /></label><div><button type="button" className="button secondary" onClick={() => setModal(false)}>Cancelar</button><button className="button primary" disabled={guardando}>{guardando ? "Enviando..." : "Enviar"}</button></div></form></div>}
    </section>
  );
}
