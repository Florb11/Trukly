import { useCallback, useEffect, useState } from "react";
import { FaCheck, FaSyncAlt, FaTools } from "react-icons/fa";
import { apiFetch } from "../utils/api";

export default function MecanicoPage() {
  const [reportes, setReportes] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [filtro, setFiltro] = useState("activos");
  const [seleccionado, setSeleccionado] = useState(null);
  const [nota, setNota] = useState("");
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");
  const cargar = useCallback(async () => {
    try {
      const resultado = await apiFetch("/api/mecanico/reportes", { signal: AbortSignal.timeout(20000) });
      if (!resultado) return;
      if (!resultado.response.ok) throw new Error(resultado.data.mensaje || "No se pudieron cargar los reportes.");
      setReportes(resultado.data.reportes || []);
      setError("");
    } catch {
      setError("No se pudieron cargar los reportes. Revisá tu conexión y volvé a intentar.");
    } finally { setCargando(false); }
  }, []);
  useEffect(() => {
    const id = setTimeout(cargar, 0);
    return () => clearTimeout(id);
  }, [cargar]);
  const resolver = async (event) => {
    event.preventDefault();
    if (guardando || !seleccionado) return;
    if (!nota.trim()) { setError("Escribí la reparación realizada."); return; }
    setGuardando(true);
    setError("");
    try {
      const resultado = await apiFetch(`/api/mecanico/reportes/${seleccionado.id_reporte}/resolver`, {
        method: "PUT", signal: AbortSignal.timeout(20000),
        body: JSON.stringify({ nota_reparacion: nota.trim() }),
      });
      if (!resultado) return;
      if (!resultado.response.ok) throw new Error(resultado.data.mensaje || "No se pudo resolver el reporte.");
      setReportes((actuales) => actuales.map((reporte) => reporte.id_reporte === seleccionado.id_reporte ? resultado.data.reporte : reporte));
      setSeleccionado(null);
      setMensaje(resultado.data.mensaje || "Reparación finalizada.");
    } catch (err) {
      setError(["TypeError", "TimeoutError", "AbortError"].includes(err.name)
        ? "No se pudo confirmar la reparación. Actualizá los reportes antes de reintentar." : err.message);
    } finally { setGuardando(false); }
  };
  const visibles = reportes.filter((reporte) => filtro === "todos" || (filtro === "activos" ? reporte.estado !== "resuelto" : reporte.estado === "resuelto"));
  return <section className="page-stack">
    <header className="page-heading with-action"><div><span>TALLER</span><h1>Reportes asignados</h1></div><button className="icon-button" onClick={cargar} title="Actualizar reportes" aria-label="Actualizar reportes"><FaSyncAlt /></button></header>
    <div className="segmented">{[["activos", "Activos"], ["resueltos", "Resueltos"], ["todos", "Todos"]].map(([valor, texto]) => <button key={valor} className={filtro === valor ? "active" : ""} onClick={() => setFiltro(valor)}>{texto}</button>)}</div>
    {error && !seleccionado && <p className="feedback error" role="alert">{error}</p>}
    {mensaje && <p className="feedback ok">{mensaje}</p>}
    {cargando ? <p className="empty">Cargando reportes...</p> : !visibles.length ? <p className="empty">No hay reportes en esta categoría.</p> : <div className="failure-list">{visibles.map((reporte) => <article key={reporte.id_reporte}>
      <div><FaTools /><span>Reporte #{reporte.id_reporte}</span><b className="status">{reporte.estado}</b></div>
      <h2>{reporte.descripcion}</h2><p>Camión #{reporte.Camion_id_camion}</p><small>{reporte.fecha_hora}</small>
      {reporte.nota_reparacion && <p className="repair-note">Reparación: {reporte.nota_reparacion}</p>}
      {reporte.estado !== "resuelto" && <button className="button secondary wide" onClick={() => { setSeleccionado(reporte); setNota(""); setError(""); setMensaje(""); }}><FaCheck /> Finalizar reparación</button>}
    </article>)}</div>}
    {seleccionado && <div className="modal-backdrop"><form className="modal-sheet" role="dialog" aria-modal="true" aria-labelledby="repair-title" onSubmit={resolver}>
      <span>REPORTE #{seleccionado.id_reporte}</span><h2 id="repair-title">Finalizar reparación</h2><p>{seleccionado.descripcion}</p>
      {error && <p className="feedback error" role="alert">{error}</p>}
      <label>Reparación realizada<textarea required maxLength="200" value={nota} onChange={(event) => setNota(event.target.value)} /></label>
      <div><button className="button secondary" type="button" disabled={guardando} onClick={() => setSeleccionado(null)}>Cancelar</button><button className="button primary" disabled={guardando}>{guardando ? "Guardando..." : "Confirmar"}</button></div>
    </form></div>}
  </section>;
}
