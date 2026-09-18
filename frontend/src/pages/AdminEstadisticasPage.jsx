import { useEffect, useState } from "react";
import {
  FaChartBar,
  FaChevronLeft,
  FaChevronRight,
  FaClipboardCheck,
  FaExclamationTriangle,
  FaFilePdf,
  FaRoute,
  FaTruck,
  FaTruckLoading,
  FaUserCog,
  FaUsers,
} from "react-icons/fa";
import { fetchConToken } from "../utils/fetchConToken";
import "./AdminEstadisticasPage.css";

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
    <nav className="estadisticas-pagination" aria-label={`Páginas de ${nombre}`}>
      <button type="button" onClick={() => onChange(pagina - 1)} disabled={pagina === 1} aria-label="Página anterior">
        <FaChevronLeft />
      </button>
      <span>Página {pagina} de {totalPaginas}</span>
      <button type="button" onClick={() => onChange(pagina + 1)} disabled={pagina === totalPaginas} aria-label="Página siguiente">
        <FaChevronRight />
      </button>
    </nav>
  );
}

function AdminEstadisticasPage() {
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
      `${import.meta.env.VITE_API_URL || "http://localhost:5000"}/api/admin/estadisticas?mes=${mes}`,
      { method: "GET", signal: controlador.signal }
    ).then((resultado) => {
      if (!resultado || controlador.signal.aborted) return;
      const { respuesta, data } = resultado;
      if (!respuesta.ok) throw new Error(data.mensaje || data.msg || "Error al cargar las estadísticas");
      setEstadisticas(data);
      setCargando(false);
    }).catch((errorCarga) => {
      if (controlador.signal.aborted) return;
      setError(errorCarga.message);
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
      const { exportarEstadisticasPdf } = await import("../utils/exportAdminStatisticsPdf");
      await exportarEstadisticasPdf(estadisticas, mes);
    } catch {
      setError("No se pudo generar el PDF. Intentá nuevamente.");
    } finally {
      setExportando(false);
    }
  };

  const formatearFecha = (fecha) => {
    if (!fecha) return "-";

    const fechaSimple = fecha.split(" ")[0];
    const partes = fechaSimple.split("-");

    if (partes.length !== 3) return fecha;

    return `${partes[2]}/${partes[1]}/${partes[0]}`;
  };

  const getEstadoViajeClass = (estado) => {
    const estadoNormalizado = (estado || "").toLowerCase().replace(/\s+/g, "-");

    if (estadoNormalizado === "pendiente") {
      return "estadisticas-badge estadisticas-badge--pendiente";
    }

    if (estadoNormalizado === "aceptado") {
      return "estadisticas-badge estadisticas-badge--aceptado";
    }

    if (estadoNormalizado === "en-curso") {
      return "estadisticas-badge estadisticas-badge--curso";
    }

    if (estadoNormalizado === "finalizado") {
      return "estadisticas-badge estadisticas-badge--finalizado";
    }

    return "estadisticas-badge estadisticas-badge--cancelado";
  };

  const getEstadoReporteClass = (estado) => {
    if (estado === "pendiente") {
      return "estadisticas-badge estadisticas-badge--pendiente";
    }

    if (estado === "en revision") {
      return "estadisticas-badge estadisticas-badge--curso";
    }

    if (estado === "resuelto") {
      return "estadisticas-badge estadisticas-badge--finalizado";
    }

    return "estadisticas-badge estadisticas-badge--cancelado";
  };

  const resumen = estadisticas?.resumen || {};
  const choferesMasViajes = estadisticas?.choferes_mas_viajes || [];
  const operadoresMasViajes = estadisticas?.operadores_mas_viajes || [];
  const choferesMasReportes = estadisticas?.choferes_mas_reportes || [];
  const mecanicosMasReparaciones =
    estadisticas?.mecanicos_mas_reparaciones || [];
  const camionesMasReportes = estadisticas?.camiones_mas_reportes || [];
  const ultimosViajes = estadisticas?.ultimos_viajes || [];
  const ultimosReportes = estadisticas?.ultimos_reportes || [];
  const viajesVisibles = ultimosViajes.slice((paginaViajes - 1) * TAMANIO_PAGINA, paginaViajes * TAMANIO_PAGINA);
  const reportesVisibles = ultimosReportes.slice((paginaReportes - 1) * TAMANIO_PAGINA, paginaReportes * TAMANIO_PAGINA);
  const [anio, numeroMes] = mes.split("-").map(Number);
  const nombreMes = new Intl.DateTimeFormat("es-AR", { month: "long", year: "numeric" }).format(new Date(anio, numeroMes - 1, 1));

  const cards = [
    {
      label: "Viajes con salida",
      value: resumen.total_viajes ?? 0,
      detail: `${resumen.viajes_en_curso ?? 0} en curso`,
      icon: <FaRoute />,
      tone: "violet",
    },
    {
      label: "Viajes finalizados",
      value: resumen.viajes_finalizados ?? 0,
      detail: `${resumen.viajes_cancelados ?? 0} cancelados`,
      icon: <FaTruckLoading />,
      tone: "green",
    },
    {
      label: "Reportes activos",
      value: resumen.reportes_activos ?? 0,
      detail: `${resumen.total_reportes ?? 0} reportes totales`,
      icon: <FaExclamationTriangle />,
      tone: "orange",
    },
    {
      label: "Reportes resueltos",
      value: resumen.reportes_resueltos ?? 0,
      detail: "Fallas cerradas",
      icon: <FaClipboardCheck />,
      tone: "blue",
    },
  ];

  return (
    <section className="estadisticas-page">
      <div className="estadisticas-page__heading">
        <div>
          <span>Administración</span>
          <h1>Estadísticas e historiales</h1>
          <p>
            Consultá viajes con salida y reportes creados en el mes seleccionado.
          </p>
        </div>

        <div className="estadisticas-page__heading-icon">
          <FaChartBar />
        </div>
      </div>

      <div className="estadisticas-periodo">
        <div className="estadisticas-periodo__selector">
          <button type="button" onClick={() => seleccionarMes(cambiarMes(mes, -1))} aria-label="Mes anterior" title="Mes anterior">
            <FaChevronLeft />
          </button>
          <label htmlFor="estadisticas-mes">Mes</label>
          <input id="estadisticas-mes" type="month" value={mes} max={mesActual()} onChange={(e) => seleccionarMes(e.target.value)} />
          <button type="button" onClick={() => seleccionarMes(cambiarMes(mes, 1))} disabled={mes >= mesActual()} aria-label="Mes siguiente" title="Mes siguiente">
            <FaChevronRight />
          </button>
        </div>
        <strong>{nombreMes}</strong>
        <button type="button" className="estadisticas-periodo__pdf" onClick={descargarPdf} disabled={cargando || !estadisticas || exportando}>
          <FaFilePdf aria-hidden="true" /> {exportando ? "Preparando PDF..." : "Descargar PDF"}
        </button>
      </div>

      <p className="estadisticas-periodo__nota">Los estados muestran la situación actual de los registros de este mes; no son una foto del cierre mensual.</p>

      {cargando && <p className="admin-message">Cargando estadísticas...</p>}
      {error && <p className="admin-message admin-message--error">{error}</p>}
      {!cargando && estadisticas && (
      <>

      <div className="estadisticas-summary">
        {cards.map((card) => (
          <article
            key={card.label}
            className={`estadisticas-summary-card estadisticas-summary-card--${card.tone}`}
          >
            <div>
              <span>{card.label}</span>
              <strong>{card.value}</strong>
              <p>{card.detail}</p>
            </div>

            <div className="estadisticas-summary-card__icon">{card.icon}</div>
          </article>
        ))}
      </div>

      <div className="estadisticas-grid">
        <article className="estadisticas-card">
          <div className="estadisticas-card__header">
            <div>
              <h2>Choferes con más viajes</h2>
              <span>Ranking según viajes asignados</span>
            </div>

            <FaUsers />
          </div>

          {choferesMasViajes.length === 0 ? (
            <p className="estadisticas-feedback">No hay datos disponibles.</p>
          ) : (
            <div className="estadisticas-ranking">
              {choferesMasViajes.map((chofer, index) => (
                <div
                  key={chofer.id_usuario}
                  className="estadisticas-ranking__item"
                >
                  <div className="estadisticas-ranking__position">
                    {index + 1}
                  </div>

                  <div className="estadisticas-ranking__user">
                    <strong>
                      {chofer.nombre} {chofer.apellido}
                    </strong>
                    <span>Chofer #{chofer.id_usuario}</span>
                  </div>

                  <div className="estadisticas-ranking__values">
                    <strong>{chofer.total_viajes}</strong>
                    <span>viajes</span>
                  </div>

                  <div className="estadisticas-ranking__details">
                    <span>{chofer.viajes_finalizados} finalizados</span>
                    <span>{chofer.viajes_cancelados} cancelados</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </article>

        <article className="estadisticas-card">
          <div className="estadisticas-card__header">
            <div>
              <h2>Operadores con más viajes</h2>
              <span>Viajes gestionados por operador</span>
            </div>

            <FaUserCog />
          </div>

          {operadoresMasViajes.length === 0 ? (
            <p className="estadisticas-feedback">No hay datos disponibles.</p>
          ) : (
            <div className="estadisticas-ranking">
              {operadoresMasViajes.map((operador, index) => (
                <div
                  key={operador.id_usuario}
                  className="estadisticas-ranking__item"
                >
                  <div className="estadisticas-ranking__position">
                    {index + 1}
                  </div>

                  <div className="estadisticas-ranking__user">
                    <strong>
                      {operador.nombre} {operador.apellido}
                    </strong>
                    <span>Operador #{operador.id_usuario}</span>
                  </div>

                  <div className="estadisticas-ranking__values">
                    <strong>{operador.total_viajes}</strong>
                    <span>viajes</span>
                  </div>

                  <div className="estadisticas-ranking__details">
                    <span>{operador.viajes_finalizados} finalizados</span>
                    <span>{operador.viajes_cancelados} cancelados</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </article>
      </div>

      <div className="estadisticas-grid">
        <article className="estadisticas-card">
          <div className="estadisticas-card__header">
            <div>
              <h2>Choferes con más reportes</h2>
              <span>Fallas informadas por chofer</span>
            </div>

            <FaExclamationTriangle />
          </div>

          {choferesMasReportes.length === 0 ? (
            <p className="estadisticas-feedback">No hay datos disponibles.</p>
          ) : (
            <div className="estadisticas-ranking">
              {choferesMasReportes.map((chofer, index) => (
                <div
                  key={chofer.id_usuario}
                  className="estadisticas-ranking__item"
                >
                  <div className="estadisticas-ranking__position">
                    {index + 1}
                  </div>

                  <div className="estadisticas-ranking__user">
                    <strong>
                      {chofer.nombre} {chofer.apellido}
                    </strong>
                    <span>Chofer #{chofer.id_usuario}</span>
                  </div>

                  <div className="estadisticas-ranking__values">
                    <strong>{chofer.total_reportes}</strong>
                    <span>reportes</span>
                  </div>

                  <div className="estadisticas-ranking__details">
                    <span>{chofer.reportes_resueltos} resueltos</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </article>

        <article className="estadisticas-card">
          <div className="estadisticas-card__header">
            <div>
              <h2>Mecánicos con más reparaciones</h2>
              <span>Reportes asignados y resueltos</span>
            </div>

            <FaUserCog />
          </div>

          {mecanicosMasReparaciones.length === 0 ? (
            <p className="estadisticas-feedback">No hay datos disponibles.</p>
          ) : (
            <div className="estadisticas-ranking">
              {mecanicosMasReparaciones.map((mecanico, index) => (
                <div
                  key={mecanico.id_usuario}
                  className="estadisticas-ranking__item"
                >
                  <div className="estadisticas-ranking__position">
                    {index + 1}
                  </div>

                  <div className="estadisticas-ranking__user">
                    <strong>
                      {mecanico.nombre} {mecanico.apellido}
                    </strong>
                    <span>Mecánico #{mecanico.id_usuario}</span>
                  </div>

                  <div className="estadisticas-ranking__values">
                    <strong>{mecanico.total_asignados}</strong>
                    <span>asignados</span>
                  </div>

                  <div className="estadisticas-ranking__details">
                    <span>{mecanico.total_resueltos} resueltos</span>
                    <span>{mecanico.en_revision} en revisión</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </article>
      </div>

      <article className="estadisticas-card">
        <div className="estadisticas-card__header">
          <div>
            <h2>Camiones con más reportes</h2>
            <span>Vehículos que registraron más fallas</span>
          </div>

          <FaTruck />
        </div>

        {camionesMasReportes.length === 0 ? (
          <p className="estadisticas-feedback">No hay datos disponibles.</p>
        ) : (
          <div className="estadisticas-camiones">
            {camionesMasReportes.map((camion, index) => (
              <div
                key={camion.id_camion}
                className="estadisticas-camion-card"
              >
                <span className="estadisticas-camion-card__position">
                  #{index + 1}
                </span>

                <div>
                  <strong>{camion.matricula}</strong>
                  <span>
                    {camion.marca} {camion.modelo}
                  </span>
                </div>

                <div className="estadisticas-camion-card__total">
                  <strong>{camion.total_reportes}</strong>
                  <span>reportes</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </article>

      <div className="estadisticas-history-grid">
        <article className="estadisticas-card">
          <div className="estadisticas-card__header">
            <div>
              <h2>Viajes del mes</h2>
              <span>{ultimosViajes.length} viajes con salida en {nombreMes}</span>
            </div>

            <FaRoute />
          </div>

          {ultimosViajes.length === 0 ? (
            <p className="estadisticas-feedback">
              No hay viajes registrados.
            </p>
          ) : (
            <div className="estadisticas-history-list">
              {viajesVisibles.map((viaje) => (
                <div
                  key={viaje.id_viaje}
                  className="estadisticas-history-item"
                >
                  <div className="estadisticas-history-item__icon">
                    <FaTruckLoading />
                  </div>

                  <div className="estadisticas-history-item__content">
                    <strong>
                      {viaje.origen} → {viaje.destino}
                    </strong>

                    <span>
                      Viaje #{viaje.id_viaje} · Chofer #
                      {viaje.Chofer_Usuario_idUsuario} · Camión #
                      {viaje.Camion_id_camion}
                    </span>

                    <small>
                      Salida: {formatearFecha(viaje.fecha_salida)}
                    </small>
                  </div>

                  <span className={getEstadoViajeClass(viaje.estado)}>
                    {viaje.estado}
                  </span>
                </div>
              ))}
            </div>
          )}
          <Paginacion pagina={paginaViajes} total={ultimosViajes.length} onChange={setPaginaViajes} nombre="viajes" />
        </article>

        <article className="estadisticas-card">
          <div className="estadisticas-card__header">
            <div>
              <h2>Reportes del mes</h2>
              <span>{ultimosReportes.length} reportes creados en {nombreMes}</span>
            </div>

            <FaClipboardCheck />
          </div>

          {ultimosReportes.length === 0 ? (
            <p className="estadisticas-feedback">
              No hay reportes registrados.
            </p>
          ) : (
            <div className="estadisticas-history-list">
              {reportesVisibles.map((reporte) => (
                <div
                  key={reporte.id_reporte}
                  className="estadisticas-history-item"
                >
                  <div className="estadisticas-history-item__icon">
                    <FaExclamationTriangle />
                  </div>

                  <div className="estadisticas-history-item__content">
                    <strong>Reporte #{reporte.id_reporte}</strong>

                    <span>
                      Camión #{reporte.Camion_id_camion} · Chofer #
                      {reporte.Chofer_Usuario_idUsuario}
                    </span>

                    <small>{reporte.descripcion}</small>
                  </div>

                  <span className={getEstadoReporteClass(reporte.estado)}>
                    {reporte.estado}
                  </span>
                </div>
              ))}
            </div>
          )}
          <Paginacion pagina={paginaReportes} total={ultimosReportes.length} onChange={setPaginaReportes} nombre="reportes" />
        </article>
      </div>
      </>
      )}
    </section>
  );
}

export default AdminEstadisticasPage;
