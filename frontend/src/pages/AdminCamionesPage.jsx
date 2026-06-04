import { useEffect, useState } from "react";
import { fetchConToken } from "../utils/fetchConToken";
import DetalleCamionModal from "../components/DetalleCamionModal";
import NuevoCamionModal from "../components/NuevoCamionModal";
import EditarCamionModal from "../components/EditarCamionModal";
import "./AdminCamionesPage.css";

function AdminCamionesPage() {
    const [camiones, setCamiones] = useState([]);
    const [cargandoCamiones, setCargandoCamiones] = useState(true);
    const [errorCamiones, setErrorCamiones] = useState("");

    const [camionDetalle, setCamionDetalle] = useState(null);

    const [mostrarModalNuevo, setMostrarModalNuevo] = useState(false);
    const [errorNuevo, setErrorNuevo] = useState("");

    const [camionEditando, setCamionEditando] = useState(null);
    const [errorEditar, setErrorEditar] = useState("");

    const [busqueda, setBusqueda] = useState("");
    const [filtroEstado, setFiltroEstado] = useState("todos");

    const [formNuevo, setFormNuevo] = useState({
        matricula: "",
        marca: "",
        modelo: "",
        capacidad_carga: "",
        estado: "disponible",
        nroTanque: "",
    });

    const [formEditar, setFormEditar] = useState({
        matricula: "",
        marca: "",
        modelo: "",
        capacidad_carga: "",
        estado: "",
        nroTanque: "",
    });

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

    const abrirDetalleCamion = (camion) => {
        setCamionDetalle(camion);
    };

    const cerrarDetalleCamion = () => {
        setCamionDetalle(null);
    };

    const abrirNuevoCamion = () => {
        setMostrarModalNuevo(true);
        setErrorNuevo("");
        setErrorCamiones("");
    };

    const cerrarNuevoCamion = () => {
        setMostrarModalNuevo(false);
        setErrorNuevo("");

        setFormNuevo({
            matricula: "",
            marca: "",
            modelo: "",
            capacidad_carga: "",
            estado: "disponible",
            nroTanque: "",
        });
    };

    const handleNuevoChange = (e) => {
        setFormNuevo({
            ...formNuevo,
            [e.target.name]: e.target.value,
        });
    };

    const guardarNuevoCamion = async (e) => {
        e.preventDefault();

        try {
            setErrorNuevo("");
            setErrorCamiones("");

            const datosCamion = {
                ...formNuevo,
                capacidad_carga: Number(formNuevo.capacidad_carga),
                nroTanque: Number(formNuevo.nroTanque),
            };

            const resultado = await fetchConToken(
                "http://localhost:5000/api/admin/camiones",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(datosCamion),
                }
            );

            if (!resultado) return;

            const { respuesta, data } = resultado;

            if (!respuesta.ok) {
                throw new Error(data.mensaje || data.msg || "Error al registrar camión");
            }

            setCamiones((prev) => [...prev, data.camion]);
            cerrarNuevoCamion();
        } catch (error) {
            setErrorNuevo(error.message);
        }
    };

    const abrirEditarCamion = (camion) => {
        setCamionEditando(camion);
        setErrorEditar("");
        setErrorCamiones("");

        setFormEditar({
            matricula: camion.matricula || "",
            marca: camion.marca || "",
            modelo: camion.modelo || "",
            capacidad_carga: camion.capacidad_carga || "",
            estado: camion.estado || "disponible",
            nroTanque: camion.nroTanque || "",
        });
    };

    const cerrarEditarCamion = () => {
        setCamionEditando(null);
        setErrorEditar("");

        setFormEditar({
            matricula: "",
            marca: "",
            modelo: "",
            capacidad_carga: "",
            estado: "",
            nroTanque: "",
        });
    };

    const handleEditarChange = (e) => {
        setFormEditar({
            ...formEditar,
            [e.target.name]: e.target.value,
        });
    };

    const guardarEdicionCamion = async (e) => {
        e.preventDefault();

        if (!camionEditando) return;

        try {
            setErrorEditar("");
            setErrorCamiones("");

            const datosCamion = {
                ...formEditar,
                capacidad_carga: Number(formEditar.capacidad_carga),
                nroTanque: Number(formEditar.nroTanque),
            };

            const resultado = await fetchConToken(
                `http://localhost:5000/api/admin/camiones/${camionEditando.id_camion}`,
                {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(datosCamion),
                }
            );

            if (!resultado) return;

            const { respuesta, data } = resultado;

            if (!respuesta.ok) {
                throw new Error(data.mensaje || data.msg || "Error al modificar camión");
            }

            setCamiones((prev) =>
                prev.map((camion) =>
                    camion.id_camion === camionEditando.id_camion
                        ? data.camion
                        : camion
                )
            );

            cerrarEditarCamion();
        } catch (error) {
            setErrorEditar(error.message);
        }
    };

    const cambiarEstadoCamion = async (idCamion, nuevoEstado) => {
        try {
            setErrorCamiones("");

            const resultado = await fetchConToken(
                `http://localhost:5000/api/admin/camiones/${idCamion}/estado`,
                {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ estado: nuevoEstado }),
                }
            );

            if (!resultado) return;

            const { respuesta, data } = resultado;

            if (!respuesta.ok) {
                throw new Error(
                    data.mensaje || data.msg || "Error al cambiar estado del camión"
                );
            }

            setCamiones((prev) =>
                prev.map((camion) =>
                    camion.id_camion === idCamion ? data.camion : camion
                )
            );
        } catch (error) {
            setErrorCamiones(error.message);
        }
    };

    const camionesFiltrados = camiones.filter((camion) => {
        const textoBusqueda = busqueda.trim().toLowerCase();

        const coincideEstado =
            filtroEstado === "todos" || camion.estado === filtroEstado;

        if (textoBusqueda === "") {
            return coincideEstado;
        }

        const esNumero = !Number.isNaN(Number(textoBusqueda));

        let coincideBusqueda = false;

        if (esNumero) {
            coincideBusqueda =
                camion.id_camion?.toString() === textoBusqueda ||
                camion.nroTanque?.toString() === textoBusqueda ||
                camion.capacidad_carga?.toString().includes(textoBusqueda);
        } else {
            coincideBusqueda =
                camion.matricula?.toLowerCase().includes(textoBusqueda) ||
                camion.marca?.toLowerCase().includes(textoBusqueda) ||
                camion.modelo?.toLowerCase().includes(textoBusqueda) ||
                camion.estado?.toLowerCase().includes(textoBusqueda);
        }

        return coincideBusqueda && coincideEstado;
    });

    const renderAcciones = (camion) => (
        <div className="camiones-actions">
            <button
                type="button"
                className="btn-camion btn-camion--detalle"
                onClick={() => abrirDetalleCamion(camion)}
            >
                Ver detalle
            </button>

            <button
                type="button"
                className="btn-camion btn-camion--editar"
                onClick={() => abrirEditarCamion(camion)}
            >
                Editar
            </button>

            {camion.estado === "inactivo" ? (
                <button
                    type="button"
                    className="btn-camion btn-camion--activar"
                    onClick={() => cambiarEstadoCamion(camion.id_camion, "disponible")}
                >
                    Activar
                </button>
            ) : (
                camion.estado !== "en viaje" && (
                    <button
                        type="button"
                        className="btn-camion btn-camion--desactivar"
                        onClick={() => cambiarEstadoCamion(camion.id_camion, "inactivo")}
                    >
                        Desactivar
                    </button>
                )
            )}
        </div>
    );

    return (
        <section className="camiones-page">
            <div className="camiones-page__heading">
                <div className="camiones-page__heading-text">
                    <span>Administración</span>
                    <h1>Gestión de camiones</h1>
                </div>

                <button
                    type="button"
                    className="btn-nuevo-camion"
                    onClick={abrirNuevoCamion}
                >
                    + Nuevo camión
                </button>
            </div>

            <article className="camiones-card">
                <div className="camiones-card__header">
                    <div>
                        <h2>Camiones registrados</h2>
                        <span>Consultá la flota y su estado actual</span>
                    </div>
                </div>

                <div className="camiones-filtros">
                    <div className="camiones-filtro-busqueda">
                        <label htmlFor="busquedaCamion">Buscar camión</label>
                        <input
                            type="text"
                            id="busquedaCamion"
                            value={busqueda}
                            onChange={(e) => setBusqueda(e.target.value)}
                            placeholder="Buscar por ID, matrícula, marca, modelo..."
                        />
                    </div>

                    <div className="camiones-filtro-select">
                        <label htmlFor="filtroEstadoCamion">Estado</label>
                        <select
                            id="filtroEstadoCamion"
                            value={filtroEstado}
                            onChange={(e) => setFiltroEstado(e.target.value)}
                        >
                            <option value="todos">Todos</option>
                            <option value="disponible">Disponible</option>
                            <option value="en viaje">En viaje</option>
                            <option value="en mantenimiento">En mantenimiento</option>
                            <option value="inactivo">Inactivo</option>
                        </select>
                    </div>
                </div>

                {cargandoCamiones ? (
                    <p className="camiones-feedback">Cargando camiones...</p>
                ) : errorCamiones ? (
                    <p className="camiones-feedback camiones-feedback--error">
                        {errorCamiones}
                    </p>
                ) : camiones.length === 0 ? (
                    <p className="camiones-feedback">No hay camiones registrados.</p>
                ) : camionesFiltrados.length === 0 ? (
                    <p className="camiones-feedback">
                        No se encontraron camiones con esos filtros.
                    </p>
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
                                    {camionesFiltrados.map((camion) => (
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
                                            <td>{renderAcciones(camion)}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>

                        <div className="camiones-cards-mobile">
                            {camionesFiltrados.map((camion) => (
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
                                        {renderAcciones(camion)}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </>
                )}
            </article>

            {camionDetalle && (
                <DetalleCamionModal
                    camion={camionDetalle}
                    onClose={cerrarDetalleCamion}
                />
            )}

            {mostrarModalNuevo && (
                <NuevoCamionModal
                    formNuevo={formNuevo}
                    errorNuevo={errorNuevo}
                    onChange={handleNuevoChange}
                    onSubmit={guardarNuevoCamion}
                    onClose={cerrarNuevoCamion}
                />
            )}

            {camionEditando && (
                <EditarCamionModal
                    camionEditando={camionEditando}
                    formEditar={formEditar}
                    errorEditar={errorEditar}
                    onChange={handleEditarChange}
                    onSubmit={guardarEdicionCamion}
                    onClose={cerrarEditarCamion}
                />
            )}
        </section>
    );
}

export default AdminCamionesPage;