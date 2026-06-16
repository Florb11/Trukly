import { useState, useEffect } from "react";
import NuevoReporteModal from "../components/NuevoReporteModal";
import DetalleReporteModal from "../components/DetalleReporteModal";
import "./ChoferReportesPage.css";
import { fetchConToken } from "../utils/fetchConToken";

// 1. Sacamos el MOCK y dejamos el estado inicial limpio (sin la gravedad)
const FORM_NUEVO_INICIAL = {
  descripcion: "",
  id_camion: "",
};

function ChoferReportesPage() {
  // 2. Inicializamos con un array vacío [] para evitar que el .filter() rompa la pantalla
  const [reportes, setReportes] = useState([]);
  const [reporteDetalle, setReporteDetalle] = useState(null);
  const [mostrarModalNuevo, setMostrarModalNuevo] = useState(false);
  const [formNuevo, setFormNuevo] = useState(FORM_NUEVO_INICIAL);
  const [errorNuevo, setErrorNuevo] = useState("");
  const [mensajeReportes, setMensajeReportes] = useState("");
  const [busqueda, setBusqueda] = useState("");
  const [filtroEstado, setFiltroEstado] = useState("todos");

  // 3. Agregamos useEffect para cargar los reportes al entrar a la página
  useEffect(() => {
    cargarReportes();
  }, []);

  const cargarReportes = async () => {
    try {
      const resultado = await fetchConToken(
        "http://localhost:5000/api/choferes/mis-reportes",
        { method: "GET" },
      );
      if (!resultado) return;
      const { respuesta, data } = resultado;
      if (!respuesta.ok)
        throw new Error(data.mensaje || "Error al obtener los reportes");
      setReportes(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Error cargando reportes:", error);
    }
  };

  const abrirDetalle = (reporte) => {
    setReporteDetalle(reporte);
    setMensajeReportes("");
  };

  const cerrarDetalle = () => {
    setReporteDetalle(null);
  };

  const abrirNuevoReporte = () => {
    setMostrarModalNuevo(true);
    setErrorNuevo("");
    setMensajeReportes("");
  };

  const cerrarNuevoReporte = () => {
    setMostrarModalNuevo(false);
    setErrorNuevo("");
    setFormNuevo(FORM_NUEVO_INICIAL);
  };

  const handleNuevoChange = (e) => {
    setFormNuevo({ ...formNuevo, [e.target.name]: e.target.value });
  };

  const guardarNuevoReporte = async (e) => {
    e.preventDefault();

    if (!formNuevo.descripcion.trim()) {
      setErrorNuevo("La descripción es obligatoria.");
      return;
    }

    if (!formNuevo.id_camion) {
      setErrorNuevo("Debés indicar el ID del camión.");
      return;
    }

    try {
      const token = localStorage.getItem("token");

      const resultado = await fetchConToken(
        "http://localhost:5000/api/reportes",
        {
          method: "POST",
          body: JSON.stringify({
            descripcion: formNuevo.descripcion.trim(),
            Camion_id_camion: Number(formNuevo.id_camion),
          }),
        },
      );
      const { respuesta, data } = resultado;
      if (!respuesta.ok)
        throw new Error(data.mensaje || "Error al crear el reporte");

      setMensajeReportes("Reporte creado correctamente.");
      cerrarNuevoReporte();

      // 4. Volvemos a pedir los datos al backend para que el nuevo reporte aparezca en la lista
      cargarReportes();
    } catch (error) {
      setErrorNuevo(error.message);
    }
  };

  const reportesFiltrados = reportes.filter((r) => {
    const texto = busqueda.toLowerCase();
    const coincideTexto =
      r.id_reporte?.toString().includes(texto) ||
      r.descripcion?.toLowerCase().includes(texto) ||
      r.estado?.toLowerCase().includes(texto) ||
      r.Camion_id_camion?.toString().includes(texto);

    const coincideEstado =
      filtroEstado === "todos" || r.estado === filtroEstado;

    return coincideTexto && coincideEstado;
  });

  const getBadgeClass = (estado) => {
    if (estado === "resuelto") return "estado-badge estado-badge--resuelto";
    if (estado === "en_reparacion")
      return "estado-badge estado-badge--en-reparacion";
    return "estado-badge estado-badge--pendiente";
  };

  const getEstadoLabel = (estado) => {
    if (estado === "resuelto") return "Resuelto";
    if (estado === "en_reparacion") return "En reparación";
    return "Pendiente";
  };

  const renderAcciones = (reporte) => (
    <div className="acciones-group">
      <button
        type="button"
        className="btn-accion btn-accion--detalle"
        onClick={() => abrirDetalle(reporte)}
      >
        Ver detalle
      </button>
    </div>
  );

  return (
    <section className="reportes-page">
      <div className="reportes-page__heading">
        <div className="reportes-page__heading-text">
          <span>Chofer</span>
          <h1>Mis reportes de falla</h1>
        </div>

        <button
          type="button"
          className="btn-nuevo-reporte"
          onClick={abrirNuevoReporte}
        >
          Nuevo reporte
        </button>
      </div>

      <article className="reportes-card">
        <div className="reportes-card__header">
          <h2>Reportes enviados</h2>
          <span>Seguí el estado de tus reportes de falla</span>
        </div>

        <div className="reportes-filtros">
          <div className="reportes-filtro-busqueda">
            <label htmlFor="busqueda">Buscar reporte</label>
            <input
              type="text"
              id="busqueda"
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              placeholder="Buscar por ID, descripción, camión..."
            />
          </div>

          <div className="reportes-filtro-select">
            <label htmlFor="filtroEstado">Estado</label>
            <select
              id="filtroEstado"
              value={filtroEstado}
              onChange={(e) => setFiltroEstado(e.target.value)}
            >
              <option value="todos">Todos</option>
              <option value="pendiente">Pendiente</option>
              <option value="en_reparacion">En reparación</option>
              <option value="resuelto">Resuelto</option>
            </select>
          </div>
        </div>

        {mensajeReportes && (
          <p className="reportes-feedback reportes-feedback--ok">
            ✓ {mensajeReportes}
          </p>
        )}

        {reportes.length === 0 ? (
          <p className="reportes-feedback reportes-feedback--loading">
            No tenés reportes registrados.
          </p>
        ) : reportesFiltrados.length === 0 ? (
          <p className="reportes-feedback reportes-feedback--loading">
            No se encontraron reportes con esos filtros.
          </p>
        ) : (
          <>
            <div className="reportes-table-wrap">
              <table className="reportes-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Fecha y hora</th>
                    <th>Camión</th>
                    <th>Descripción</th>
                    <th>Estado</th>
                    <th>Fecha resolución</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {reportesFiltrados.map((reporte) => (
                    <tr key={reporte.id_reporte}>
                      <td>{reporte.id_reporte}</td>
                      <td>{reporte.fecha_hora}</td>
                      <td>Camión {reporte.Camion_id_camion}</td>
                      <td className="reportes-table__descripcion">
                        {reporte.descripcion}
                      </td>
                      <td>
                        <span className={getBadgeClass(reporte.estado)}>
                          {getEstadoLabel(reporte.estado)}
                        </span>
                      </td>
                      <td>{reporte.fecha_resolucion || "-"}</td>
                      <td className="reportes-table__acciones">
                        {renderAcciones(reporte)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="reportes-cards-mobile">
              {reportesFiltrados.map((reporte) => (
                <div key={reporte.id_reporte} className="reporte-card-mobile">
                  <div className="reporte-card-mobile__header">
                    <div>
                      <p className="reporte-card-mobile__titulo">
                        Reporte #{reporte.id_reporte}
                      </p>
                      <p className="reporte-card-mobile__fecha">
                        {reporte.fecha_hora}
                      </p>
                    </div>
                    <span className={getBadgeClass(reporte.estado)}>
                      {getEstadoLabel(reporte.estado)}
                    </span>
                  </div>

                  <div className="reporte-card-mobile__body">
                    <div className="reporte-card-mobile__field">
                      <span>Camión</span>
                      <p>#{reporte.Camion_id_camion}</p>
                    </div>
                    <div className="reporte-card-mobile__field">
                      <span>Resolución</span>
                      <p>{reporte.fecha_resolucion || "-"}</p>
                    </div>
                    <div className="reporte-card-mobile__field reporte-card-mobile__field--full">
                      <span>Descripción</span>
                      <p>{reporte.descripcion}</p>
                    </div>
                  </div>

                  <div className="reporte-card-mobile__actions">
                    {renderAcciones(reporte)}
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </article>

      {mostrarModalNuevo && (
        <NuevoReporteModal
          formNuevo={formNuevo}
          errorNuevo={errorNuevo}
          onChange={handleNuevoChange}
          onSubmit={guardarNuevoReporte}
          onClose={cerrarNuevoReporte}
        />
      )}

      {reporteDetalle && (
        <DetalleReporteModal
          reporte={reporteDetalle}
          onClose={cerrarDetalle}
          getBadgeClass={getBadgeClass}
          getEstadoLabel={getEstadoLabel}
        />
      )}
    </section>
  );
}

export default ChoferReportesPage;
