import { useCallback, useEffect, useState } from "react";
import { FaTools, FaSyncAlt } from "react-icons/fa";
import { apiFetch } from "../utils/api";

export default function OperadorPage() {
  const [reportes, setReportes] = useState([]);
  const [mecanicos, setMecanicos] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [errorMecanicos, setErrorMecanicos] = useState("");
  const [filtro, setFiltro] = useState("activos");
  const [reporte, setReporte] = useState(null);
  const [accion, setAccion] = useState("estado");
  const [estado, setEstado] = useState("");
  const [mecanico, setMecanico] = useState("");
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");
  const cargar = useCallback(async () => {
    try {
      const resultado = await apiFetch("/api/reportes", { signal: AbortSignal.timeout(20000) });
      if (!resultado) return;
      if (!resultado.response.ok) throw new Error(resultado.data.mensaje || "No se pudieron cargar los reportes.");
      setReportes(resultado.data.reportes || []);
      setError("");
    } catch { setError("No se pudieron cargar los reportes. Revisá tu conexión y volvé a intentar."); }
    finally { setCargando(false); }
  }, []);
  useEffect(() => {
    const id = setTimeout(cargar, 0);
    return () => clearTimeout(id);
  }, [cargar]);
  const abrir = async (item) => {
    setReporte(item);
    setEstado(item.estado);
    setMecanico("");
    setAccion("estado");
    setError("");
    setMensaje("");
    setMecanicos([]);
    setErrorMecanicos("");
    try {
      const resultado = await apiFetch("/api/operador/mecanicos", { signal: AbortSignal.timeout(20000) });
      if (!resultado) return;
      if (!resultado.response.ok) throw new Error();
      setMecanicos(Array.isArray(resultado.data) ? resultado.data : []);
    } catch { setErrorMecanicos("No se pudieron cargar los mecánicos. Cerrá y volvé a abrir el reporte para reintentar."); }
  };
  const guardar = async (event) => {
    event.preventDefault();
    if (guardando || !reporte) return;
    setGuardando(true);
    setError("");
    try {
      const resultado = await apiFetch(`/api/reportes/${reporte.id_reporte}/${accion === "estado" ? "estado" : "asignar-mecanico"}`, {
        method: "PUT", signal: AbortSignal.timeout(20000),
        body: JSON.stringify(accion === "estado" ? { estado } : { Mecanico_Usuario_idUsuario: Number(mecanico) }),
      });
      if (!resultado) return;
      if (!resultado.response.ok) throw new Error(resultado.data.mensaje || "No se pudo actualizar el reporte.");
      setReportes((actuales) => actuales.map((item) => item.id_reporte === reporte.id_reporte ? resultado.data.reporte : item));
      setReporte(null);
      setMensaje(resultado.data.mensaje || "Reporte actualizado.");
    } catch (err) {
      setError(["TypeError", "TimeoutError", "AbortError"].includes(err.name)
        ? "No se pudo confirmar el cambio. Actualizá los reportes antes de reintentar." : err.message);
    } finally { setGuardando(false); }
  };
  const activos = (item) => ["pendiente", "en revision"].includes(item.estado);
  const visibles = reportes.filter((item) => filtro === "todos" || (filtro === "activos" ? activos(item) : !activos(item)));
  return <section className="page-stack">
    <header className="page-heading with-action"><div><span>OPERACIÓN</span><h1>Reportes de falla</h1></div><button className="icon-button" onClick={cargar} title="Actualizar reportes" aria-label="Actualizar reportes"><FaSyncAlt /></button></header>
    <div className="segmented">{[["activos", "Activos"], ["cerrados", "Cerrados"], ["todos", "Todos"]].map(([valor, texto]) => <button key={valor} className={filtro === valor ? "active" : ""} onClick={() => setFiltro(valor)}>{texto}</button>)}</div>
    {error && !reporte && <p className="feedback error" role="alert">{error}</p>}
    {mensaje && <p className="feedback ok">{mensaje}</p>}
    {cargando ? <p className="empty">Cargando reportes...</p> : !visibles.length ? <p className="empty">No hay reportes en esta categoría.</p> : <div className="failure-list">{visibles.map((item) => <article key={item.id_reporte}>
      <div><FaTools /><span>Reporte #{item.id_reporte}</span><b className="status">{item.estado}</b></div><h2>{item.descripcion}</h2>
      <p>Camión #{item.Camion_id_camion}</p><p>{item.Mecanico_Usuario_idUsuario ? `Mecánico #${item.Mecanico_Usuario_idUsuario}` : "Sin mecánico asignado"}</p><small>{item.fecha_hora}</small>
      {item.nota_reparacion && <p>Reparación: {item.nota_reparacion}</p>}
      <button className="button secondary wide" onClick={() => abrir(item)}><FaTools /> Gestionar reporte</button>
    </article>)}</div>}
    {reporte && <div className="modal-backdrop"><form className="modal-sheet" role="dialog" aria-modal="true" aria-labelledby="manage-title" onSubmit={guardar}>
      <span>REPORTE #{reporte.id_reporte}</span><h2 id="manage-title">Gestionar reporte</h2><p>{reporte.descripcion}</p>
      <div className="segmented notification-filters"><button type="button" disabled={guardando} className={accion === "estado" ? "active" : ""} onClick={() => { setAccion("estado"); setError(""); }}>Estado</button><button type="button" disabled={guardando} className={accion === "mecanico" ? "active" : ""} onClick={() => { setAccion("mecanico"); setError(""); }}>Mecánico</button></div>
      {error && <p className="feedback error" role="alert">{error}</p>}
      {accion === "estado" ? <label>Nuevo estado<select required value={estado} onChange={(event) => setEstado(event.target.value)}>
        {!reporte.Mecanico_Usuario_idUsuario && <option value="pendiente">Pendiente</option>}<option value="en revision">En revisión</option><option value="cancelado">Cancelado</option>
        {!["pendiente", "en revision", "cancelado"].includes(reporte.estado) && <option value={reporte.estado} disabled>{reporte.estado}</option>}
      </select></label> : <><label>Mecánico<select required value={mecanico} onChange={(event) => setMecanico(event.target.value)}><option value="">Seleccionar</option>{mecanicos.map((item) => <option key={item.id_usuario} value={item.id_usuario}>{item.nombre} {item.apellido} ({item.especialidad})</option>)}</select></label>{errorMecanicos && <p className="feedback error" role="alert">{errorMecanicos}</p>}{!errorMecanicos && !mecanicos.length && <p className="feedback info">No hay mecánicos disponibles.</p>}</>}
      <div><button type="button" className="button secondary" disabled={guardando} onClick={() => setReporte(null)}>Cancelar</button><button className="button primary" disabled={guardando || (accion === "estado" ? estado === reporte.estado : !mecanico)}>{guardando ? "Guardando..." : "Confirmar"}</button></div>
    </form></div>}
  </section>;
}
