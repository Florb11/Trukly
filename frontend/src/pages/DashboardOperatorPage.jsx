import { useEffect, useState } from "react";
import {
  FaTruck,
  FaTruckLoading,
  FaUsers,
  FaClipboardList,
  FaExclamationTriangle,
  FaCheckCircle,
} from "react-icons/fa";
import "./DashboardOperatorPage.css";
import { fetchConToken } from "../utils/fetchConToken";

function DashboardOperatorPage({ title = "Panel de operador logístico" }) {
  const [viajes, setViajes] = useState([]);
  const [estadisticas, setEstadisticas] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    cargarDatos();
  }, []);

  const cargarDatos = async () => {
    try {
      setCargando(true);
      setError("");

      const [resViajes, resStats] = await Promise.all([
        fetchConToken("http://localhost:5000/api/operador/viajes", { method: "GET" }),
        fetchConToken("http://localhost:5000/api/operador/estadisticas", { method: "GET" }),
      ]);

      if (resViajes) {
        const { respuesta, data } = resViajes;
        if (respuesta.ok) setViajes(Array.isArray(data) ? data : []);
      }

      if (resStats) {
        const { respuesta, data } = resStats;
        if (respuesta.ok) setEstadisticas(data);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setCargando(false);
    }
  };

  const resumen = estadisticas?.resumen || {};

  const stats = [
    {
      label: "Viajes totales",
      value: resumen.total_viajes ?? 0,
      detail: `${resumen.viajes_en_curso ?? 0} en curso`,
      icon: <FaTruckLoading />,
      tone: "info",
    },
    {
      label: "Finalizados",
      value: resumen.viajes_finalizados ?? 0,
      detail: `${resumen.viajes_cancelados ?? 0} cancelados`,
      icon: <FaCheckCircle />,
      tone: "success",
    },
    {
      label: "Pendientes",
      value: resumen.viajes_pendientes ?? 0,
      detail: "Sin iniciar",
      icon: <FaClipboardList />,
      tone: "warning",
    },
    {
      label: "Reportes activos",
      value: (resumen.reportes_pendientes ?? 0) + (resumen.reportes_en_revision ?? 0),
      detail: `${resumen.reportes_resueltos ?? 0} resueltos`,
      icon: <FaExclamationTriangle />,
      tone: "dark",
    },
  ];

  const ultimosViajes = [...viajes]
    .sort((a, b) => b.id_viaje - a.id_viaje)
    .slice(0, 5);

  const total = viajes.length || 1;
  const pct = (n) => Math.round((n / total) * 100);

  const finalizados = viajes.filter(v => v.estado?.toLowerCase() === "finalizado").length;
  const enCurso = viajes.filter(v => v.estado?.toLowerCase() === "en curso").length;
  const pendientes = viajes.filter(v => v.estado?.toLowerCase() === "pendiente").length;
  const cancelados = viajes.filter(v => v.estado?.toLowerCase() === "cancelado").length;

  const getEstadoClass = (estado) => {
    const e = (estado || "").toLowerCase().replace(/\s+/g, "-");
    return `chofer-badge chofer-badge--${e}`;
  };

  return (
    <section className="operator-page">
      <div className="operator-page__header">
        <div>
          <span>Operador logístico</span>
          <h1>{title}</h1>
        </div>
      </div>

      {cargando ? (
        <p className="admin-message">Cargando información...</p>
      ) : error ? (
        <p className="admin-message admin-message--error">{error}</p>
      ) : (
        <>
          <div className="operator-page__grid">
            {stats.map((stat) => (
              <article className={`operator-card operator-card--${stat.tone}`} key={stat.label}>
                <div>
                  <span>{stat.label}</span>
                  <strong>{stat.value}</strong>
                  <p>{stat.detail}</p>
                </div>
                <div className="operator-card__icon">{stat.icon}</div>
              </article>
            ))}
          </div>

          <div className="operator-dashboard__grid">
            <article className="operator-table-card operator-table-card--chart">
              <div className="operator-table-card__header">
                <h2>Actividad semanal</h2>
                <span>Últimos 7 días</span>
              </div>
              <div className="operator-chart">
                <div className="operator-chart__bars">
                  {(() => {
                    const dias = Array.from({ length: 7 }, (_, i) => {
                      const d = new Date();
                      d.setDate(d.getDate() - (6 - i));
                      return d.toISOString().slice(0, 10);
                    });
                    const conteos = dias.map(
                      (dia) => viajes.filter((v) => v.fecha_salida?.slice(0, 10) === dia).length
                    );
                    const maximo = Math.max(...conteos, 1);
                    return conteos.map((v, i) => (
                      <div key={i} className="operator-chart__bar-wrap">
                        <div className="operator-chart__bar" style={{ height: `${Math.round((v / maximo) * 100)}%` }} />
                        <span className="operator-chart__label">
                          {["L", "M", "X", "J", "V", "S", "D"][i]}
                        </span>
                      </div>
                    ));
                  })()}
                </div>
              </div>
            </article>

            <article className="operator-table-card">
              <div className="operator-table-card__header">
                <h2>Distribución de estados</h2>
                <span>Mis viajes</span>
              </div>
              <div className="operator-progress-list">
                {[
                  { label: "Finalizados", value: finalizados },
                  { label: "En curso", value: enCurso },
                  { label: "Pendientes", value: pendientes },
                  { label: "Cancelados", value: cancelados },
                ].map((item) => (
                  <div className="operator-progress-item" key={item.label}>
                    <div className="operator-progress-item__top">
                      <span>{item.label}</span>
                      <strong>{pct(item.value)}%</strong>
                    </div>
                    <div className="operator-progress-item__bar">
                      <i style={{ width: `${pct(item.value)}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </article>
          </div>

          <article className="operator-table-card">
            <div className="operator-table-card__header">
              <h2>Últimos viajes</h2>
              <span>Historial reciente</span>
            </div>
            {ultimosViajes.length === 0 ? (
              <p className="admin-message">No tenés viajes registrados.</p>
            ) : (
              <div className="operator-table-wrap">
                <table className="operator-table">
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>Origen</th>
                      <th>Destino</th>
                      <th>Chofer</th>
                      <th>Camión</th>
                      <th>Fecha salida</th>
                      <th>Estado</th>
                    </tr>
                  </thead>
                  <tbody>
                    {ultimosViajes.map((v) => (
                      <tr key={v.id_viaje}>
                        <td className="operator-table__id">{v.id_viaje}</td>
                        <td>{v.origen}</td>
                        <td>{v.destino}</td>
                        <td>{v.Chofer_Usuario_idUsuario}</td>
                        <td>{v.Camion_id_camion}</td>
                        <td>{v.fecha_salida || "-"}</td>
                        <td>
                          <span className={getEstadoClass(v.estado)}>
                            {v.estado}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </article>
        </>
      )}
    </section>
  );
}

export default DashboardOperatorPage;