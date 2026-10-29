import { useEffect, useRef, useState } from "react";
import { fetchConToken } from "../utils/fetchConToken";
import "./CargasViajeModal.css";

const VACIO = { descripcion: "", tipo: "", peso: "", bultos: "", remito: "" };
const kg = (valor) => `${Number(valor).toLocaleString("es-AR", { maximumFractionDigits: 3 })} kg`;

export default function CargasViajeModal({ viaje, onClose }) {
  const [datos, setDatos] = useState(null);
  const [form, setForm] = useState(VACIO);
  const [editando, setEditando] = useState(null);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [guardando, setGuardando] = useState(false);
  const ocupado = useRef(false);
  const titulo = useRef(null);
  const modal = useRef(null);
  const api = `${import.meta.env.VITE_API_URL || "http://localhost:5000"}/api/operador/viajes/${viaje.id_viaje}/cargas`;

  useEffect(() => {
    const controller = new AbortController();
    const anterior = document.activeElement;
    const overflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    titulo.current?.focus();
    const escapar = (event) => {
      if (event.key === "Escape" && !ocupado.current) onClose();
      if (event.key === "Tab") {
        const controles = [...(modal.current?.querySelectorAll('button:not([disabled]), input:not(:disabled), [href]') || [])];
        const primero = controles[0], ultimo = controles.at(-1);
        if (event.shiftKey && [primero, titulo.current].includes(document.activeElement)) { event.preventDefault(); ultimo?.focus(); }
        else if (!event.shiftKey && document.activeElement === ultimo) { event.preventDefault(); primero?.focus(); }
      }
    };
    document.addEventListener("keydown", escapar);
    fetchConToken(api, { signal: controller.signal }).then((resultado) => {
      if (!resultado || controller.signal.aborted) return;
      if (!resultado.respuesta.ok) throw new Error(resultado.data.mensaje || "No se pudieron cargar las cargas del viaje");
      setDatos(resultado.data);
    }).catch((err) => { if (!controller.signal.aborted) setError(err.message); });
    return () => { controller.abort(); document.removeEventListener("keydown", escapar); document.body.style.overflow = overflow; anterior?.focus(); };
  }, [api, onClose]);

  const limpiar = () => { setForm(VACIO); setEditando(null); };
  const enviar = async (metodo, id, body) => {
    if (ocupado.current) return;
    ocupado.current = true; setGuardando(true); setError(""); setMensaje("");
    try {
      const resultado = await fetchConToken(`${api}${id == null ? "" : `/${id}`}`, {
        method: metodo, ...(body ? { body: JSON.stringify(body) } : {}), signal: AbortSignal.timeout(20000),
      });
      if (!resultado) return;
      if (!resultado.respuesta.ok) throw new Error(resultado.data.mensaje || "No se pudo guardar la carga");
      setDatos(resultado.data); limpiar();
      setMensaje(metodo === "DELETE" ? "Carga eliminada. Total actualizado." : "Carga guardada. Total actualizado.");
    } catch (err) {
      setError(["AbortError", "TimeoutError", "TypeError"].includes(err.name) ? "No se pudo confirmar el cambio. Cerrá y volvé a abrir Cargas para revisar el estado antes de reintentar." : err.message);
    } finally { ocupado.current = false; setGuardando(false); }
  };
  const guardar = (event) => {
    event.preventDefault();
    enviar(editando == null ? "POST" : "PUT", editando, { ...form, bultos: form.bultos || null, remito: form.remito || null });
  };
  const pesoAnterior = datos?.cargas.find((carga) => carga.id_carga === editando)?.peso || 0;
  const totalPrevisto = datos ? datos.peso_total_kg - Number(pesoAnterior) + (Number(form.peso) || 0) : 0;
  const excede = datos && totalPrevisto > datos.capacidad_kg + 0.0000001;
  const cambiar = (event) => setForm((actual) => ({ ...actual, [event.target.name]: event.target.value }));
  return <div className="cargas-modal-backdrop"><section ref={modal} className="cargas-modal" role="dialog" aria-modal="true" aria-labelledby="cargas-titulo">
    <header><div><span>GESTIÓN DE CARGAS</span><h2 id="cargas-titulo" ref={titulo} tabIndex={-1}>Cargas del viaje #{viaje.id_viaje}</h2><p>{viaje.origen} → {viaje.destino}</p></div><button type="button" aria-label="Cerrar cargas" disabled={guardando} onClick={onClose}>×</button></header>
    <div className="cargas-modal__body">
      {error && <p className="cargas-modal__error" role="alert">{error}</p>}{mensaje && <p className="cargas-modal__ok" role="status">{mensaje}</p>}
      {!datos && !error && <p role="status">Cargando cargas...</p>}
      {datos && <>
        <p className="cargas-modal__camion">{datos.camion} · {datos.estado_viaje}</p>
        <dl className="cargas-modal__resumen"><div><dt>Capacidad del camión</dt><dd>{kg(datos.capacidad_kg)}</dd></div><div><dt>Carga asignada</dt><dd>{kg(datos.peso_total_kg)}</dd></div><div><dt>Disponible</dt><dd>{kg(datos.disponible_kg)}</dd></div></dl>
        {!datos.editable && <p className="cargas-modal__nota">Las cargas de este viaje son de solo lectura. Se pueden modificar antes de iniciar la salida.</p>}
        <h3>Cargas registradas <span>({datos.cargas.length})</span></h3>
        {!datos.cargas.length ? <p className="cargas-modal__nota">Todavía no hay cargas. Agregá cada mercadería con su peso total en kg.</p> : <div className="cargas-modal__lista">{datos.cargas.map((carga) => <article key={carga.id_carga}>
          <div><strong>{carga.descripcion}</strong><p>{carga.tipo} · {carga.bultos ? `${carga.bultos} bultos` : "Sin bultos informados"}{carga.remito ? ` · Remito: ${carga.remito}` : ""}</p></div><strong>{kg(carga.peso)}</strong>
          {datos.editable && <div className="cargas-modal__acciones"><button type="button" disabled={guardando} onClick={() => { setEditando(carga.id_carga); setForm({ descripcion: carga.descripcion, tipo: carga.tipo, peso: String(carga.peso), bultos: carga.bultos == null ? "" : String(carga.bultos), remito: carga.remito || "" }); setError(""); setMensaje(""); }}>Editar</button><button type="button" disabled={guardando} onClick={() => { if (window.confirm(`¿Quitar la carga «${carga.descripcion}»?`)) enviar("DELETE", carga.id_carga); }}>Quitar</button></div>}
        </article>)}</div>}
        {datos.editable && <form onSubmit={guardar}><h3>{editando == null ? "Agregar carga" : "Editar carga"}</h3><fieldset disabled={guardando}>
          <label>Descripción<input name="descripcion" value={form.descripcion} onChange={cambiar} maxLength={255} required placeholder="Ej.: Bolsas de cemento" /></label>
          <label>Tipo de carga<input name="tipo" value={form.tipo} onChange={cambiar} maxLength={45} required placeholder="Ej.: Material de construcción" /></label>
          <label>Peso total de esta carga (kg)<input name="peso" type="number" min="0.001" step="0.001" value={form.peso} onChange={cambiar} required placeholder="Ej.: 10000" /></label>
          <label>Cantidad de bultos (opcional)<input name="bultos" type="number" min="1" max="2147483647" step="1" value={form.bultos} onChange={cambiar} /></label>
          <label>Remito (opcional)<input name="remito" value={form.remito} onChange={cambiar} maxLength={80} placeholder="Ej.: REM-000123" /></label>
        </fieldset>
        <p className={excede ? "cargas-modal__error" : "cargas-modal__nota"} aria-live="polite">Con esta carga: {kg(totalPrevisto)} / {kg(datos.capacidad_kg)}{excede ? " · Supera la capacidad disponible" : ` · Quedan ${kg(datos.capacidad_kg - totalPrevisto)}`}</p>
        <div className="cargas-modal__pie-form">{editando != null && <button type="button" disabled={guardando} onClick={limpiar}>Cancelar edición</button>}<button type="submit" className="cargas-modal__principal" disabled={guardando || excede}>{guardando ? "Guardando..." : editando == null ? "Agregar carga" : "Guardar cambios"}</button></div>
        </form>}
      </>}
    </div><footer><button type="button" disabled={guardando} onClick={onClose}>Cerrar</button></footer>
  </section></div>;
}
