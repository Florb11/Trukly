import { useEffect, useState } from "react";
import { FaCheckCircle, FaClipboardList } from "react-icons/fa";
import { fetchConToken } from "../utils/fetchConToken";
import "./MecanicoReportesPage.css";

function MecanicoReportesPage() {
  const [reportes, setReportes] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [mensaje, setMensaje] = useState("");
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
          data.mensaje || data.msg || "Error al cargar los reportes"
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

  const resolverReporte = async (idReporte) => {
    try {
      setMensaje("");
      setError("");

      const resultado = await fetchConToken(
        `http://localhost:5000/api/mecanico/reportes/${idReporte}/resolver`,
        {
          method: "PUT",
        }
      );

      if (!resultado) return;

      const { respuesta, data } = resultado;

      if (!respuesta.ok) {
        throw new Error(
          data.mensaje || data.msg || "Error al resolver el reporte"
        );
      }

      setReportes((reportesActuales) =>
        reportesActuales.map((reporte) =>
          reporte.id_reporte === idReporte ? data.reporte : reporte
        )
      );

      setMensaje(data.mensaje || "Reporte marcado como resuelto");
    } catch (error) {
      setError(error.message);
    }
  };

  if (cargando) {
    return (
      <section className="mecanico-reportes-page">
        <p className="mecanico-message">Cargando reportes...</p>
      </section>
    );
  }

  return (
    <section className="mecanico-reportes-page">
      <div className="mecanico-reportes-header">
        <div>
          <span>Reportes</span>
          <h1>Reportes asignados</h1>
          <p>
            Revisá las fallas asignadas y marcá como resueltos los trabajos que
            ya fueron reparados.
          </p>
        </div>

        <div className="mecanico-reportes-header__icon">
          <FaClipboardList />
        </div>
      </div>

      {mensaje && <p className="mecanico-message mecanico-message--ok">{mensaje}</p>}
      {error && <p className="mecanico-message mecanico-message--error">{error}</p>}

      <div className="mecanico-reportes-card">
        {reportes.length === 0 ? (
          <p className="mecanico-empty">No tenés reportes asignados por ahora.</p>
        ) : (
          <div className="mecanico-reportes-table-wrap">
            <table className="mecanico-reportes-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Fecha</th>
                  <th>Camión</th>
                  <th>Descripción</th>
                  <th>Estado</th>
                  <th>Acción</th>
                </tr>
              </thead>

              <tbody>
                {reportes.map((reporte) => (
                  <tr key={reporte.id_reporte}>
                    <td>#{reporte.id_reporte}</td>
                    <td>{reporte.fecha_hora}</td>
                    <td>{reporte.Camion_id_camion}</td>
                    <td>{reporte.descripcion}</td>
                    <td>
                      <span className={`mecanico-badge mecanico-badge--${reporte.estado}`}>
                        {reporte.estado}
                      </span>
                    </td>
                    <td>
                      {reporte.estado !== "resuelto" ? (
                        <button
                          type="button"
                          className="mecanico-action-btn"
                          onClick={() => resolverReporte(reporte.id_reporte)}
                        >
                          <FaCheckCircle />
                          Resolver
                        </button>
                      ) : (
                        <span className="mecanico-resuelto">Finalizado</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
}

export default MecanicoReportesPage;