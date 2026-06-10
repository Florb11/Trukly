import { useEffect, useState } from "react";
import {
  FaTools,
  FaExclamationTriangle,
  FaClock,
  FaCheckCircle,
  FaTruck,
  FaUserCog,
} from "react-icons/fa";
import { fetchConToken } from "../utils/fetchConToken";
import "./AdminMantenimientoPage.css";

function AdminMantenimientoPage() {
  const [reportes, setReportes] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const cargarReportes = async () => {
    try {
      setCargando(true);
      setError("");

      const resultado = await fetchConToken(
        "http://localhost:5000/api/reportes",
        { method: "GET" }
      );

      if (!resultado) return;

      const { respuesta, data } = resultado;

      if (!respuesta.ok) {
        throw new Error(data.mensaje || data.msg || "Error al cargar mantenimiento");
      }

      setReportes(data.reportes || []);
    } catch (error) {
      setError(error.message);
      setReportes([]);
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarReportes();
  }, []);

  const reportesPendientes = reportes.filter(
    (reporte) => reporte.estado === "pendiente"
  );

  const reportesEnRevision = reportes.filter(
    (reporte) => reporte.estado === "en revision"
  );

  const reportesResueltos = reportes.filter(
    (reporte) => reporte.estado === "resuelto"
  );

  const reportesActivos = reportes.filter(
    (reporte) => reporte.estado !== "resuelto" && reporte.estado !== "cancelado"
  );

  const getEstadoClass = (estado) => {
    if (estado === "pendiente") return "mantenimiento-estado mantenimiento-estado--pendiente";
    if (estado === "en revision") return "mantenimiento-estado mantenimiento-estado--revision";
    if (estado === "resuelto") return "mantenimiento-estado mantenimiento-estado--resuelto";
    return "mantenimiento-estado mantenimiento-estado--cancelado";
  };

  return (
    <section className="mantenimiento-page">
      <div className="mantenimiento-page__heading">
        <div>
          <span>Administración</span>
          <h1>Mantenimiento</h1>
          <p>
            Supervisá las fallas activas, los camiones afectados y el estado de atención.
          </p>
        </div>

        <div className="mantenimiento-page__icon">
          <FaTools />
        </div>
      </div>

      {cargando ? (
        <p className="admin-message">Cargando mantenimiento...</p>
      ) : error ? (
        <p className="admin-message admin-message--error">{error}</p>
      ) : (
        <>
          <div className="mantenimiento-stats">
            <article className="mantenimiento-stat mantenimiento-stat--warning">
              <div>
                <span>Pendientes</span>
                <strong>{reportesPendientes.length}</strong>
                <p>Fallas sin resolver</p>
              </div>
              <FaExclamationTriangle />
            </article>

            <article className="mantenimiento-stat mantenimiento-stat--info">
              <div>
                <span>En revisión</span>
                <strong>{reportesEnRevision.length}</strong>
                <p>Casos en seguimiento</p>
              </div>
              <FaClock />
            </article>

            <article className="mantenimiento-stat mantenimiento-stat--success">
              <div>
                <span>Resueltos</span>
                <strong>{reportesResueltos.length}</strong>
                <p>Fallas cerradas</p>
              </div>
              <FaCheckCircle />
            </article>
          </div>

          <article className="mantenimiento-card">
            <div className="mantenimiento-card__header">
              <div>
                <h2>Fallas activas</h2>
                <span>Reportes pendientes o en revisión</span>
              </div>
            </div>

            {reportesActivos.length === 0 ? (
              <p className="admin-message">No hay fallas activas.</p>
            ) : (
              <>
                <div className="mantenimiento-table-wrap">
                  <table className="mantenimiento-table">
                    <thead>
                      <tr>
                        <th>Reporte</th>
                        <th>Fecha</th>
                        <th>Camión</th>
                        <th>Chofer</th>
                        <th>Mecánico</th>
                        <th>Estado</th>
                        <th>Descripción</th>
                      </tr>
                    </thead>

                    <tbody>
                      {reportesActivos.map((reporte) => (
                        <tr key={reporte.id_reporte}>
                          <td>#{reporte.id_reporte}</td>
                          <td>{reporte.fecha_hora}</td>
                          <td>
                            <span className="mantenimiento-inline">
                              <FaTruck />
                              #{reporte.Camion_id_camion}
                            </span>
                          </td>
                          <td>#{reporte.Chofer_Usuario_idUsuario}</td>
                          <td>
                            <span className="mantenimiento-inline">
                              <FaUserCog />
                              {reporte.Mecanico_Usuario_idUsuario
                                ? `#${reporte.Mecanico_Usuario_idUsuario}`
                                : "Sin asignar"}
                            </span>
                          </td>
                          <td>
                            <span className={getEstadoClass(reporte.estado)}>
                              {reporte.estado}
                            </span>
                          </td>
                          <td>{reporte.descripcion}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                <div className="mantenimiento-cards-mobile">
                  {reportesActivos.map((reporte) => (
                    <article
                      key={reporte.id_reporte}
                      className="mantenimiento-card-mobile"
                    >
                      <div className="mantenimiento-card-mobile__top">
                        <div>
                          <strong>Reporte #{reporte.id_reporte}</strong>
                          <span>{reporte.fecha_hora}</span>
                        </div>

                        <span className={getEstadoClass(reporte.estado)}>
                          {reporte.estado}
                        </span>
                      </div>

                      <p>{reporte.descripcion}</p>

                      <div className="mantenimiento-card-mobile__grid">
                        <div>
                          <span>Camión</span>
                          <strong>#{reporte.Camion_id_camion}</strong>
                        </div>

                        <div>
                          <span>Chofer</span>
                          <strong>#{reporte.Chofer_Usuario_idUsuario}</strong>
                        </div>

                        <div>
                          <span>Mecánico</span>
                          <strong>
                            {reporte.Mecanico_Usuario_idUsuario
                              ? `#${reporte.Mecanico_Usuario_idUsuario}`
                              : "Sin asignar"}
                          </strong>
                        </div>
                      </div>
                    </article>
                  ))}
                </div>
              </>
            )}
          </article>
        </>
      )}
    </section>
  );
}

export default AdminMantenimientoPage;