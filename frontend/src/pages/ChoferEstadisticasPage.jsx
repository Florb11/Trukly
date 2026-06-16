import { useEffect, useState } from "react";
import {
  FaChartBar,
  FaClipboardCheck,
  FaExclamationTriangle,
  FaRoute,
  FaTruckLoading,
} from "react-icons/fa";
import { fetchConToken } from "../utils/fetchConToken";
import "./ChoferEstadisticasPage.css";

function ChoferEstadisticasPage() {
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
        "http://localhost:5000/api/choferes/estadisticas",
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
    if (e === "pendiente") return "ch-badge ch-badge--pendiente";
    if (e === "aceptado") return "ch-badge ch-badge--aceptado";
    if (e === "en-curso") return "ch-badge ch-badge--curso";
    if (e === "finalizado") return "ch-badge ch-badge--finalizado";
    return "ch-badge ch-badge--cancelado";
  };

  const getBadgeReporte = (estado) => {
    if (estado === "pendiente") return "ch-badge ch-badge--pendiente";
    if (estado === "en revision") return "ch-badge ch-badge--curso";
    if (estado === "resuelto") return "ch-badge ch-badge--finalizado";
    return "ch-badge ch-badge--cancelado";
  };

  if (cargando) return <section className="ch-stats-page"><p className="admin-message">Cargando estadísticas...</p></section>;
  if (error) return <section className="ch-stats-page"><p className="admin-message admin-message--error">{error}</p></section>;

  const resumen = estadisticas?.resumen || {};
  const ultimosViajes = estadisticas?.ultimos_viajes || [];
  const ultimosReportes = estadisticas?.ultimos_reportes || [];

  const cards = [
    { label: "Viajes totales", value: resumen.total_viajes ?? 0, detail: `${resumen.viajes_en_curso ?? 0} en curso`, icon: <FaRoute />, tone: "blue" },
    { label: "Finalizados", value: resumen.viajes_finalizados ?? 0, detail: `${resumen.viajes_cancelados ?? 0} cancelados`, icon: <FaTruckLoading />, tone: "green" },
    { label: "Pendientes", value: resumen.viajes_pendientes ?? 0, detail: "Sin iniciar", icon: <FaClipboardCheck />, tone: "violet" },
    { label: "Reportes activos", value: (resumen.reportes_pendientes ?? 0) + (resumen.reportes_en_revision ?? 0), detail: `${resumen.reportes_resueltos ?? 0} resueltos`, icon: <FaExclamationTriangle />, tone: "orange" },
  ];

  return (
    <section className="ch-stats-page">
      <div className="ch-stats-heading">
        <div>
          <span>Chofer</span>
          <h1>Mis estadísticas</h1>
          <p>Resumen de tu actividad: viajes realizados y reportes de falla enviados.</p>
        </div>
        <div className="ch-stats-heading__icon"><FaChartBar /></div>
      </div>

      <div className="ch-stats-summary">
        {cards.map((card) => (
          <article key={card.label} className={`ch-stats-card ch-stats-card--${card.tone}`}>
            <div>
              <span>{card.label}</span>
              <strong>{card.value}</strong>
              <p>{card.detail}</p>
            </div>
            <div className="ch-stats-card__icon">{card.icon}</div>
          </article>
        ))}
      </div>

      <div className="ch-stats-grid">
        <article className="ch-stats-section">
          <div className="ch-stats-section__header">
            <div><h2>Últimos viajes</h2><span>Historial reciente</span></div>
            <FaRoute />
          </div>
          {ultimosViajes.length === 0 ? (
            <p className="ch-stats-empty">No tenés viajes registrados.</p>
          ) : (
            <div className="ch-stats-history">
              {ultimosViajes.map((viaje) => (
                <div key={viaje.id_viaje} className="ch-stats-history__item">
                  <div className="ch-stats-history__icon"><FaTruckLoading /></div>
                  <div className="ch-stats-history__content">
                    <strong>{viaje.origen} → {viaje.destino}</strong>
                    <span>Viaje #{viaje.id_viaje} · Camión #{viaje.Camion_id_camion}</span>
                    <small>Salida: {formatearFecha(viaje.fecha_salida)}</small>
                  </div>
                  <span className={getBadgeViaje(viaje.estado)}>{viaje.estado}</span>
                </div>
              ))}
            </div>
          )}
        </article>

        <article className="ch-stats-section">
          <div className="ch-stats-section__header">
            <div><h2>Últimos reportes</h2><span>Fallas enviadas</span></div>
            <FaClipboardCheck />
          </div>
          {ultimosReportes.length === 0 ? (
            <p className="ch-stats-empty">No tenés reportes registrados.</p>
          ) : (
            <div className="ch-stats-history">
              {ultimosReportes.map((reporte) => (
                <div key={reporte.id_reporte} className="ch-stats-history__item">
                  <div className="ch-stats-history__icon"><FaExclamationTriangle /></div>
                  <div className="ch-stats-history__content">
                    <strong>Reporte {reporte.id_reporte}</strong>
                    <span>Camión {reporte.Camion_id_camion}</span>
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

export default ChoferEstadisticasPage;