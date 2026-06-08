import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { FaTools, FaClipboardList, FaCheckCircle, FaExclamationTriangle } from "react-icons/fa";
import { fetchConToken } from "../utils/fetchConToken";
import "./DashboardMecanicoPage.css";

function DashboardMecanicoPage() {
  const [reportes, setReportes] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const cargarReportes = async () => {
    try {
      setCargando(true);
      setError("");

      const resultado = await fetchConToken(
        "http://localhost:5000/api/mecanico/reportes",
        {
          method: "GET",
        }
      );

      if (!resultado) return;

      const { respuesta, data } = resultado;

      if (!respuesta.ok) {
        throw new Error(
          data.mensaje || data.msg || "Error al cargar los reportes del mecánico"
        );
      }

      setReportes(data.reportes || []);
    } catch (error) {
      setError(error.message);
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarReportes();
  }, []);

  const reportesAsignados = reportes.length;

  const reportesPendientes = reportes.filter(
    (reporte) => reporte.estado !== "resuelto"
  ).length;

  const reportesResueltos = reportes.filter(
    (reporte) => reporte.estado === "resuelto"
  ).length;

  const ultimosReportesAbiertos = reportes
    .filter((reporte) => reporte.estado !== "resuelto")
    .slice(0, 3);

  if (cargando) {
    return (
      <section className="mecanico-dashboard">
        <p className="mecanico-message">Cargando dashboard...</p>
      </section>
    );
  }

  return (
    <section className="mecanico-dashboard">
      <div className="mecanico-dashboard__header">
        <div>
          <span>Panel de mecánico</span>
          <h1>Mantenimiento</h1>
          <p>
            Desde acá podés revisar los reportes asignados, controlar trabajos
            pendientes y marcar reparaciones como resueltas.
          </p>
        </div>

        <div className="mecanico-dashboard__header-icon">
          <FaTools />
        </div>
      </div>

      {error && (
        <p className="mecanico-message mecanico-message--error">
          {error}
        </p>
      )}

      <div className="mecanico-dashboard__cards">
        <article className="mecanico-card">
          <div className="mecanico-card__icon">
            <FaClipboardList />
          </div>

          <span>Reportes asignados</span>
          <strong>{reportesAsignados}</strong>
          <p>Total de fallas asignadas a tu usuario.</p>
        </article>

        <article className="mecanico-card">
          <div className="mecanico-card__icon">
            <FaExclamationTriangle />
          </div>

          <span>Pendientes</span>
          <strong>{reportesPendientes}</strong>
          <p>Reportes que todavía necesitan revisión.</p>
        </article>

        <article className="mecanico-card">
          <div className="mecanico-card__icon">
            <FaCheckCircle />
          </div>

          <span>Resueltos</span>
          <strong>{reportesResueltos}</strong>
          <p>Reparaciones finalizadas correctamente.</p>
        </article>
      </div>

      <div className="mecanico-dashboard__content">
        <article className="mecanico-panel">
          <div className="mecanico-panel__header">
            <div>
              <span>Actividad reciente</span>
              <h2>Últimos reportes abiertos</h2>
            </div>

            <Link to="/dashboardMechanic/reportes" className="mecanico-panel__link">
              Ver todos
            </Link>
          </div>

          {ultimosReportesAbiertos.length === 0 ? (
            <p className="mecanico-empty">
              No tenés reportes abiertos por ahora.
            </p>
          ) : (
            <div className="mecanico-reportes-list">
              {ultimosReportesAbiertos.map((reporte) => (
                <div key={reporte.id_reporte} className="mecanico-reporte-item">
                  <div>
                    <strong>Reporte #{reporte.id_reporte}</strong>
                    <p>{reporte.descripcion}</p>

                    <span>
                      Camión:{" "}
                      {reporte.camion?.matricula ||
                        reporte.Camion_id_camion ||
                        "Sin datos"}
                    </span>
                  </div>

                  <span className={`mecanico-estado mecanico-estado--${reporte.estado}`}>
                    {reporte.estado}
                  </span>
                </div>
              ))}
            </div>
          )}
        </article>

        <article className="mecanico-panel mecanico-panel--info">
          <span>Próxima acción recomendada</span>
          <h2>Revisar reportes pendientes</h2>
          <p>
            Entrá a la sección de reportes asignados para ver el detalle de cada
            falla y resolverla con una nota de reparación.
          </p>

          <Link to="/dashboardMechanic/reportes" className="mecanico-main-action">
            Ir a reportes
          </Link>
        </article>
      </div>
    </section>
  );
}

export default DashboardMecanicoPage;