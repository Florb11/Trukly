import { useEffect, useState } from "react";
import {
  FaClipboardList,
  FaCheckCircle,
  FaClock,
  FaTruck,
} from "react-icons/fa";
import "./DashboardTruckerPage.css";
import { fetchConToken } from "../utils/fetchConToken";

function DashboardTruckerPage({ title = "Panel del chofer" }) {
  const [viajes, setViajes] = useState([]);
  const [cargandoViajes, setCargandoViajes] = useState(true);
  const [errorViajes, setErrorViajes] = useState("");

  const usuario = JSON.parse(localStorage.getItem("usuario"));
  const idChofer = usuario?.id_usuario;

  const cargarViajes = async () => {
    try {
      setCargandoViajes(true);
      setErrorViajes("");

      const resultado = await fetchConToken(
        "http://localhost:5000/api/choferes/mis-viajes",
        {
          method: "GET",
        },
      );

      if (!resultado) return;

      const { respuesta, data } = resultado;

      if (!respuesta.ok) {
        throw new Error(data.mensaje || data.msg || "Error al cargar viajes");
      }

      setViajes(Array.isArray(data) ? data : []);
    } catch (error) {
      setErrorViajes(error.message);
      setViajes([]);
    } finally {
      setCargandoViajes(false);
    }
  };

  useEffect(() => {
    cargarViajes();
  }, []);

  const totalViajes = viajes.length;
  const viajesActivos = viajes.filter(
    (v) => v.estado?.toLowerCase() === "en curso",
  ).length;
  const viajesPendientes = viajes.filter(
    (v) => v.estado?.toLowerCase() === "pendiente",
  ).length;
  const viajesFinalizados = viajes.filter(
    (v) => v.estado?.toLowerCase() === "finalizado",
  ).length;
  const viajesCancelados = viajes.filter(
    (v) => v.estado?.toLowerCase() === "cancelado",
  ).length;

  const pct = (n) =>
    totalViajes === 0 ? 0 : Math.round((n / totalViajes) * 100);

  const getChoferStats = () => [
    {
      label: "Viajes totales",
      value: totalViajes,
      detail: `${viajesPendientes} pendientes por iniciar`,
      icon: <FaTruck />,
      tone: "danger",
    },
    {
      label: "En curso",
      value: viajesActivos,
      detail: "Actualmente en ruta",
      icon: <FaClipboardList />,
      tone: "info",
    },
    {
      label: "Pendientes",
      value: viajesPendientes,
      detail: "Esperando inicio",
      icon: <FaClock />,
      tone: "warning",
    },
    {
      label: "Finalizados",
      value: viajesFinalizados,
      detail: `${viajesCancelados} cancelados`,
      icon: <FaCheckCircle />,
      tone: "dark",
    },
  ];

  const getActividadViajes = () => {
    const dias = Array.from({ length: 7 }, (_, i) => {
      const d = new Date();
      d.setDate(d.getDate() - (6 - i));
      return d.toISOString().slice(0, 10);
    });

    const conteos = dias.map(
      (dia) =>
        viajes.filter((v) => v.fecha_salida?.slice(0, 10) === dia).length,
    );

    const maximo = Math.max(...conteos, 1);
    return conteos.map((v) =>
      v === 0 ? "8%" : `${Math.round((v / maximo) * 100)}%`,
    );
  };

  const ultimosViajes = [...viajes]
    .sort((a, b) => new Date(b.fecha_salida) - new Date(a.fecha_salida))
    .slice(0, 5);

  return (
    <section className="admin-dashboard">
      <div className="admin-dashboard__heading">
        <div>
          <span>Dashboard</span>
          <h1>{title}</h1>
        </div>
      </div>

      {cargandoViajes ? (
        <p className="admin-message">Cargando tu información...</p>
      ) : errorViajes ? (
        <p className="admin-message admin-message--error">{errorViajes}</p>
      ) : (
        <>
          <div className="admin-small-boxes">
            {getChoferStats().map((stat) => (
              <article
                className={`admin-small-box admin-small-box--${stat.tone}`}
                key={stat.label}
              >
                <strong>{stat.value}</strong>
                <span>{stat.label}</span>
                <p>{stat.detail}</p>
                <div className="admin-small-box__icon">{stat.icon}</div>
              </article>
            ))}
          </div>

          <div className="admin-dashboard__grid">
            <article className="admin-card admin-card--chart">
              <div className="admin-card__header">
                <h2>Actividad de viajes</h2>
                <span>Últimos 7 días</span>
              </div>
              <div className="admin-chart">
                {getActividadViajes().map((altura, index) => (
                  <span key={index} style={{ height: altura }} />
                ))}
              </div>
            </article>

            <article className="admin-card">
              <div className="admin-card__header">
                <h2>Estado de mis viajes</h2>
                <span>Métricas personales</span>
              </div>
              <div className="admin-progress-list">
                <div>
                  <span>Finalizados</span>
                  <strong>{pct(viajesFinalizados)}%</strong>
                  <div>
                    <i style={{ width: `${pct(viajesFinalizados)}%` }} />
                  </div>
                </div>
                <div>
                  <span>En curso</span>
                  <strong>{pct(viajesActivos)}%</strong>
                  <div>
                    <i style={{ width: `${pct(viajesActivos)}%` }} />
                  </div>
                </div>
                <div>
                  <span>Pendientes</span>
                  <strong>{pct(viajesPendientes)}%</strong>
                  <div>
                    <i style={{ width: `${pct(viajesPendientes)}%` }} />
                  </div>
                </div>
                <div>
                  <span>Cancelados</span>
                  <strong>{pct(viajesCancelados)}%</strong>
                  <div>
                    <i style={{ width: `${pct(viajesCancelados)}%` }} />
                  </div>
                </div>
              </div>
            </article>
          </div>

          <article className="admin-card">
            <div className="admin-card__header">
              <h2>Últimos viajes asignados</h2>
              <span>Historial reciente</span>
            </div>

            {ultimosViajes.length === 0 ? (
              <p className="admin-message">No tenés viajes asignados.</p>
            ) : (
              <div className="admin-table-wrap">
                <table className="admin-table">
                  <thead>
                    <tr>
                      <th>Origen</th>
                      <th>Destino</th>
                      <th>Fecha salida</th>
                      <th>Fecha llegada</th>
                      <th>Estado</th>
                    </tr>
                  </thead>
                  <tbody>
                    {ultimosViajes.map((viaje) => (
                      <tr key={viaje.id_viaje}>
                        <td>{viaje.origen}</td>
                        <td>{viaje.destino}</td>
                        <td>{viaje.fecha_salida}</td>
                        <td>{viaje.fecha_llegada || "-"}</td>
                        <td>
                          <span
                            className={`admin-badge admin-badge--${
                              viaje.estado === "finalizado"
                                ? "ok"
                                : viaje.estado === "en curso"
                                  ? "info"
                                  : viaje.estado === "cancelado"
                                    ? "danger"
                                    : "warn"
                            }`}
                          >
                            {viaje.estado}
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

export default DashboardTruckerPage;
