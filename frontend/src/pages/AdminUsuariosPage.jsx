import { useEffect, useState } from "react";
import { fetchConToken } from "../utils/fetchConToken";
import "./AdminUsuariosPage.css";
 
function AdminUsuariosPage() {
    const [usuarios, setUsuarios] = useState([]);
    const [cargandoUsuarios, setCargandoUsuarios] = useState(true);
    const [errorUsuarios, setErrorUsuarios] = useState("");
    const [mensajeUsuarios, setMensajeUsuarios] = useState("");
 
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
            <button type="button" className="btn-accion btn-accion--editar">
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
                        {/* Tabla — visible en desktop */}
                        <div className="usuarios-table-wrap">
                            <table className="usuarios-table">
                                <thead>
                                    <tr>
                                        <th>Usuario</th>
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
 
                        {/* Cards — visible en mobile */}
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
        </section>
    );
}
 
export default AdminUsuariosPage;