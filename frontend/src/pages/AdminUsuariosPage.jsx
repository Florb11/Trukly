import { useEffect, useState } from "react";
import { fetchConToken } from "../utils/fetchConToken";
import "./AdminUsuariosPage.css";

function AdminUsuariosPage() {
const [usuarios, setUsuarios] = useState([]);
const [cargandoUsuarios, setCargandoUsuarios] = useState(true);
const [errorUsuarios, setErrorUsuarios] = useState("");
const [mensajeUsuarios, setMensajeUsuarios] = useState("");

const [usuarioEditando, setUsuarioEditando] = useState(null);
const [errorEditar, setErrorEditar] = useState("");

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

    return (
        <section className="usuarios-page">
            <div className="usuarios-page__heading">
                <div className="usuarios-page__heading-text">
                    <span>Administración</span>
                    <h1>Gestión de usuarios</h1>
                </div>

                <button type="button" className="btn-nuevo-usuario">
                    + Nuevo usuario
                </button>
            </div>

            <article className="usuarios-card">
                <div className="usuarios-card__header">
                    <h2>Usuarios del sistema</h2>
                    <span>Administrá cuentas y roles</span>
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
                ) : (
                    <>
                        <div className="usuarios-table-wrap">
                            <table className="usuarios-table">
                                <thead>
                                    <tr>
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
                                    {usuarios.map((usuario) => (
                                        <tr key={usuario.id_usuario}>
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
                                            <td>{renderAcciones(usuario)}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>

                        <div className="usuarios-cards-mobile">
                            {usuarios.map((usuario) => (
                                <div key={usuario.id_usuario} className="usuario-card-mobile">
                                    <div className="usuario-card-mobile__header">
                                        <div>
                                            <p className="usuario-card-mobile__nombre">
                                                {usuario.nombre} {usuario.apellido}
                                            </p>
                                            <p className="usuario-card-mobile__username">
                                                @{usuario.username}
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

            {usuarioEditando && (
                <div className="usuarios-modal-backdrop">
                    <div className="usuarios-modal">
                        <div className="usuarios-modal__header">
                            <div>
                                <span>Editar usuario</span>
                                <h2>{usuarioEditando.username}</h2>
                            </div>

                            <button type="button" onClick={cerrarEditarUsuario}>
                                ×
                            </button>
                        </div>

                        {errorEditar && (
                            <p className="usuarios-feedback usuarios-feedback--error">
                                {errorEditar}
                            </p>
                        )}

                        <form className="usuarios-form" onSubmit={guardarEdicionUsuario}>
                            <label>
                                Usuario
                                <input
                                    type="text"
                                    name="username"
                                    value={formEditar.username}
                                    onChange={handleEditarChange}
                                />
                            </label>

                            <label>
                                Email
                                <input
                                    type="email"
                                    name="email"
                                    value={formEditar.email}
                                    onChange={handleEditarChange}
                                />
                            </label>

                            <label>
                                Nombre
                                <input
                                    type="text"
                                    name="nombre"
                                    value={formEditar.nombre}
                                    onChange={handleEditarChange}
                                />
                            </label>

                            <label>
                                Apellido
                                <input
                                    type="text"
                                    name="apellido"
                                    value={formEditar.apellido}
                                    onChange={handleEditarChange}
                                />
                            </label>

                            <label>
                                Estado
                                <select
                                    name="estado"
                                    value={formEditar.estado}
                                    onChange={handleEditarChange}
                                >
                                    <option value="pendiente">Pendiente</option>
                                    <option value="activo">Activo</option>
                                    <option value="inactivo">Inactivo</option>
                                </select>
                            </label>

                            <label>
                                Nueva contraseña
                                <input
                                    type="password"
                                    name="password"
                                    value={formEditar.password}
                                    onChange={handleEditarChange}
                                    placeholder="Dejar vacío para no cambiar"
                                />
                            </label>

                            <label>
                                Legajo
                                <input
                                    type="text"
                                    name="legajo"
                                    value={formEditar.legajo}
                                    onChange={handleEditarChange}
                                />
                            </label>

                            {usuarioEditando.rol === "chofer" && (
                                <>
                                    <label>
                                        Licencia
                                        <input
                                            type="text"
                                            name="licencia"
                                            value={formEditar.licencia}
                                            onChange={handleEditarChange}
                                        />
                                    </label>

                                    <label>
                                        Vencimiento licencia
                                        <input
                                            type="date"
                                            name="vencimientoLicencia"
                                            value={formEditar.vencimientoLicencia}
                                            onChange={handleEditarChange}
                                        />
                                    </label>
                                </>
                            )}

                            {usuarioEditando.rol === "mecanico" && (
                                <label>
                                    Especialidad
                                    <input
                                        type="text"
                                        name="especialidad"
                                        value={formEditar.especialidad}
                                        onChange={handleEditarChange}
                                    />
                                </label>
                            )}

                            {usuarioEditando.rol === "operador" && (
                                <label>
                                    Sector
                                    <input
                                        type="text"
                                        name="sector"
                                        value={formEditar.sector}
                                        onChange={handleEditarChange}
                                    />
                                </label>
                            )}

                            <div className="usuarios-modal__actions">
                                <button type="button" onClick={cerrarEditarUsuario}>
                                    Cancelar
                                </button>

                                <button type="submit">
                                    Guardar cambios
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </section>
    );
}

export default AdminUsuariosPage;