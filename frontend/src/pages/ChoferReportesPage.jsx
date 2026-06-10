import { useState } from "react";
import NuevoReporteModal from "../components/NuevoReporteModal";
// import DetalleReporteModal from "../components/DetalleReporteModal";
import "./ChoferReportesPage.css";

const REPORTES_MOCK = [
  {
    id_reporte: 1,
    fecha_hora: "2025-06-01 08:30:00",
    descripcion:
      "Falla en el sistema de frenos delanteros, se siente vibración al frenar.",
    estado: "pendiente",
    nota_reparacion: null,
    fecha_resolucion: null,
    Camion_id_camion: 3,
    Mecanico_Usuario_idUsuario: null,
    Chofer_Usuario_idUsuario: 7,
  },
  {
    id_reporte: 2,
    fecha_hora: "2025-05-20 14:15:00",
    descripcion: "Luz de tablero indica baja presión de aceite.",
    estado: "en_reparacion",
    nota_reparacion:
      "Se revisó el nivel de aceite, se detectó pérdida en junta.",
    fecha_resolucion: null,
    Camion_id_camion: 3,
    Mecanico_Usuario_idUsuario: 2,
    Chofer_Usuario_idUsuario: 7,
  },
  {
    id_reporte: 3,
    fecha_hora: "2025-04-10 09:00:00",
    descripcion: "Neumático trasero derecho con desgaste irregular.",
    estado: "resuelto",
    nota_reparacion: "Se reemplazó el neumático y se realizó alineación.",
    fecha_resolucion: "2025-04-12 11:00:00",
    Camion_id_camion: 3,
    Mecanico_Usuario_idUsuario: 2,
    Chofer_Usuario_idUsuario: 7,
  },
  {
    id_reporte: 4,
    fecha_hora: "2025-03-05 07:45:00",
    descripcion: "El sistema de climatización no enfría correctamente.",
    estado: "resuelto",
    nota_reparacion: "Se recargó el gas refrigerante y se limpió el filtro.",
    fecha_resolucion: "2025-03-07 16:30:00",
    Camion_id_camion: 3,
    Mecanico_Usuario_idUsuario: 5,
    Chofer_Usuario_idUsuario: 7,
  },
];

const FORM_NUEVO_INICIAL = {
  descripcion: "",
  Camion_id_camion: "",
};

function ChoferReportesPage() {
  const [reportes, setReportes] = useState(REPORTES_MOCK);

  const [reporteDetalle, setReporteDetalle] = useState(null);

  const [mostrarModalNuevo, setMostrarModalNuevo] = useState(false);
  const [formNuevo, setFormNuevo] = useState(FORM_NUEVO_INICIAL);
  const [errorNuevo, setErrorNuevo] = useState("");
  const [mensajeReportes, setMensajeReportes] = useState("");

  const [busqueda, setBusqueda] = useState("");
  const [filtroEstado, setFiltroEstado] = useState("todos");


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

  const guardarNuevoReporte = (e) => {
    e.preventDefault();

    if (!formNuevo.descripcion.trim()) {
      setErrorNuevo("La descripción es obligatoria.");
      return;
    }

    if (!formNuevo.Camion_id_camion) {
      setErrorNuevo("Debés indicar el ID del camión.");
      return;
    }

    const nuevoReporte = {
      id_reporte: reportes.length + 1,
      fecha_hora: new Date().toISOString().replace("T", " ").slice(0, 19),
      descripcion: formNuevo.descripcion.trim(),
      estado: "pendiente",
      nota_reparacion: null,
      fecha_resolucion: null,
      Camion_id_camion: Number(formNuevo.Camion_id_camion),
      Mecanico_Usuario_idUsuario: null,
      Chofer_Usuario_idUsuario: 7,
    };

    setReportes((prev) => [nuevoReporte, ...prev]);
    setMensajeReportes("Reporte creado correctamente.");
    cerrarNuevoReporte();
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
          + Nuevo reporte
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
                      <td>#{reporte.id_reporte}</td>
                      <td>{reporte.fecha_hora}</td>
                      <td>Camión #{reporte.Camion_id_camion}</td>
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
