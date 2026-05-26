import { useEffect, useState } from "react";
import {
  FaClipboardList,
  FaExclamationTriangle,
  FaTruck,
  FaUsers,
} from "react-icons/fa";
import "./DashboardAdminPage.css";
import { fetchConToken } from "../utils/fetchConToken";

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

function DashboardAdminPage({ title = "Panel de administrador" }) {
  const [usuariosPendientes, setUsuariosPendientes] = useState([]);
  const [cargandoUsuarios, setCargandoUsuarios] = useState(true);
  const [errorUsuarios, setErrorUsuarios] = useState("");
  const [mensajeUsuarios, setMensajeUsuarios] = useState("");

  const cargarUsuariosPendientes = async () => {
    try {
      setCargandoUsuarios(true);
      setErrorUsuarios("");

      const resultado = await fetchConToken(
        "http://localhost:5000/api/admin/usuarios-pendientes",
        {
          method: "GET",
        }
      );

      if (!resultado) return;

      const { respuesta, data } = resultado;

      if (!respuesta.ok) {
        throw new Error(
          data.mensaje || data.msg || "Error al cargar usuarios pendientes"
        );
      }

      setUsuariosPendientes(data.usuarios || []);
    } catch (error) {
      setErrorUsuarios(error.message);
      setUsuariosPendientes([]);
    } finally {
      setCargandoUsuarios(false);
    }
  };

  const activarUsuario = async (idUsuario) => {
    try {
      setMensajeUsuarios("");
      setErrorUsuarios("");

      const resultado = await fetchConToken(
        `http://localhost:5000/api/admin/usuarios/${idUsuario}/activar`,
        {
          method: "PUT",
        }
      );

      if (!resultado) return;

      const { respuesta, data } = resultado;

      if (!respuesta.ok) {
        throw new Error(
          data.mensaje || data.msg || "Error al activar usuario"
        );
      }

      setMensajeUsuarios(data.mensaje || "Usuario activado correctamente");

      setUsuariosPendientes((usuariosActuales) =>
        usuariosActuales.filter((usuario) => usuario.id_usuario !== idUsuario)
      );
    } catch (error) {
      setErrorUsuarios(error.message);
    }
  };

  useEffect(() => {
    cargarUsuariosPendientes();
  }, []);

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
          <article
            className={`admin-small-box admin-small-box--${stat.tone}`}
            key={stat.label}
          >
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
              <div>
                <i style={{ width: "83%" }} />
              </div>
            </div>

            <div>
              <span>Reportes resueltos</span>
              <strong>68%</strong>
              <div>
                <i style={{ width: "68%" }} />
              </div>
            </div>

            <div>
              <span>Viajes finalizados</span>
              <strong>91%</strong>
              <div>
                <i style={{ width: "91%" }} />
              </div>
            </div>
          </div>
        </article>
      </div>

      <article className="admin-card">
        <div className="admin-card__header">
          <h2>Usuarios pendientes</h2>
          <span>Choferes por activar</span>
        </div>

        {mensajeUsuarios && (
          <p className="admin-message admin-message--ok">{mensajeUsuarios}</p>
        )}

        {cargandoUsuarios ? (
          <p className="admin-message">Cargando usuarios pendientes...</p>
        ) : errorUsuarios ? (
          <p className="admin-message admin-message--error">{errorUsuarios}</p>
        ) : usuariosPendientes.length === 0 ? (
          <p className="admin-message">No hay usuarios pendientes.</p>
        ) : (
          <div className="admin-table-wrap">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Usuario</th>
                  <th>Nombre</th>
                  <th>Apellido</th>
                  <th>Licencia</th>
                  <th>Estado</th>
                  <th>Acción</th>
                </tr>
              </thead>

              <tbody>
                {usuariosPendientes.map((usuario) => (
                  <tr key={usuario.id_usuario}>
                    <td>{usuario.username}</td>
                    <td>{usuario.nombre}</td>
                    <td>{usuario.apellido}</td>
                    <td>{usuario.licencia}</td>
                    <td>
                      <span className="admin-badge admin-badge--warn">
                        {usuario.estado}
                      </span>
                    </td>
                    <td>
                      <button
                        type="button"
                        className="admin-table__action"
                        onClick={() => activarUsuario(usuario.id_usuario)}
                      >
                        Activar
                      </button>
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

export default DashboardAdminPage;