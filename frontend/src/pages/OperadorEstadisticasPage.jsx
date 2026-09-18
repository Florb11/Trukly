import { useEffect, useState } from "react";
import {
  FaChartBar,
  FaChevronLeft,
  FaChevronRight,
  FaCheckCircle,
  FaClipboardCheck,
  FaExclamationTriangle,
  FaFilePdf,
  FaClock,
  FaRoute,
  FaTruck,
  FaTruckLoading,
  FaUsers,
} from "react-icons/fa";
import { fetchConToken } from "../utils/fetchConToken";
import "./OperadorEstadisticasPage.css";

const mesActual = () => {
  const hoy = new Date();
  return `${hoy.getFullYear()}-${String(hoy.getMonth() + 1).padStart(2, "0")}`;
};

const cambiarMes = (mes, desplazamiento) => {
  const [anio, numeroMes] = mes.split("-").map(Number);
  const fecha = new Date(anio, numeroMes - 1 + desplazamiento, 1);
  return `${fecha.getFullYear()}-${String(fecha.getMonth() + 1).padStart(2, "0")}`;
};

const TAMANIO_PAGINA = 10;

function Paginacion({ pagina, total, onChange, nombre }) {
  const totalPaginas = Math.ceil(total / TAMANIO_PAGINA);
  if (totalPaginas <= 1) return null;
  return (
    <nav className="op-stats-pagination" aria-label={`Páginas de ${nombre}`}>
      <button type="button" onClick={() => onChange(pagina - 1)} disabled={pagina === 1} aria-label="Página anterior"><FaChevronLeft /></button>
      <span>Página {pagina} de {totalPaginas}</span>
      <button type="button" onClick={() => onChange(pagina + 1)} disabled={pagina === totalPaginas} aria-label="Página siguiente"><FaChevronRight /></button>
    </nav>
  );
}

function OperadorEstadisticasPage() {
  const [mes, setMes] = useState(mesActual);
  const [estadisticas, setEstadisticas] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [exportando, setExportando] = useState(false);
  const [paginaViajes, setPaginaViajes] = useState(1);
  const [paginaReportes, setPaginaReportes] = useState(1);

  useEffect(() => {
    const controlador = new AbortController();
    fetchConToken(
      `${import.meta.env.VITE_API_URL || "http://localhost:5000"}/api/operador/estadisticas?mes=${mes}`,
      { method: "GET", signal: controlador.signal }
    ).then((resultado) => {
      if (!resultado || controlador.signal.aborted) return;
      const { respuesta, data } = resultado;
      if (!respuesta.ok) throw new Error(data.mensaje || "Error al cargar estadísticas");
      setEstadisticas(data);
      setCargando(false);
    }).catch((err) => {
      if (controlador.signal.aborted) return;
      setError(err.message);
      setEstadisticas(null);
      setCargando(false);
    });
    return () => controlador.abort();
  }, [mes]);

  const seleccionarMes = (nuevoMes) => {
    if (!nuevoMes || nuevoMes === mes || nuevoMes > mesActual()) return;
    setMes(nuevoMes);
    setCargando(true);
    setError("");
    setPaginaViajes(1);
    setPaginaReportes(1);
  };

  const descargarPdf = async () => {
    if (!estadisticas || cargando) return;
    setExportando(true);
    setError("");
    try {
      const { exportarEstadisticasOperadorPdf } = await import("../utils/exportOperatorStatisticsPdf");
      await exportarEstadisticasOperadorPdf(estadisticas, mes);
    } catch {
      setError("No se pudo generar el PDF. Intentá nuevamente.");
    } finally {
      setExportando(false);
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

  const resumen = estadisticas?.resumen || {};
  const ultimosViajes = estadisticas?.ultimos_viajes || [];
  const ultimosReportes = estadisticas?.ultimos_reportes || [];
  const choferesTop = estadisticas?.choferes_mas_usados || [];
  const camionesTop = estadisticas?.camiones_mas_usados || [];
  const viajesVisibles = ultimosViajes.slice((paginaViajes - 1) * TAMANIO_PAGINA, paginaViajes * TAMANIO_PAGINA);
  const reportesVisibles = ultimosReportes.slice((paginaReportes - 1) * TAMANIO_PAGINA, paginaReportes * TAMANIO_PAGINA);
  const [anio, numeroMes] = mes.split("-").map(Number);
  const nombreMes = new Intl.DateTimeFormat("es-AR", { month: "long", year: "numeric" }).format(new Date(anio, numeroMes - 1, 1));

  const cards = [
    { label: "Viajes con salida", value: resumen.total_viajes ?? 0, detail: `${resumen.viajes_en_curso ?? 0} en curso`, icon: <FaRoute />, tone: "blue" },
    { label: "Finalizados", value: resumen.viajes_finalizados ?? 0, detail: `${resumen.viajes_cancelados ?? 0} cancelados`, icon: <FaCheckCircle />, tone: "green" },
    { label: "Pendientes", value: resumen.viajes_pendientes ?? 0, detail: "Sin iniciar", icon: <FaClock />, tone: "violet" },
    { label: "Reportes activos", value: (resumen.reportes_pendientes ?? 0) + (resumen.reportes_en_revision ?? 0), detail: `${resumen.reportes_resueltos ?? 0} resueltos`, icon: <FaClipboardCheck />, tone: "orange" },
  ];

  return (
    <section className="op-stats-page">
      <div className="op-stats-heading">
        <div>
          <span>Operador logístico</span>
          <h1>Estadísticas e historiales</h1>
          <p>Consultá viajes con salida y reportes creados en el mes seleccionado.</p>
        </div>
        <div className="op-stats-heading__icon dashboard-heading-icon" aria-hidden="true"><FaChartBar /></div>
      </div>

      <div className="op-stats-periodo">
        <div className="op-stats-periodo__selector">
          <button type="button" onClick={() => seleccionarMes(cambiarMes(mes, -1))} aria-label="Mes anterior" title="Mes anterior"><FaChevronLeft /></button>
          <label htmlFor="op-stats-mes">Mes</label>
          <input id="op-stats-mes" type="month" value={mes} max={mesActual()} onChange={(event) => seleccionarMes(event.target.value)} />
          <button type="button" onClick={() => seleccionarMes(cambiarMes(mes, 1))} disabled={mes >= mesActual()} aria-label="Mes siguiente" title="Mes siguiente"><FaChevronRight /></button>
        </div>
        <strong>{nombreMes}</strong>
        <button type="button" className="op-stats-periodo__pdf" onClick={descargarPdf} disabled={cargando || !estadisticas || exportando}>
          <FaFilePdf aria-hidden="true" /> {exportando ? "Preparando PDF..." : "Descargar PDF"}
        </button>
      </div>
      <p className="op-stats-periodo__nota">Los estados reflejan la situación actual de los registros del mes, no una foto del cierre mensual. Los reportes corresponden a camiones vinculados a tus viajes.</p>

      {cargando && <p className="admin-message">Cargando estadísticas...</p>}
      {error && <p className="admin-message admin-message--error">{error}</p>}
      {!cargando && estadisticas && <>

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
              {viajesVisibles.map((viaje) => (
                <div key={viaje.id_viaje} className="op-stats-history__item">
                  <div className="op-stats-history__icon"><FaTruckLoading /></div>
                  <div className="op-stats-history__content">
                    <strong>{viaje.origen} → {viaje.destino}</strong>
                    <span>Viaje {viaje.id_viaje} · Chofer {viaje.Chofer_Usuario_idUsuario} · Camión {viaje.Camion_id_camion}</span>
                    <small>Salida: {formatearFecha(viaje.fecha_salida)}</small>
                  </div>
                  <span className={getBadgeViaje(viaje.estado)}>{viaje.estado}</span>
                </div>
              ))}
            </div>
          )}
          <Paginacion pagina={paginaViajes} total={ultimosViajes.length} onChange={setPaginaViajes} nombre="viajes" />
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
              {reportesVisibles.map((reporte) => (
                <div key={reporte.id_reporte} className="op-stats-history__item">
                  <div className="op-stats-history__icon"><FaExclamationTriangle /></div>
                  <div className="op-stats-history__content">
                    <strong>Reporte {reporte.id_reporte}</strong>
                    <span>Camión {reporte.Camion_id_camion} · Chofer {reporte.Chofer_Usuario_idUsuario}</span>
                    <small>{reporte.descripcion}</small>
                  </div>
                  <span className={getBadgeReporte(reporte.estado)}>{reporte.estado}</span>
                </div>
              ))}
            </div>
          )}
          <Paginacion pagina={paginaReportes} total={ultimosReportes.length} onChange={setPaginaReportes} nombre="reportes" />
        </article>
      </div>
      </>}
    </section>
  );
}

export default OperadorEstadisticasPage;
