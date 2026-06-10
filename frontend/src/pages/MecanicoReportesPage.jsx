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
  const [textoBusqueda, setTextoBusqueda] = useState("");
  const [filtroEstado, setFiltroEstado] = useState("todos");
  const [filtroCamion, setFiltroCamion] = useState("todos");

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

  const getEstadoClass = (estado) => {
    const estadoNormalizado = estado?.toString().trim().replaceAll(" ", "-");

    return `mecanico-badge mecanico-badge--${estadoNormalizado}`;
  };

  const estadosDisponibles = [
    ...new Set(reportes.map((reporte) => reporte.estado).filter(Boolean)),
  ];

  const camionesDisponibles = [
    ...new Set(
      reportes.map((reporte) => reporte.Camion_id_camion).filter(Boolean)
    ),
  ];

  const reportesFiltrados = reportes.filter((reporte) => {
    const texto = textoBusqueda.trim().toLowerCase();

    const coincideBusqueda =
      texto === "" ||
      reporte.id_reporte?.toString().includes(texto) ||
      reporte.fecha_hora?.toLowerCase().includes(texto) ||
      reporte.Camion_id_camion?.toString().includes(texto) ||
      reporte.descripcion?.toLowerCase().includes(texto) ||
      reporte.nota_reparacion?.toLowerCase().includes(texto);

    const coincideEstado =
      filtroEstado === "todos" || reporte.estado === filtroEstado;

    const coincideCamion =
      filtroCamion === "todos" ||
      reporte.Camion_id_camion?.toString() === filtroCamion;

    return coincideBusqueda && coincideEstado && coincideCamion;
  });

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
          <>
            <div className="mecanico-reportes-filtros">
              <label className="mecanico-reportes-filtro mecanico-reportes-filtro--busqueda">
                <span>Buscar reporte</span>
                <input
                  type="text"
                  value={textoBusqueda}
                  onChange={(e) => setTextoBusqueda(e.target.value)}
                  placeholder="Buscar por ID, fecha, camión, descripción..."
                />
              </label>

              <label className="mecanico-reportes-filtro">
                <span>Estado</span>
                <select
                  value={filtroEstado}
                  onChange={(e) => setFiltroEstado(e.target.value)}
                >
                  <option value="todos">Todos</option>
                  {estadosDisponibles.map((estado) => (
                    <option key={estado} value={estado}>
                      {estado}
                    </option>
                  ))}
                </select>
              </label>

              <label className="mecanico-reportes-filtro">
                <span>Camión</span>
                <select
                  value={filtroCamion}
                  onChange={(e) => setFiltroCamion(e.target.value)}
                >
                  <option value="todos">Todos</option>
                  {camionesDisponibles.map((camion) => (
                    <option key={camion} value={camion}>
                      Camión {camion}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            {reportesFiltrados.length === 0 ? (
              <p className="mecanico-empty mecanico-empty--filtrado">
                No hay reportes que coincidan con los filtros.
              </p>
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
                {reportesFiltrados.map((reporte) => (
                  <tr key={reporte.id_reporte}>
                    <td>#{reporte.id_reporte}</td>
                    <td>{reporte.fecha_hora}</td>
                    <td>{reporte.Camion_id_camion}</td>
                    <td>{reporte.descripcion}</td>
                    <td>
                      <span className={getEstadoClass(reporte.estado)}>
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
          </>
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