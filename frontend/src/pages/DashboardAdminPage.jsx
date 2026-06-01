import { useEffect, useState } from "react";
import {
  FaClipboardList,
  FaExclamationTriangle,
  FaTruck,
  FaUsers,
} from "react-icons/fa";
import "./DashboardAdminPage.css";
import { fetchConToken } from "../utils/fetchConToken";

function DashboardAdminPage({ title = "Panel de administrador" }) {
  const [resumenDashboard, setResumenDashboard] = useState(null);
  const [usuariosPendientes, setUsuariosPendientes] = useState([]);
  const [cargandoResumen, setCargandoResumen] = useState(true);
  const [errorResumen, setErrorResumen] = useState("");
  const [mensajeUsuarios, setMensajeUsuarios] = useState("");

  const cargarResumenDashboard = async () => {
    try {
      setCargandoResumen(true);
      setErrorResumen("");

      const resultado = await fetchConToken(
        "http://localhost:5000/api/admin/dashboard/resumen",
        {
          method: "GET",
        }
      );

      if (!resultado) return;

      const { respuesta, data } = resultado;

      if (!respuesta.ok) {
        throw new Error(
          data.mensaje || data.msg || "Error al cargar el resumen del dashboard"
        );
      }

      setResumenDashboard(data);
      setUsuariosPendientes(data.usuarios_pendientes || []);
    } catch (error) {
      setErrorResumen(error.message);
      setResumenDashboard(null);
      setUsuariosPendientes([]);
    } finally {
      setCargandoResumen(false);
    }
  };

  const activarUsuario = async (idUsuario) => {
    try {
      setMensajeUsuarios("");
      setErrorResumen("");

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

      setResumenDashboard((resumenActual) => {
        if (!resumenActual) return resumenActual;

        return {
          ...resumenActual,
          usuarios_activos: resumenActual.usuarios_activos + 1,
        };
      });
    } catch (error) {
      setErrorResumen(error.message);
    }
  };

  useEffect(() => {
    cargarResumenDashboard();
  }, []);

  const getAdminStats = () => {
    const resumen = resumenDashboard || {};

    return [
      {
        label: "Usuarios activos",
        value: resumen.usuarios_activos ?? 0,
        detail: `${usuariosPendientes.length} pendientes por activar`,
        icon: <FaUsers />,
        tone: "danger",
      },
      {
        label: "Camiones registrados",
        value: resumen.camiones_registrados ?? 0,
        detail: `${resumen.camiones_disponibles ?? 0} disponibles`,
        icon: <FaTruck />,
        tone: "dark",
      },
      {
        label: "Reportes abiertos",
        value: resumen.reportes_abiertos ?? 0,
        detail: `${resumen.reportes_prioridad_alta ?? 0} con prioridad alta`,
        icon: <FaExclamationTriangle />,
        tone: "warning",
      },
      {
        label: "Viajes del día",
        value: resumen.viajes_del_dia ?? 0,
        detail: `${resumen.viajes_en_curso ?? 0} en curso`,
        icon: <FaClipboardList />,
        tone: "info",
      },
    ];
  };

  const getEstadoGeneral = () => {
    return (
      resumenDashboard?.estado_general || {
        flota_disponible: 0,
        reportes_resueltos: 0,
        viajes_finalizados: 0,
      }
    );
  };

  const getActividadOperativa = () => {
    const actividad = resumenDashboard?.actividad_operativa || [
      0, 0, 0, 0, 0, 0, 0,
    ];

    const maximo = Math.max(...actividad, 1);

    return actividad.map((valor) => {
      if (valor === 0) return "8%";

      return `${Math.round((valor / maximo) * 100)}%`;
    });
  };

  const estadoGeneral = getEstadoGeneral();

  return (
    <section className="admin-dashboard">
      <div className="admin-dashboard__heading">
        <div>
          <span>Administración</span>
          <h1>{title}</h1>
        </div>

        <button type="button">Nuevo usuario</button>
      </div>

      {cargandoResumen ? (
        <p className="admin-message">Cargando resumen del dashboard...</p>
      ) : errorResumen ? (
        <p className="admin-message admin-message--error">{errorResumen}</p>
      ) : (
        <>
          <div className="admin-small-boxes">
            {getAdminStats().map((stat) => (
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
                {getActividadOperativa().map((altura, index) => (
                  <span key={index} style={{ height: altura }} />
                ))}
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
                  <strong>{estadoGeneral.flota_disponible}%</strong>
                  <div>
                    <i style={{ width: `${estadoGeneral.flota_disponible}%` }} />
                  </div>
                </div>

                <div>
                  <span>Reportes resueltos</span>
                  <strong>{estadoGeneral.reportes_resueltos}%</strong>
                  <div>
                    <i style={{ width: `${estadoGeneral.reportes_resueltos}%` }} />
                  </div>
                </div>

                <div>
                  <span>Viajes finalizados</span>
                  <strong>{estadoGeneral.viajes_finalizados}%</strong>
                  <div>
                    <i style={{ width: `${estadoGeneral.viajes_finalizados}%` }} />
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
              <p className="admin-message admin-message--ok">
                {mensajeUsuarios}
              </p>
            )}

            {usuariosPendientes.length === 0 ? (
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
                        <td>{usuario.licencia || "-"}</td>
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
        </>
      )}
    </section>
  );
}

export default DashboardAdminPage;