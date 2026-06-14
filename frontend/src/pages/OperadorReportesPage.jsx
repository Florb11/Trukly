import { useEffect, useState } from "react";
import { fetchConToken } from "../utils/fetchConToken";
import DetalleReporteOperadorModal from "../components/DetalleReporteOperadorModal";
import GestionarReporteModal from "../components/GestionarReporteModal";
import "./OperadorReportesPage.css";

function OperadorReportesPage() {
  const [reportes, setReportes] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const [busqueda, setBusqueda] = useState("");
  const [filtroEstado, setFiltroEstado] = useState("todos");
  const [reporteDetalle, setReporteDetalle] = useState(null);
  const [reporteGestionar, setReporteGestionar] = useState(null);

  useEffect(() => {
    cargarReportes();
  }, []);

  const cargarReportes = async () => {
    try {
      setCargando(true);
      setError("");
      const resultado = await fetchConToken("http://localhost:5000/api/reportes", { method: "GET" });
      if (!resultado) return;
      const { respuesta, data } = resultado;
      if (!respuesta.ok) throw new Error(data.mensaje || "Error al cargar reportes");
      setReportes(data.reportes || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setCargando(false);
    }
  };

  const getEstadoClass = (estado) => {
    if (estado === "pendiente") return "op-reporte-estado op-reporte-estado--pendiente";
    if (estado === "en revision") return "op-reporte-estado op-reporte-estado--revision";
    if (estado === "resuelto") return "op-reporte-estado op-reporte-estado--resuelto";
    return "op-reporte-estado op-reporte-estado--cancelado";
  };

  const reportesFiltrados = reportes.filter((r) => {
    const texto = busqueda.trim().toLowerCase();
    const coincideEstado = filtroEstado === "todos" || r.estado === filtroEstado;
    if (!texto) return coincideEstado;
    const coincideTexto =
      r.id_reporte?.toString().includes(texto) ||
      r.descripcion?.toLowerCase().includes(texto) ||
      r.Camion_id_camion?.toString().includes(texto) ||
      r.Chofer_Usuario_idUsuario?.toString().includes(texto);
    return coincideTexto && coincideEstado;
  });

  return (
    <section className="op-reportes-page">
      <div className="op-reportes-heading">
        <div>
          <span>Operador logístico</span>
          <h1>Reportes de falla</h1>
        </div>
      </div>

      <article className="op-reportes-card">
        <div className="op-reportes-card__header">
          <div>
            <h2>Reportes registrados</h2>
            <span>Asigná mecánicos y gestioná el estado de las fallas</span>
          </div>
        </div>

        <div className="op-reportes-filtros">
          <div className="op-reportes-filtro-busqueda">
            <label htmlFor="busquedaReporte">Buscar reporte</label>
            <input
              type="text"
              id="busquedaReporte"
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              placeholder="Buscar por ID, descripción, camión o chofer..."
            />
          </div>
          <div className="op-reportes-filtro-select">
            <label htmlFor="filtroEstado">Estado</label>
            <select
              id="filtroEstado"
              value={filtroEstado}
              onChange={(e) => setFiltroEstado(e.target.value)}
            >
              <option value="todos">Todos</option>
              <option value="pendiente">Pendiente</option>
              <option value="en revision">En revisión</option>
              <option value="resuelto">Resuelto</option>
              <option value="cancelado">Cancelado</option>
            </select>
          </div>
        </div>

        {cargando ? (
          <p className="op-reportes-feedback">Cargando reportes...</p>
        ) : error ? (
          <p className="op-reportes-feedback op-reportes-feedback--error">{error}</p>
        ) : reportes.length === 0 ? (
          <p className="op-reportes-feedback">No hay reportes registrados.</p>
        ) : reportesFiltrados.length === 0 ? (
          <p className="op-reportes-feedback">No se encontraron reportes con esos filtros.</p>
        ) : (
          <div className="op-reportes-table-wrap">
            <table className="op-reportes-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Fecha</th>
                  <th>Descripción</th>
                  <th>Estado</th>
                  <th>Camión</th>
                  <th>Chofer</th>
                  <th>Mecánico</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {reportesFiltrados.map((reporte) => (
                  <tr key={reporte.id_reporte}>
                    <td>#{reporte.id_reporte}</td>
                    <td>{reporte.fecha_hora}</td>
                    <td className="op-reportes-table__desc">{reporte.descripcion}</td>
                    <td><span className={getEstadoClass(reporte.estado)}>{reporte.estado}</span></td>
                    <td>#{reporte.Camion_id_camion}</td>
                    <td>#{reporte.Chofer_Usuario_idUsuario}</td>
                    <td>{reporte.Mecanico_Usuario_idUsuario ? `#${reporte.Mecanico_Usuario_idUsuario}` : "-"}</td>
                    <td>
                      <div className="op-reportes-actions">
                        <button
                          type="button"
                          className="op-btn-reporte op-btn-reporte--detalle"
                          onClick={() => setReporteDetalle(reporte)}
                        >
                          Ver detalle
                        </button>
                        <button
                          type="button"
                          className="op-btn-reporte op-btn-reporte--gestionar"
                          onClick={() => setReporteGestionar(reporte)}
                        >
                          Gestionar
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </article>

      {reporteDetalle && (
        <DetalleReporteOperadorModal
          reporte={reporteDetalle}
          onClose={() => setReporteDetalle(null)}
        />
      )}

      {reporteGestionar && (
        <GestionarReporteModal
          reporte={reporteGestionar}
          onClose={() => setReporteGestionar(null)}
          onActualizado={() => { cargarReportes(); setReporteGestionar(null); }}
        />
      )}
    </section>
  );
}

export default OperadorReportesPage;