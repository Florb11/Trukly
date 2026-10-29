import { useEffect, useState } from "react";
import { fetchConToken } from "../utils/fetchConToken";
import "./CambiarEstadoReporteModal.css";

export default function CambiarEstadoReporteModal({ reporte, nuevoEstado, errorEstado, onChange, onSubmit, onClose, idMecanico, onMecanicoChange, motivo, onMotivoChange, guardando }) {
  const [resultado, setResultado] = useState(null);
  const [intento, setIntento] = useState(0);
  useEffect(() => {
    const controlador = new AbortController();
    fetchConToken(`${import.meta.env.VITE_API_URL || "http://localhost:5000"}/api/reportes/mecanicos-activos`, { signal: controlador.signal }).then((r) => {
      if (!r || controlador.signal.aborted) return;
      if (!r.respuesta.ok) throw new Error(r.data.mensaje || "No se pudieron cargar los mecánicos");
      setResultado({ intento, lista: r.data.mecanicos || [] });
    }).catch((error) => { if (!controlador.signal.aborted) setResultado({ intento, error: error.message }); });
    return () => controlador.abort();
  }, [intento]);
  if (!reporte) return null;
  const lista = resultado?.intento === intento ? resultado.lista || [] : [];
  const cargando = resultado?.intento !== intento;
  const mecanicoValido = lista.some((m) => String(m.id_usuario) === String(idMecanico));
  return <div className="cambiar-estado-reporte-backdrop"><div className="cambiar-estado-reporte-modal" role="dialog" aria-modal="true" aria-labelledby="estado-reporte-titulo">
    <div className="cambiar-estado-reporte-header"><div><span>Cambiar estado</span><h2 id="estado-reporte-titulo">Reporte #{reporte.id_reporte}</h2><p>Estado actual: {reporte.estado}</p></div><button type="button" className="cambiar-estado-reporte-close" onClick={onClose} disabled={guardando} aria-label="Cerrar">×</button></div>
    <form className="cambiar-estado-reporte-form" onSubmit={onSubmit}>
      {errorEstado && <p role="alert" className="cambiar-estado-reporte-error">{errorEstado}</p>}
      <div className="cambiar-estado-reporte-field"><label htmlFor="nuevoEstadoReporte">Nuevo estado</label><select id="nuevoEstadoReporte" value={nuevoEstado} onChange={onChange} disabled={guardando}>
        {reporte.estado === "resuelto" && <option value="resuelto" disabled>Resuelto (estado actual)</option>}
        {!reporte.Mecanico_Usuario_idUsuario && <option value="pendiente">Pendiente</option>}
        <option value="en revision">En revisión</option><option value="cancelado">Cancelado</option>
      </select></div>
      {nuevoEstado === "en revision" && <div className="cambiar-estado-reporte-field">
        {reporte.mecanico_nombre && <p>Mecánico actual: <strong>{reporte.mecanico_nombre}</strong></p>}
        <label htmlFor="estado-reporte-mecanico">Mecánico responsable</label>
        <select id="estado-reporte-mecanico" value={idMecanico} onChange={(e) => onMecanicoChange(e.target.value)} required disabled={guardando || cargando || !lista.length}>
          <option value="">{cargando ? "Cargando mecánicos..." : "Seleccioná un mecánico activo"}</option>
          {idMecanico && !mecanicoValido && <option value={idMecanico} disabled>Mecánico anterior no disponible</option>}
          {lista.map((m) => <option key={m.id_usuario} value={m.id_usuario}>{m.nombre} {m.apellido}{m.especialidad ? ` · ${m.especialidad}` : ""}</option>)}
        </select>
        {!cargando && !resultado?.error && !lista.length && <p>No hay mecánicos activos para asignar.</p>}
        {resultado?.error && <div><p role="alert">{resultado.error}</p><button type="button" onClick={() => setIntento((v) => v + 1)} disabled={guardando}>Reintentar</button></div>}
        <p className="cambiar-estado-reporte-ayuda">El reporte necesita un mecánico activo. Si asignás uno nuevo, recibirá una notificación.</p>
      </div>}
      {nuevoEstado === "cancelado" && <div className="cambiar-estado-reporte-field"><label htmlFor="motivo-cancelar-reporte">Motivo de cancelación</label><textarea id="motivo-cancelar-reporte" value={motivo} onChange={(e) => onMotivoChange(e.target.value)} required maxLength={255} rows={3} disabled={guardando} placeholder="Explicá por qué se cancela el reporte" /><p className="cambiar-estado-reporte-ayuda">El motivo quedará guardado. Antes de cancelar te pediremos confirmación.</p></div>}
      <div className="cambiar-estado-reporte-footer"><button type="button" className="cambiar-estado-reporte-btn cambiar-estado-reporte-btn--cancelar" onClick={onClose} disabled={guardando}>Volver</button><button type="submit" className="cambiar-estado-reporte-btn cambiar-estado-reporte-btn--guardar" disabled={guardando || nuevoEstado === "resuelto" || (nuevoEstado === "en revision" && !mecanicoValido)}>{guardando ? "Guardando..." : nuevoEstado === "cancelado" ? "Continuar" : "Guardar estado"}</button></div>
    </form>
  </div></div>;
}
