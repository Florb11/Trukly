import {
  FaClipboardList,
  FaExclamationTriangle,
  FaTruck,
  FaUsers,
} from "react-icons/fa";
import "./DashboardAdminPage.css";

const adminStats = [
  {
    label: "Usuarios activos",
    value: "128",
    detail: "18 altas este mes",
    icon: <FaUsers />,
    tone: "danger",
  },
  {
    label: "Camiones registrados",
    value: "42",
    detail: "35 disponibles",
    icon: <FaTruck />,
    tone: "dark",
  },
  {
    label: "Reportes abiertos",
    value: "9",
    detail: "3 con prioridad alta",
    icon: <FaExclamationTriangle />,
    tone: "warning",
  },
  {
    label: "Viajes del día",
    value: "24",
    detail: "7 en curso",
    icon: <FaClipboardList />,
    tone: "info",
  },
];

const usuarios = [
  { nombre: "Florencia Bergman", rol: "Administrador", estado: "Activo" },
  { nombre: "Juan Díaz", rol: "Chofer", estado: "Activo" },
  { nombre: "Martín Rivas", rol: "Mecánico", estado: "Pendiente" },
  { nombre: "Camila Soto", rol: "Operador", estado: "Activo" },
];

function DashboardAdminPage({ title = "Panel de administrador" }) {
  return (
    <section className="admin-dashboard">
      <div className="admin-dashboard__heading">
        <div>
          <span>Administración</span>
          <h1>{title}</h1>
        </div>
        <button type="button">Nuevo usuario</button>
      </div>

      <div className="admin-small-boxes">
        {adminStats.map((stat) => (
          <article className={`admin-small-box admin-small-box--${stat.tone}`} key={stat.label}>
            <div>
              <strong>{stat.value}</strong>
              <span>{stat.label}</span>
              <p>{stat.detail}</p>
            </div>
            <div className="admin-small-box__icon">{stat.icon}</div>
          </article>
        ))}
      </div>

      <div className="admin-dashboard__grid">
        <article className="admin-card admin-card--chart">
          <div className="admin-card__header">
            <h2>Actividad operativa</h2>
            <span>Últimos 7 días</span>
          </div>
          <div className="admin-chart">
            <span style={{ height: "52%" }} />
            <span style={{ height: "74%" }} />
            <span style={{ height: "46%" }} />
            <span style={{ height: "86%" }} />
            <span style={{ height: "63%" }} />
            <span style={{ height: "92%" }} />
            <span style={{ height: "70%" }} />
          </div>
        </article>

        <article className="admin-card">
          <div className="admin-card__header">
            <h2>Estado general</h2>
            <span>Sistema</span>
          </div>
          <div className="admin-progress-list">
            <div>
              <span>Flota disponible</span>
              <strong>83%</strong>
              <div><i style={{ width: "83%" }} /></div>
            </div>
            <div>
              <span>Reportes resueltos</span>
              <strong>68%</strong>
              <div><i style={{ width: "68%" }} /></div>
            </div>
            <div>
              <span>Viajes finalizados</span>
              <strong>91%</strong>
              <div><i style={{ width: "91%" }} /></div>
            </div>
          </div>
        </article>
      </div>

      <article className="admin-card">
        <div className="admin-card__header">
          <h2>Usuarios recientes</h2>
          <span>AdminLTE</span>
        </div>

        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Usuario</th>
                <th>Rol</th>
                <th>Estado</th>
                <th>Acción</th>
              </tr>
            </thead>
            <tbody>
              {usuarios.map((usuario) => (
                <tr key={usuario.nombre}>
                  <td>{usuario.nombre}</td>
                  <td>{usuario.rol}</td>
                  <td>
                    <span
                      className={
                        usuario.estado === "Activo"
                          ? "admin-badge admin-badge--ok"
                          : "admin-badge admin-badge--warn"
                      }
                    >
                      {usuario.estado}
                    </span>
                  </td>
                  <td>
                    <button type="button" className="admin-table__action">
                      Ver
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </article>
    </section>
  );
}

export default DashboardAdminPage;