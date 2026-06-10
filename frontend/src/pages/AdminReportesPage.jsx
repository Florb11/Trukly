import { useEffect, useState } from "react";
import { fetchConToken } from "../utils/fetchConToken";
import DetalleReporteModal from "../components/DetalleReporteModal";
import CambiarEstadoReporteModal from "../components/CambiarEstadoReporteModal";
import "./AdminReportesPage.css";

function AdminReportesPage() {
    const [reportes, setReportes] = useState([]);
    const [cargandoReportes, setCargandoReportes] = useState(true);
    const [errorReportes, setErrorReportes] = useState("");

    const [busqueda, setBusqueda] = useState("");
    const [filtroEstado, setFiltroEstado] = useState("todos");

    const [reporteDetalle, setReporteDetalle] = useState(null);

    const [reporteCambiandoEstado, setReporteCambiandoEstado] = useState(null);
    const [nuevoEstado, setNuevoEstado] = useState("");
    const [errorEstado, setErrorEstado] = useState("");

    const cargarReportes = async () => {
        try {
            setCargandoReportes(true);
            setErrorReportes("");

            const resultado = await fetchConToken(
                "http://localhost:5000/api/reportes",
                { method: "GET" }
            );

            if (!resultado) return;

            const { respuesta, data } = resultado;

            if (!respuesta.ok) {
                throw new Error(data.mensaje || data.msg || "Error al cargar reportes");
            }

            setReportes(data.reportes || []);
        } catch (error) {
            setErrorReportes(error.message);
            setReportes([]);
        } finally {
            setCargandoReportes(false);
        }
    };

    useEffect(() => {
        cargarReportes();
    }, []);

    const getEstadoClass = (estado) => {
        if (estado === "pendiente") return "reporte-estado reporte-estado--pendiente";
        if (estado === "en revision") return "reporte-estado reporte-estado--revision";
        if (estado === "resuelto") return "reporte-estado reporte-estado--resuelto";
        return "reporte-estado reporte-estado--cancelado";
    };

    const abrirDetalleReporte = (reporte) => {
        setReporteDetalle(reporte);
    };

    const cerrarDetalleReporte = () => {
        setReporteDetalle(null);
    };

    const abrirCambiarEstadoReporte = (reporte) => {
        setReporteCambiandoEstado(reporte);
        setNuevoEstado(
            reporte.Mecanico_Usuario_idUsuario && reporte.estado === "pendiente"
                ? "en revision"
                : reporte.estado || "pendiente"
        );
        setErrorEstado("");
        setErrorReportes("");
    };

    const cerrarCambiarEstadoReporte = () => {
        setReporteCambiandoEstado(null);
        setNuevoEstado("");
        setErrorEstado("");
    };

    const guardarCambioEstadoReporte = async (e) => {
        e.preventDefault();

        if (!reporteCambiandoEstado) return;

        try {
            setErrorEstado("");
            setErrorReportes("");

            const resultado = await fetchConToken(
                `http://localhost:5000/api/reportes/${reporteCambiandoEstado.id_reporte}/estado`,
                {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        estado: nuevoEstado,
                    }),
                }
            );

            if (!resultado) return;

            const { respuesta, data } = resultado;

            if (!respuesta.ok) {
                throw new Error(data.mensaje || data.msg || "Error al cambiar estado");
            }

            setReportes((prev) =>
                prev.map((reporte) =>
                    reporte.id_reporte === reporteCambiandoEstado.id_reporte
                        ? data.reporte
                        : reporte
                )
            );

            cerrarCambiarEstadoReporte();
        } catch (error) {
            setErrorEstado(error.message);
        }
    };

    const reportesFiltrados = reportes.filter((reporte) => {
        const textoBusqueda = busqueda.trim().toLowerCase();

        const coincideEstado =
            filtroEstado === "todos" || reporte.estado === filtroEstado;

        if (textoBusqueda === "") {
            return coincideEstado;
        }

        const coincideBusqueda =
            reporte.id_reporte?.toString() === textoBusqueda ||
            reporte.descripcion?.toLowerCase().includes(textoBusqueda) ||
            reporte.estado?.toLowerCase().includes(textoBusqueda) ||
            reporte.Camion_id_camion?.toString() === textoBusqueda ||
            reporte.Chofer_Usuario_idUsuario?.toString() === textoBusqueda ||
            reporte.Mecanico_Usuario_idUsuario?.toString() === textoBusqueda;

        return coincideBusqueda && coincideEstado;
    });

    return (
        <section className="reportes-page">
            <div className="reportes-page__heading">
                <div className="reportes-page__heading-text">
                    <span>Administración</span>
                    <h1>Reportes de falla</h1>
                </div>
            </div>

            <article className="reportes-card">
                <div className="reportes-card__header">
                    <div>
                        <h2>Reportes registrados</h2>
                        <span>Consultá las fallas informadas por los choferes</span>
                    </div>
                </div>

                <div className="reportes-filtros">
                    <div className="reportes-filtro-busqueda">
                        <label htmlFor="busquedaReporte">Buscar reporte</label>
                        <input
                            type="text"
                            id="busquedaReporte"
                            value={busqueda}
                            onChange={(e) => setBusqueda(e.target.value)}
                            placeholder="Buscar por ID, descripción, camión o chofer..."
                        />
                    </div>

                    <div className="reportes-filtro-select">
                        <label htmlFor="filtroEstadoReporte">Estado</label>
                        <select
                            id="filtroEstadoReporte"
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

                {cargandoReportes ? (
                    <p className="reportes-feedback">Cargando reportes...</p>
                ) : errorReportes ? (
                    <p className="reportes-feedback reportes-feedback--error">
                        {errorReportes}
                    </p>
                ) : reportes.length === 0 ? (
                    <p className="reportes-feedback">No hay reportes registrados.</p>
                ) : reportesFiltrados.length === 0 ? (
                    <p className="reportes-feedback">
                        No se encontraron reportes con esos filtros.
                    </p>
                ) : (
                    <>
                        <div className="reportes-table-wrap">
                            <table className="reportes-table">
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
                                            <td>{reporte.descripcion}</td>
                                            <td>
                                                <span className={getEstadoClass(reporte.estado)}>
                                                    {reporte.estado}
                                                </span>
                                            </td>
                                            <td>#{reporte.Camion_id_camion}</td>
                                            <td>#{reporte.Chofer_Usuario_idUsuario}</td>
                                            <td>
                                                {reporte.Mecanico_Usuario_idUsuario
                                                    ? `#${reporte.Mecanico_Usuario_idUsuario}`
                                                    : "-"}
                                            </td>
                                            <td>
                                                <div className="reportes-actions">
                                                    <button
                                                        type="button"
                                                        className="btn-reporte btn-reporte--detalle"
                                                        onClick={() => abrirDetalleReporte(reporte)}
                                                    >
                                                        Ver detalle
                                                    </button>

                                                    <button
                                                        type="button"
                                                        className="btn-reporte btn-reporte--estado"
                                                        onClick={() => abrirCambiarEstadoReporte(reporte)}
                                                    >
                                                        Cambiar estado
                                                    </button>
                                                </div>
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

                                            <p className="reporte-card-mobile__subtitulo">
                                                Camión #{reporte.Camion_id_camion} · Chofer #
                                                {reporte.Chofer_Usuario_idUsuario}
                                            </p>
                                        </div>

                                        <span className={getEstadoClass(reporte.estado)}>
                                            {reporte.estado}
                                        </span>
                                    </div>

                                    <div className="reporte-card-mobile__body">
                                        <div className="reporte-card-mobile__field">
                                            <span>Fecha</span>
                                            <p>{reporte.fecha_hora}</p>
                                        </div>

                                        <div className="reporte-card-mobile__field">
                                            <span>Descripción</span>
                                            <p>{reporte.descripcion}</p>
                                        </div>

                                        <div className="reporte-card-mobile__field">
                                            <span>Mecánico</span>
                                            <p>
                                                {reporte.Mecanico_Usuario_idUsuario
                                                    ? `#${reporte.Mecanico_Usuario_idUsuario}`
                                                    : "Sin asignar"}
                                            </p>
                                        </div>
                                    </div>

                                    <div className="reporte-card-mobile__actions">
                                        <button
                                            type="button"
                                            className="btn-reporte btn-reporte--detalle"
                                            onClick={() => abrirDetalleReporte(reporte)}
                                        >
                                            Ver detalle
                                        </button>

                                        <button
                                            type="button"
                                            className="btn-reporte btn-reporte--estado"
                                            onClick={() => abrirCambiarEstadoReporte(reporte)}
                                        >
                                            Cambiar estado
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </>
                )}
            </article>

            {reporteDetalle && (
                <DetalleReporteModal
                    reporte={reporteDetalle}
                    onClose={cerrarDetalleReporte}
                />
            )}

            {reporteCambiandoEstado && (
                <CambiarEstadoReporteModal
                    reporte={reporteCambiandoEstado}
                    nuevoEstado={nuevoEstado}
                    errorEstado={errorEstado}
                    onChange={(e) => setNuevoEstado(e.target.value)}
                    onSubmit={guardarCambioEstadoReporte}
                    onClose={cerrarCambiarEstadoReporte}
                />
            )}
        </section>
    );
}

export default AdminReportesPage;