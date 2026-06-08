import { useEffect, useState } from "react";
import { FaCheckCircle, FaClipboardList } from "react-icons/fa";
import { fetchConToken } from "../utils/fetchConToken";
import MecanicoResolverModal from "../components/MecanicoResolverModal";
import "./MecanicoReportesPage.css";

function MecanicoReportesPage() {
  const [reportes, setReportes] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");

  const [reporteSeleccionado, setReporteSeleccionado] = useState(null);
  const [notaReparacion, setNotaReparacion] = useState("");
  const [resolviendo, setResolviendo] = useState(false);

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

  const abrirModalResolver = (reporte) => {
    setMensaje("");
    setError("");
    setReporteSeleccionado(reporte);
    setNotaReparacion("");
  };

  const cerrarModalResolver = () => {
    setReporteSeleccionado(null);
    setNotaReparacion("");
  };

  const resolverReporte = async (e) => {
    e.preventDefault();

    if (!reporteSeleccionado) return;

    if (notaReparacion.trim() === "") {
      setError("Tenés que escribir una nota de reparación");
      return;
    }

    try {
      setResolviendo(true);
      setMensaje("");
      setError("");

      const resultado = await fetchConToken(
        `http://localhost:5000/api/mecanico/reportes/${reporteSeleccionado.id_reporte}/resolver`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            nota_reparacion: notaReparacion,
          }),
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
          reporte.id_reporte === reporteSeleccionado.id_reporte
            ? data.reporte
            : reporte
        )
      );

      setMensaje(data.mensaje || "Reporte marcado como resuelto");
      cerrarModalResolver();
    } catch (error) {
      setError(error.message);
    } finally {
      setResolviendo(false);
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
                  <th>Nota reparación</th>
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
                      <span
                        className={`mecanico-badge mecanico-badge--${reporte.estado}`}
                      >
                        {reporte.estado}
                      </span>
                    </td>
                    <td>
                      {reporte.nota_reparacion ? (
                        <span className="mecanico-nota">
                          {reporte.nota_reparacion}
                        </span>
                      ) : (
                        <span className="mecanico-muted">-</span>
                      )}
                    </td>
                    <td>
                      {reporte.estado !== "resuelto" ? (
                        <button
                          type="button"
                          className="mecanico-action-btn"
                          onClick={() => abrirModalResolver(reporte)}
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

      <MecanicoResolverModal
        reporte={reporteSeleccionado}
        notaReparacion={notaReparacion}
        setNotaReparacion={setNotaReparacion}
        resolviendo={resolviendo}
        onClose={cerrarModalResolver}
        onSubmit={resolverReporte}
      />
    </section>
  );
}

export default MecanicoReportesPage;