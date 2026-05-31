import { useEffect, useState } from "react";
import { fetchConToken } from "../utils/fetchConToken";
import "./AdminCamionesPage.css";

function AdminCamionesPage() {
    const [camiones, setCamiones] = useState([]);
    const [cargandoCamiones, setCargandoCamiones] = useState(true);
    const [errorCamiones, setErrorCamiones] = useState("");

    const cargarCamiones = async () => {
        try {
            setCargandoCamiones(true);
            setErrorCamiones("");

            const resultado = await fetchConToken(
                "http://localhost:5000/api/admin/camiones",
                { method: "GET" }
            );

            if (!resultado) return;

            const { respuesta, data } = resultado;

            if (!respuesta.ok) {
                throw new Error(data.mensaje || data.msg || "Error al cargar camiones");
            }

            setCamiones(data.camiones || []);
        } catch (error) {
            setErrorCamiones(error.message);
            setCamiones([]);
        } finally {
            setCargandoCamiones(false);
        }
    };

    useEffect(() => {
        cargarCamiones();
    }, []);

    const getEstadoClass = (estado) => {
        if (estado === "disponible") {
            return "camion-estado camion-estado--disponible";
        }

        if (estado === "en viaje") {
            return "camion-estado camion-estado--viaje";
        }

        if (estado === "en mantenimiento") {
            return "camion-estado camion-estado--mantenimiento";
        }

        return "camion-estado camion-estado--inactivo";
    };

    const renderAcciones = () => (
        <div className="camiones-actions">
            <button type="button" className="btn-camion btn-camion--detalle">
                Ver detalle
            </button>

            <button type="button" className="btn-camion btn-camion--editar">
                Editar
            </button>
        </div>
    );

    return (
        <section className="camiones-page">
            <div className="camiones-page__heading">
                <div className="camiones-page__heading-text">
                    <span>Administración</span>
                    <h1>Gestión de camiones</h1>
                </div>

                <button type="button" className="btn-nuevo-camion">
                    + Nuevo camión
                </button>
            </div>

            <article className="camiones-card">
                <div className="camiones-card__header">
                    <h2>Camiones registrados</h2>
                    <span>Consultá la flota y su estado actual</span>
                </div>

                {cargandoCamiones ? (
                    <p className="camiones-feedback">Cargando camiones...</p>
                ) : errorCamiones ? (
                    <p className="camiones-feedback camiones-feedback--error">
                        {errorCamiones}
                    </p>
                ) : camiones.length === 0 ? (
                    <p className="camiones-feedback">No hay camiones registrados.</p>
                ) : (
                    <>
                        <div className="camiones-table-wrap">
                            <table className="camiones-table">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Matrícula</th>
                                        <th>Marca</th>
                                        <th>Modelo</th>
                                        <th>Capacidad</th>
                                        <th>Estado</th>
                                        <th>Nro. tanque</th>
                                        <th>Acciones</th>
                                    </tr>
                                </thead>

                                <tbody>
                                    {camiones.map((camion) => (
                                        <tr key={camion.id_camion}>
                                            <td>#{camion.id_camion}</td>
                                            <td>{camion.matricula}</td>
                                            <td>{camion.marca}</td>
                                            <td>{camion.modelo}</td>
                                            <td>{camion.capacidad_carga} kg</td>
                                            <td>
                                                <span className={getEstadoClass(camion.estado)}>
                                                    {camion.estado}
                                                </span>
                                            </td>
                                            <td>{camion.nroTanque}</td>
                                            <td>{renderAcciones()}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>

                        <div className="camiones-cards-mobile">
                            {camiones.map((camion) => (
                                <div key={camion.id_camion} className="camion-card-mobile">
                                    <div className="camion-card-mobile__header">
                                        <div>
                                            <p className="camion-card-mobile__titulo">
                                                {camion.marca} {camion.modelo}
                                            </p>

                                            <p className="camion-card-mobile__subtitulo">
                                                #{camion.id_camion} · {camion.matricula}
                                            </p>
                                        </div>

                                        <span className={getEstadoClass(camion.estado)}>
                                            {camion.estado}
                                        </span>
                                    </div>

                                    <div className="camion-card-mobile__body">
                                        <div className="camion-card-mobile__field">
                                            <span>Capacidad</span>
                                            <p>{camion.capacidad_carga} kg</p>
                                        </div>

                                        <div className="camion-card-mobile__field">
                                            <span>Nro. tanque</span>
                                            <p>{camion.nroTanque}</p>
                                        </div>
                                    </div>

                                    <div className="camion-card-mobile__actions">
                                        {renderAcciones()}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </>
                )}
            </article>
        </section>
    );
}

export default AdminCamionesPage;