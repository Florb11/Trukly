import { useEffect, useState } from "react";
import { fetchConToken } from "../utils/fetchConToken";
import NuevoUsuarioModal from "../components/NuevoUsuarioModal";
import EditarUsuarioModal from "../components/EditarUsuarioModal";
import DetalleUsuarioModal from "../components/DetalleUsuarioModal";
import "./AdminUsuariosPage.css";

function AdminUsuariosPage() {
    const [usuarios, setUsuarios] = useState([]);
    const [cargandoUsuarios, setCargandoUsuarios] = useState(true);
    const [errorUsuarios, setErrorUsuarios] = useState("");
    const [mensajeUsuarios, setMensajeUsuarios] = useState("");

    const [usuarioEditando, setUsuarioEditando] = useState(null);
    const [errorEditar, setErrorEditar] = useState("");

    const [mostrarModalNuevo, setMostrarModalNuevo] = useState(false);
    const [errorNuevo, setErrorNuevo] = useState("");

    const [usuarioDetalle, setUsuarioDetalle] = useState(null);

    const [busqueda, setBusqueda] = useState("");
    const [filtroRol, setFiltroRol] = useState("todos");
    const [filtroEstado, setFiltroEstado] = useState("todos");

    const [formEditar, setFormEditar] = useState({
        username: "",
        email: "",
        nombre: "",
        apellido: "",
        estado: "",
        password: "",
        legajo: "",
        licencia: "",
        vencimientoLicencia: "",
        especialidad: "",
        sector: "",
    });

    const [formNuevo, setFormNuevo] = useState({
        username: "",
        email: "",
        password: "",
        nombre: "",
        apellido: "",
        estado: "activo",
        rol: "admin",
        legajo: "",
        licencia: "",
        vencimientoLicencia: "",
        especialidad: "",
        sector: "",
    });

    const cargarUsuarios = async () => {
        try {
            setCargandoUsuarios(true);
            setErrorUsuarios("");

            const resultado = await fetchConToken(
                "http://localhost:5000/api/admin/usuarios",
                { method: "GET" }
            );

            if (!resultado) return;

            const { respuesta, data } = resultado;

            if (!respuesta.ok) {
                throw new Error(data.mensaje || data.msg || "Error al cargar usuarios");
            }

            setUsuarios(data.usuarios || []);
        } catch (error) {
            setErrorUsuarios(error.message);
            setUsuarios([]);
        } finally {
            setCargandoUsuarios(false);
        }
    };

    const activarUsuario = async (idUsuario) => {
        try {
            setMensajeUsuarios("");
            setErrorUsuarios("");

            const resultado = await fetchConToken(
                `http://localhost:5000/api/admin/usuarios/${idUsuario}/activar`,
                { method: "PUT" }
            );

            if (!resultado) return;

            const { respuesta, data } = resultado;

            if (!respuesta.ok) {
                throw new Error(data.mensaje || data.msg || "Error al activar usuario");
            }

            setMensajeUsuarios(data.mensaje || "Usuario activado correctamente");

            setUsuarios((prev) =>
                prev.map((u) =>
                    u.id_usuario === idUsuario ? { ...u, estado: "activo" } : u
                )
            );
        } catch (error) {
            setErrorUsuarios(error.message);
        }
    };

    const desactivarUsuario = async (idUsuario) => {
        try {
            setMensajeUsuarios("");
            setErrorUsuarios("");

            const resultado = await fetchConToken(
                `http://localhost:5000/api/admin/usuarios/${idUsuario}/desactivar`,
                { method: "PUT" }
            );

            if (!resultado) return;

            const { respuesta, data } = resultado;

            if (!respuesta.ok) {
                throw new Error(data.mensaje || data.msg || "Error al desactivar usuario");
            }

            setMensajeUsuarios(data.mensaje || "Usuario desactivado correctamente");

            setUsuarios((prev) =>
                prev.map((u) =>
                    u.id_usuario === idUsuario ? { ...u, estado: "inactivo" } : u
                )
            );
        } catch (error) {
            setErrorUsuarios(error.message);
        }
    };

    const abrirDetalleUsuario = (usuario) => {
        setUsuarioDetalle(usuario);
        setMensajeUsuarios("");
        setErrorUsuarios("");
    };

    const cerrarDetalleUsuario = () => {
        setUsuarioDetalle(null);
    };

    const abrirEditarUsuario = (usuario) => {
        setUsuarioEditando(usuario);
        setMensajeUsuarios("");
        setErrorUsuarios("");
        setErrorEditar("");

        setFormEditar({
            username: usuario.username || "",
            email: usuario.email || "",
            nombre: usuario.nombre || "",
            apellido: usuario.apellido || "",
            estado: usuario.estado || "",
            password: "",
            legajo: usuario.legajo || "",
            licencia: usuario.licencia || "",
            vencimientoLicencia: usuario.vencimientoLicencia || "",
            especialidad: usuario.especialidad || "",
            sector: usuario.sector || "",
        });
    };

    const cerrarEditarUsuario = () => {
        setUsuarioEditando(null);
        setErrorEditar("");

        setFormEditar({
            username: "",
            email: "",
            nombre: "",
            apellido: "",
            estado: "",
            password: "",
            legajo: "",
            licencia: "",
            vencimientoLicencia: "",
            especialidad: "",
            sector: "",
        });
    };

    const handleEditarChange = (e) => {
        setFormEditar({
            ...formEditar,
            [e.target.name]: e.target.value,
        });
    };

    const guardarEdicionUsuario = async (e) => {
        e.preventDefault();

        if (!usuarioEditando) return;

        try {
            setMensajeUsuarios("");
            setErrorUsuarios("");
            setErrorEditar("");

            const resultado = await fetchConToken(
                `http://localhost:5000/api/admin/usuarios/${usuarioEditando.id_usuario}`,
                {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(formEditar),
                }
            );

            if (!resultado) return;

            const { respuesta, data } = resultado;

            if (!respuesta.ok) {
                throw new Error(data.mensaje || data.msg || "Error al modificar usuario");
            }

            const { password, ...datosSinPassword } = formEditar;

            setUsuarios((prev) =>
                prev.map((usuario) =>
                    usuario.id_usuario === usuarioEditando.id_usuario
                        ? {
                              ...usuario,
                              ...datosSinPassword,
                          }
                        : usuario
                )
            );

            setMensajeUsuarios(data.mensaje || "Usuario modificado correctamente");
            cerrarEditarUsuario();
        } catch (error) {
            setErrorEditar(error.message);
        }
    };

    const abrirNuevoUsuario = () => {
        setMostrarModalNuevo(true);
        setErrorNuevo("");
        setMensajeUsuarios("");
        setErrorUsuarios("");
    };

    const cerrarNuevoUsuario = () => {
        setMostrarModalNuevo(false);
        setErrorNuevo("");

        setFormNuevo({
            username: "",
            email: "",
            password: "",
            nombre: "",
            apellido: "",
            estado: "activo",
            rol: "admin",
            legajo: "",
            licencia: "",
            vencimientoLicencia: "",
            especialidad: "",
            sector: "",
        });
    };

    const handleNuevoChange = (e) => {
        setFormNuevo({
            ...formNuevo,
            [e.target.name]: e.target.value,
        });
    };

    const guardarNuevoUsuario = async (e) => {
        e.preventDefault();

        try {
            setErrorNuevo("");
            setMensajeUsuarios("");
            setErrorUsuarios("");

            const resultado = await fetchConToken(
                "http://localhost:5000/api/admin/usuarios",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(formNuevo),
                }
            );

            if (!resultado) return;

            const { respuesta, data } = resultado;

            if (!respuesta.ok) {
                throw new Error(data.mensaje || data.msg || "Error al registrar usuario");
            }

            setUsuarios((prev) => [...prev, data.usuario]);
            setMensajeUsuarios(data.mensaje || "Usuario registrado correctamente");
            cerrarNuevoUsuario();
        } catch (error) {
            setErrorNuevo(error.message);
        }
    };

    useEffect(() => {
        cargarUsuarios();
    }, []);

    const getBadgeClass = (estado) => {
        if (estado === "activo") return "estado-badge estado-badge--activo";
        if (estado === "inactivo") return "estado-badge estado-badge--inactivo";
        return "estado-badge estado-badge--pendiente";
    };

    const getDetalle = (usuario) => {
        if (usuario.rol === "chofer") return `Licencia: ${usuario.licencia || "-"}`;
        if (usuario.rol === "mecanico") return `Especialidad: ${usuario.especialidad || "-"}`;
        if (usuario.rol === "operador") return `Sector: ${usuario.sector || "-"}`;
        if (usuario.rol === "admin") return `Legajo: ${usuario.legajo || "-"}`;
        return "-";
    };

    const renderAcciones = (usuario) => (
        <div className="acciones-group">
            <button
                type="button"
                className="btn-accion btn-accion--detalle"
                onClick={() => abrirDetalleUsuario(usuario)}
            >
                Ver detalle
            </button>

            {(usuario.estado === "pendiente" || usuario.estado === "inactivo") && (
                <button
                    type="button"
                    className="btn-accion btn-accion--activar"
                    onClick={() => activarUsuario(usuario.id_usuario)}
                >
                    Activar
                </button>
            )}

            {usuario.estado === "activo" && (
                <button
                    type="button"
                    className="btn-accion btn-accion--desactivar"
                    onClick={() => desactivarUsuario(usuario.id_usuario)}
                >
                    Desactivar
                </button>
            )}

            <button
                type="button"
                className="btn-accion btn-accion--editar"
                onClick={() => abrirEditarUsuario(usuario)}
            >
                Editar
            </button>
        </div>
    );

    const usuariosFiltrados = usuarios.filter((usuario) => {
        const textoBusqueda = busqueda.toLowerCase();

        const coincideBusqueda =
            usuario.id_usuario?.toString().includes(textoBusqueda) ||
            usuario.username?.toLowerCase().includes(textoBusqueda) ||
            usuario.email?.toLowerCase().includes(textoBusqueda) ||
            usuario.nombre?.toLowerCase().includes(textoBusqueda) ||
            usuario.apellido?.toLowerCase().includes(textoBusqueda) ||
            usuario.rol?.toLowerCase().includes(textoBusqueda) ||
            usuario.estado?.toLowerCase().includes(textoBusqueda);

        const coincideRol = filtroRol === "todos" || usuario.rol === filtroRol;

        const coincideEstado =
            filtroEstado === "todos" || usuario.estado === filtroEstado;

        return coincideBusqueda && coincideRol && coincideEstado;
    });

    return (
        <section className="usuarios-page">
            <div className="usuarios-page__heading">
                <div className="usuarios-page__heading-text">
                    <span>Administración</span>
                    <h1>Gestión de usuarios</h1>
                </div>

                <button
                    type="button"
                    className="btn-nuevo-usuario"
                    onClick={abrirNuevoUsuario}
                >
                    + Nuevo usuario
                </button>
            </div>

            <article className="usuarios-card">
                <div className="usuarios-card__header">
                    <h2>Usuarios del sistema</h2>
                    <span>Administrá cuentas y roles</span>
                </div>

                <div className="usuarios-filtros">
                    <div className="usuarios-filtro-busqueda">
                        <label htmlFor="busqueda">Buscar usuario</label>
                        <input
                            type="text"
                            id="busqueda"
                            value={busqueda}
                            onChange={(e) => setBusqueda(e.target.value)}
                            placeholder="Buscar por ID, usuario, email, nombre..."
                        />
                    </div>

                    <div className="usuarios-filtro-select">
                        <label htmlFor="filtroRol">Rol</label>
                        <select
                            id="filtroRol"
                            value={filtroRol}
                            onChange={(e) => setFiltroRol(e.target.value)}
                        >
                            <option value="todos">Todos</option>
                            <option value="admin">Admin</option>
                            <option value="chofer">Chofer</option>
                            <option value="mecanico">Mecánico</option>
                            <option value="operador">Operador</option>
                        </select>
                    </div>

                    <div className="usuarios-filtro-select">
                        <label htmlFor="filtroEstado">Estado</label>
                        <select
                            id="filtroEstado"
                            value={filtroEstado}
                            onChange={(e) => setFiltroEstado(e.target.value)}
                        >
                            <option value="todos">Todos</option>
                            <option value="activo">Activo</option>
                            <option value="pendiente">Pendiente</option>
                            <option value="inactivo">Inactivo</option>
                        </select>
                    </div>
                </div>

                {mensajeUsuarios && (
                    <p className="usuarios-feedback usuarios-feedback--ok">
                        ✓ {mensajeUsuarios}
                    </p>
                )}

                {cargandoUsuarios ? (
                    <p className="usuarios-feedback usuarios-feedback--loading">
                        Cargando usuarios...
                    </p>
                ) : errorUsuarios ? (
                    <p className="usuarios-feedback usuarios-feedback--error">
                        {errorUsuarios}
                    </p>
                ) : usuarios.length === 0 ? (
                    <p className="usuarios-feedback usuarios-feedback--loading">
                        No hay usuarios registrados.
                    </p>
                ) : usuariosFiltrados.length === 0 ? (
                    <p className="usuarios-feedback usuarios-feedback--loading">
                        No se encontraron usuarios con esos filtros.
                    </p>
                ) : (
                    <>
                        <div className="usuarios-table-wrap">
                            <table className="usuarios-table">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Usuario</th>
                                        <th>Email</th>
                                        <th>Nombre</th>
                                        <th>Apellido</th>
                                        <th>Rol</th>
                                        <th>Estado</th>
                                        <th>Detalle</th>
                                        <th>Acciones</th>
                                    </tr>
                                </thead>

                                <tbody>
                                    {usuariosFiltrados.map((usuario) => (
                                        <tr key={usuario.id_usuario}>
                                            <td>#{usuario.id_usuario}</td>
                                            <td>{usuario.username}</td>
                                            <td>{usuario.email || "-"}</td>
                                            <td>{usuario.nombre}</td>
                                            <td>{usuario.apellido}</td>
                                            <td>{usuario.rol}</td>
                                            <td>
                                                <span className={getBadgeClass(usuario.estado)}>
                                                    {usuario.estado}
                                                </span>
                                            </td>
                                            <td>{getDetalle(usuario)}</td>
                                            <td className="usuarios-table__acciones">
                                                {renderAcciones(usuario)}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>

                        <div className="usuarios-cards-mobile">
                            {usuariosFiltrados.map((usuario) => (
                                <div key={usuario.id_usuario} className="usuario-card-mobile">
                                    <div className="usuario-card-mobile__header">
                                        <div>
                                            <p className="usuario-card-mobile__nombre">
                                                {usuario.nombre} {usuario.apellido}
                                            </p>
                                            <p className="usuario-card-mobile__username">
                                                #{usuario.id_usuario} · @{usuario.username}
                                            </p>
                                        </div>

                                        <span className={getBadgeClass(usuario.estado)}>
                                            {usuario.estado}
                                        </span>
                                    </div>

                                    <div className="usuario-card-mobile__body">
                                        <div className="usuario-card-mobile__field">
                                            <span>Email</span>
                                            <p>{usuario.email || "-"}</p>
                                        </div>

                                        <div className="usuario-card-mobile__field">
                                            <span>Rol</span>
                                            <p>{usuario.rol}</p>
                                        </div>

                                        <div className="usuario-card-mobile__field">
                                            <span>Detalle</span>
                                            <p>{getDetalle(usuario)}</p>
                                        </div>
                                    </div>

                                    <div className="usuario-card-mobile__actions">
                                        {renderAcciones(usuario)}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </>
                )}
            </article>

            {mostrarModalNuevo && (
                <NuevoUsuarioModal
                    formNuevo={formNuevo}
                    errorNuevo={errorNuevo}
                    onChange={handleNuevoChange}
                    onSubmit={guardarNuevoUsuario}
                    onClose={cerrarNuevoUsuario}
                />
            )}

            {usuarioEditando && (
                <EditarUsuarioModal
                    usuarioEditando={usuarioEditando}
                    formEditar={formEditar}
                    errorEditar={errorEditar}
                    onChange={handleEditarChange}
                    onSubmit={guardarEdicionUsuario}
                    onClose={cerrarEditarUsuario}
                />
            )}

            {usuarioDetalle && (
                <DetalleUsuarioModal
                    usuario={usuarioDetalle}
                    onClose={cerrarDetalleUsuario}
                />
            )}
        </section>
    );
}

export default AdminUsuariosPage;