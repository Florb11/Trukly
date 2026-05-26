import { useEffect, useState } from "react";
import { fetchConToken } from "../utils/fetchConToken";
import "./DashboardAdminPage.css";

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
                {
                    method: "GET",
                }
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
                {
                    method: "PUT",
                }
            );

            if (!resultado) return;

            const { respuesta, data } = resultado;

            if (!respuesta.ok) {
                throw new Error(data.mensaje || data.msg || "Error al activar usuario");
            }

            setMensajeUsuarios(data.mensaje || "Usuario activado correctamente");

            setUsuarios((usuariosActuales) =>
                usuariosActuales.map((usuario) =>
                    usuario.id_usuario === idUsuario
                        ? { ...usuario, estado: "activo" }
                        : usuario
                )
            );
        } catch (error) {
            setErrorUsuarios(error.message);
        }
    };

    useEffect(() => {
        cargarUsuarios();
    }, []);

    const desactivarUsuario = async (idUsuario) => {
        try {
            setMensajeUsuarios("");
            setErrorUsuarios("");

            const resultado = await fetchConToken(
                `http://localhost:5000/api/admin/usuarios/${idUsuario}/desactivar`,
                {
                    method: "PUT",
                }
            );

            if (!resultado) return;

            const { respuesta, data } = resultado;

            if (!respuesta.ok) {
                throw new Error(
                    data.mensaje || data.msg || "Error al desactivar usuario"
                );
            }

            setMensajeUsuarios(data.mensaje || "Usuario desactivado correctamente");

            setUsuarios((usuariosActuales) =>
                usuariosActuales.map((usuario) =>
                    usuario.id_usuario === idUsuario
                        ? { ...usuario, estado: "inactivo" }
                        : usuario
                )
            );
        } catch (error) {
            setErrorUsuarios(error.message);
        }
    };

    return (
        <section className="admin-dashboard">
            <div className="admin-dashboard__heading">
                <div>
                    <span>Administración</span>
                    <h1>Gestión de usuarios</h1>
                </div>

                <button type="button">Nuevo usuario</button>
            </div>

            <article className="admin-card">
                <div className="admin-card__header">
                    <h2>Usuarios del sistema</h2>
                    <span>Administrá cuentas y roles</span>
                </div>

                {mensajeUsuarios && (
                    <p className="admin-message admin-message--ok">{mensajeUsuarios}</p>
                )}

                {cargandoUsuarios ? (
                    <p className="admin-message">Cargando usuarios...</p>
                ) : errorUsuarios ? (
                    <p className="admin-message admin-message--error">{errorUsuarios}</p>
                ) : usuarios.length === 0 ? (
                    <p className="admin-message">No hay usuarios registrados.</p>
                ) : (
                    <div className="admin-table-wrap">
                        <table className="admin-table">
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
                                            <span
                                                className={
                                                    usuario.estado === "activo"
                                                        ? "admin-badge admin-badge--ok"
                                                        : "admin-badge admin-badge--warn"
                                                }
                                            >
                                                {usuario.estado}
                                            </span>
                                        </td>

                                        <td>
                                            {usuario.rol === "chofer" && (
                                                <span>Licencia: {usuario.licencia || "-"}</span>
                                            )}

                                            {usuario.rol === "mecanico" && (
                                                <span>Especialidad: {usuario.especialidad || "-"}</span>
                                            )}

                                            {usuario.rol === "operador" && (
                                                <span>Sector: {usuario.sector || "-"}</span>
                                            )}

                                            {usuario.rol === "admin" && (
                                                <span>Legajo: {usuario.legajo || "-"}</span>
                                            )}
                                        </td>

                                        <td>
                                            <div className="admin-actions">
                                                {(usuario.estado === "pendiente" ||
                                                    usuario.estado === "inactivo") && (
                                                    <button
                                                        type="button"
                                                        className="admin-table__action"
                                                        onClick={() => activarUsuario(usuario.id_usuario)}
                                                    >
                                                        Activar
                                                    </button>
                                                )}

                                                {usuario.estado === "activo" && (
                                                    <button
                                                        type="button"
                                                        className="admin-table__action"
                                                        onClick={() => desactivarUsuario(usuario.id_usuario)}
                                                    >
                                                        Desactivar
                                                    </button>
                                                )}

                                                <button type="button" className="admin-table__action">
                                                    Editar
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
        </section>
    );
}

export default AdminUsuariosPage;