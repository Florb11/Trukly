import { useEffect, useState } from "react";
import {
  FaTruck,
  FaTruckLoading,
  FaUsers,
  FaClipboardList,
  FaCheckCircle,
  FaClock,
  FaExclamationCircle,
} from "react-icons/fa";
import "./DashboardOperatorPage.css";
import { fetchConToken } from "../utils/fetchConToken";

const operatorStats = [
  {
    label: "Viajes activos",
    value: "18",
    detail: "5 en tránsito ahora",
    icon: <FaTruckLoading />,
    tone: "info",
  },
  {
    label: "Choferes disponibles",
    value: "11",
    detail: "3 en descanso",
    icon: <FaUsers />,
    tone: "success",
  },
  {
    label: "Camiones operativos",
    value: "29",
    detail: "4 en mantenimiento",
    icon: <FaTruck />,
    tone: "warning",
  },
  {
    label: "Viajes del mes",
    value: "143",
    detail: "↑ 12% vs mes anterior",
    icon: <FaClipboardList />,
    tone: "dark",
  },
];

function DashboardOperatorPage({ title = "Panel de operador logístico" }) {
  const [viajes, setViajes] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const cargarViajes = async () => {
    try {
      setCargando(true);
      setError("");

      const resultado = await fetchConToken(
        "http://localhost:5000/api/operador/viajes-recientes",
        { method: "GET" },
      );

      if (!resultado) return;

      const { respuesta, data } = resultado;

      if (!respuesta.ok) {
        throw new Error(data.mensaje || data.msg || "Error al cargar viajes");
      }

      setViajes(data.viajes || []);
    } catch (err) {
      setError(err.message);
      setViajes([]);
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarViajes();
  }, []);

  const viajesMuestra = [
    {
      id_viaje: 1,
      origen: "Buenos Aires",
      destino: "Rosario",
      chofer: "Carlos Méndez",
      camion: "ABC 123",
      estado: "en-curso",
      fecha: "31/05/2026",
    },
    {
      id_viaje: 2,
      origen: "Córdoba",
      destino: "Mendoza",
      chofer: "Laura Gómez",
      camion: "DEF 456",
      estado: "pendiente",
      fecha: "31/05/2026",
    },
    {
      id_viaje: 3,
      origen: "Rosario",
      destino: "Santa Fe",
      chofer: "Martín Torres",
      camion: "GHI 789",
      estado: "finalizado",
      fecha: "30/05/2026",
    },
    {
      id_viaje: 4,
      origen: "Buenos Aires",
      destino: "La Plata",
      chofer: "Sofía Ruiz",
      camion: "JKL 012",
      estado: "aceptado",
      fecha: "30/05/2026",
    },
    {
      id_viaje: 5,
      origen: "Tucumán",
      destino: "Salta",
      chofer: "Diego Herrera",
      camion: "MNO 345",
      estado: "cancelado",
      fecha: "29/05/2026",
    },
  ];

  const viajesVisibles = viajes.length > 0 ? viajes : viajesMuestra;

  return (
    <section className="operator-page">
      <div className="operator-page__header">
        <div>
          <span>Operador logístico</span>
          <h1>{title}</h1>
        </div>
      
      </div>

      <div className="operator-page__grid">
        {operatorStats.map((stat) => (
          <article
            className={`operator-card operator-card--${stat.tone}`}
            key={stat.label}
          >
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
              {[62, 45, 80, 55, 90, 72, 85].map((h, i) => (
                <div key={i} className="operator-chart__bar-wrap">
                  <div
                    className="operator-chart__bar"
                    style={{ height: `${h}%` }}
                  />
                  <span className="operator-chart__label">
                    {["L", "M", "X", "J", "V", "S", "D"][i]}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </article>

        <article className="operator-table-card">
          <div className="operator-table-card__header">
            <h2>Estado de flota</h2>
            <span>Resumen</span>
          </div>

          <div className="operator-progress-list">
            <div className="operator-progress-item">
              <div className="operator-progress-item__top">
                <span>Viajes completados</span>
                <strong>87%</strong>
              </div>
              <div className="operator-progress-item__bar">
                <i style={{ width: "87%" }} />
              </div>
            </div>

            <div className="operator-progress-item">
              <div className="operator-progress-item__top">
                <span>Choferes activos</span>
                <strong>73%</strong>
              </div>
              <div className="operator-progress-item__bar">
                <i style={{ width: "73%" }} />
              </div>
            </div>

            <div className="operator-progress-item">
              <div className="operator-progress-item__top">
                <span>Camiones en ruta</span>
                <strong>61%</strong>
              </div>
              <div className="operator-progress-item__bar">
                <i style={{ width: "61%" }} />
              </div>
            </div>

            <div className="operator-progress-item">
              <div className="operator-progress-item__top">
                <span>Entregas a tiempo</span>
                <strong>94%</strong>
              </div>
              <div className="operator-progress-item__bar">
                <i style={{ width: "94%" }} />
              </div>
            </div>
          </div>
        </article>
      </div>

      <article className="operator-table-card">
        <div className="operator-table-card__header">
          <h2>Viajes recientes</h2>
          <span>Últimas operaciones</span>
        </div>

        {cargando ? (
          <p className="admin-message">Cargando viajes...</p>
        ) : error ? (
          <p className="admin-message admin-message--error">{error}</p>
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
                  <th>Fecha</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                {viajesVisibles.map((v) => (
                  <tr key={v.id_viaje}>
                    <td className="operator-table__id">#{v.id_viaje}</td>
                    <td>{v.origen}</td>
                    <td>{v.destino}</td>
                    <td>{v.chofer}</td>
                    <td>{v.camion}</td>
                    <td>{v.fecha}</td>
                    <td>
                      <span
                        className={`chofer-badge chofer-badge--${v.estado}`}
                      >
                        {v.estado.replace("-", " ")}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </article>
    </section>
  );
}

export default DashboardOperatorPage;
