import { useState } from "react";
import { FaBell, FaCheck, FaSyncAlt } from "react-icons/fa";
import { useOutletContext } from "react-router-dom";
import { apiFetch } from "../utils/api";
import PushSettings from "../components/PushSettings";

export default function NotificacionesPage() {
  const { notificaciones, setNotificaciones, cargando, error, cargar } = useOutletContext();
  const [filtro, setFiltro] = useState("todas");
  const [guardando, setGuardando] = useState(null);
  const [errorGuardar, setErrorGuardar] = useState("");
  const visibles = notificaciones.filter((aviso) => filtro === "todas" || !aviso.leida);

  const marcarLeida = async (id) => {
    if (guardando !== null) return;
    setGuardando(id);
    setErrorGuardar("");
    try {
      const resultado = await apiFetch(`/api/notificaciones/${id}/leida`, {
        method: "PUT", signal: AbortSignal.timeout(20000),
      });
      if (!resultado) return;
      if (!resultado.response.ok) throw new Error(resultado.data.mensaje || "No se pudo marcar el aviso como leído.");
      setNotificaciones((actuales) => actuales.map((aviso) => aviso.id_notificacion === id
        ? { ...aviso, leida: true } : aviso));
      await cargar();
    } catch (err) {
      setErrorGuardar(err.name === "TypeError" || err.name === "TimeoutError"
        ? "No se pudo confirmar la lectura. Actualizá los avisos y volvé a intentar." : err.message);
    } finally {
      setGuardando(null);
    }
  };

  return (
    <section className="page-stack">
      <header className="page-heading with-action">
        <div><span>MI EMPRESA</span><h1>Notificaciones</h1></div>
        <button className="icon-button" onClick={cargar} title="Actualizar avisos" aria-label="Actualizar avisos"><FaSyncAlt /></button>
      </header>
      <div className="segmented notification-filters">
        <button className={filtro === "todas" ? "active" : ""} onClick={() => setFiltro("todas")}>Todas</button>
        <button className={filtro === "pendientes" ? "active" : ""} onClick={() => setFiltro("pendientes")}>Sin leer</button>
      </div>
      <PushSettings />
      {(errorGuardar || error) && <p className="feedback error" role="alert">{errorGuardar || error}</p>}
      {cargando ? <p className="empty">Cargando avisos...</p> : visibles.length === 0 ? (
        <p className="empty">{filtro === "todas" ? "Todavía no tenés notificaciones." : "No tenés avisos sin leer."}</p>
      ) : <div className="notification-list">{visibles.map((aviso) => (
        <article key={aviso.id_notificacion} className={aviso.leida ? "read" : "unread"}>
          <div className="notification-title"><FaBell /><h2>{aviso.titulo}</h2><span className="status">{aviso.leida ? "Leída" : "Nueva"}</span></div>
          <p>{aviso.mensaje}</p>
          <time>{aviso.fecha_hora}</time>
          {!aviso.leida && <button className="button secondary" disabled={guardando !== null} onClick={() => marcarLeida(aviso.id_notificacion)}><FaCheck />{guardando === aviso.id_notificacion ? "Guardando..." : "Marcar leída"}</button>}
        </article>
      ))}</div>}
    </section>
  );
}
