import { useEffect, useState } from "react";
import {
  FaChartBar,
  FaClipboardCheck,
  FaExclamationTriangle,
  FaRoute,
  FaTruck,
  FaTruckLoading,
  FaUserCog,
  FaUsers,
} from "react-icons/fa";
import { fetchConToken } from "../utils/fetchConToken";
import "./OperadorEstadisticasPage.css";

function OperadorEstadisticasPage() {
  const [estadisticas, setEstadisticas] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    cargarEstadisticas();
  }, []);

  const cargarEstadisticas = async () => {
    try {
      setCargando(true);
      setError("");
      const resultado = await fetchConToken(
        "http://localhost:5000/api/operador/estadisticas",
        { method: "GET" }
      );
      if (!resultado) return;
      const { respuesta, data } = resultado;
      if (!respuesta.ok) throw new Error(data.mensaje || "Error al cargar estadísticas");
      setEstadisticas(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setCargando(false);
    }
  };

  const formatearFecha = (fecha) => {
    if (!fecha) return "-";
    const partes = fecha.split("-");
    if (partes.length !== 3) return fecha;
    return `${partes[2]}/${partes[1]}/${partes[0]}`;
  };

  const getBadgeViaje = (estado) => {
    const e = (estado || "").toLowerCase().replace(/\s+/g, "-");
    if (e === "pendiente") return "op-badge op-badge--pendiente";
    if (e === "aceptado") return "op-badge op-badge--aceptado";
    if (e === "en-curso") return "op-badge op-badge--curso";
    if (e === "finalizado") return "op-badge op-badge--finalizado";
    return "op-badge op-badge--cancelado";
  };

  const getBadgeReporte = (estado) => {
    if (estado === "pendiente") return "op-badge op-badge--pendiente";
    if (estado === "en revision") return "op-badge op-badge--curso";
    if (estado === "resuelto") return "op-badge op-badge--finalizado";
    return "op-badge op-badge--cancelado";
  };

  if (cargando) return <section className="op-stats-page"><p className="admin-message">Cargando estadísticas...</p></section>;
  if (error) return <section className="op-stats-page"><p className="admin-message admin-message--error">{error}</p></section>;

  const resumen = estadisticas?.resumen || {};
  const ultimosViajes = estadisticas?.ultimos_viajes || [];
  const ultimosReportes = estadisticas?.ultimos_reportes || [];
  const choferesTop = estadisticas?.choferes_mas_usados || [];
  const camionesTop = estadisticas?.camiones_mas_usados || [];

  const cards = [
    { label: "Viajes totales", value: resumen.total_viajes ?? 0, detail: `${resumen.viajes_en_curso ?? 0} en curso`, icon: <FaRoute />, tone: "blue" },
    { label: "Finalizados", value: resumen.viajes_finalizados ?? 0, detail: `${resumen.viajes_cancelados ?? 0} cancelados`, icon: <FaTruckLoading />, tone: "green" },
    { label: "Pendientes", value: resumen.viajes_pendientes ?? 0, detail: "Sin iniciar", icon: <FaClipboardCheck />, tone: "violet" },
    { label: "Reportes activos", value: (resumen.reportes_pendientes ?? 0) + (resumen.reportes_en_revision ?? 0), detail: `${resumen.reportes_resueltos ?? 0} resueltos`, icon: <FaExclamationTriangle />, tone: "orange" },
  ];

  return (
    <section className="op-stats-page">
      <div className="op-stats-heading">
        <div>
          <span>Operador logístico</span>
          <h1>Estadísticas</h1>
          <p>Resumen de tu actividad operativa, viajes gestionados y estado de la flota.</p>
        </div>
        <div className="op-stats-heading__icon"><FaChartBar /></div>
      </div>

      <div className="op-stats-summary">
        {cards.map((card) => (
          <article key={card.label} className={`op-stats-card op-stats-card--${card.tone}`}>
            <div>
              <span>{card.label}</span>
              <strong>{card.value}</strong>
              <p>{card.detail}</p>
            </div>
            <div className="op-stats-card__icon">{card.icon}</div>
          </article>
        ))}
      </div>

      <div className="op-stats-grid">
        <article className="op-stats-section">
          <div className="op-stats-section__header">
            <div><h2>Choferes más usados</h2><span>Top 5 según viajes asignados</span></div>
            <FaUsers />
          </div>
          {choferesTop.length === 0 ? (
            <p className="op-stats-empty">No hay datos disponibles.</p>
          ) : (
            <div className="op-stats-ranking">
              {choferesTop.map((chofer, index) => (
                <div key={chofer.id_usuario} className="op-stats-ranking__item">
                  <div className="op-stats-ranking__pos">{index + 1}</div>
                  <div className="op-stats-ranking__info">
                    <strong>{chofer.nombre} {chofer.apellido}</strong>
                    <span>Chofer #{chofer.id_usuario}</span>
                  </div>
                  <div className="op-stats-ranking__value">
                    <strong>{chofer.total_viajes}</strong>
                    <span>viajes</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </article>

        <article className="op-stats-section">
          <div className="op-stats-section__header">
            <div><h2>Camiones más usados</h2><span>Top 5 según viajes asignados</span></div>
            <FaTruck />
          </div>
          {camionesTop.length === 0 ? (
            <p className="op-stats-empty">No hay datos disponibles.</p>
          ) : (
            <div className="op-stats-ranking">
              {camionesTop.map((camion, index) => (
                <div key={camion.id_camion} className="op-stats-ranking__item">
                  <div className="op-stats-ranking__pos">{index + 1}</div>
                  <div className="op-stats-ranking__info">
                    <strong>{camion.matricula}</strong>
                    <span>{camion.marca} {camion.modelo}</span>
                  </div>
                  <div className="op-stats-ranking__value">
                    <strong>{camion.total_viajes}</strong>
                    <span>viajes</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </article>
      </div>

      <div className="op-stats-grid">
        <article className="op-stats-section">
          <div className="op-stats-section__header">
            <div><h2>Últimos viajes</h2><span>Historial reciente</span></div>
            <FaRoute />
          </div>
          {ultimosViajes.length === 0 ? (
            <p className="op-stats-empty">No hay viajes registrados.</p>
          ) : (
            <div className="op-stats-history">
              {ultimosViajes.map((viaje) => (
                <div key={viaje.id_viaje} className="op-stats-history__item">
                  <div className="op-stats-history__icon"><FaTruckLoading /></div>
                  <div className="op-stats-history__content">
                    <strong>{viaje.origen} → {viaje.destino}</strong>
                    <span>Viaje #{viaje.id_viaje} · Chofer #{viaje.Chofer_Usuario_idUsuario} · Camión #{viaje.Camion_id_camion}</span>
                    <small>Salida: {formatearFecha(viaje.fecha_salida)}</small>
                  </div>
                  <span className={getBadgeViaje(viaje.estado)}>{viaje.estado}</span>
                </div>
              ))}
            </div>
          )}
        </article>

        <article className="op-stats-section">
          <div className="op-stats-section__header">
            <div><h2>Últimos reportes</h2><span>Fallas de camiones asignados</span></div>
            <FaClipboardCheck />
          </div>
          {ultimosReportes.length === 0 ? (
            <p className="op-stats-empty">No hay reportes registrados.</p>
          ) : (
            <div className="op-stats-history">
              {ultimosReportes.map((reporte) => (
                <div key={reporte.id_reporte} className="op-stats-history__item">
                  <div className="op-stats-history__icon"><FaExclamationTriangle /></div>
                  <div className="op-stats-history__content">
                    <strong>Reporte #{reporte.id_reporte}</strong>
                    <span>Camión #{reporte.Camion_id_camion} · Chofer #{reporte.Chofer_Usuario_idUsuario}</span>
                    <small>{reporte.descripcion}</small>
                  </div>
                  <span className={getBadgeReporte(reporte.estado)}>{reporte.estado}</span>
                </div>
              ))}
            </div>
          )}
        </article>
      </div>
    </section>
  );
}

export default OperadorEstadisticasPage;