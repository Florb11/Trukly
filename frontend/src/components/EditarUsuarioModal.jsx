import "./EditarUsuarioModal.css"
import { useAuth } from "../context/AuthContext";

function EditarUsuarioModal({
    usuarioEditando,
    formEditar,
    errorEditar,
    onChange,
    onSubmit,
    onClose,
}) {
    const { usuario } = useAuth();
    const propiaCuenta = String(usuario?.id_usuario) === String(usuarioEditando.id_usuario);
    return (
        <div className="usuarios-modal-backdrop">
            <div className="usuarios-modal">
                <div className="usuarios-modal__header">
                    <div>
                        <span>Editar usuario</span>
                        <h2>{usuarioEditando.username}</h2>
                    </div>

                    <button type="button" onClick={onClose}>
                        ×
                    </button>
                </div>

                {errorEditar && (
                    <p className="usuarios-feedback usuarios-feedback--error">
                        {errorEditar}
                    </p>
                )}

                <form className="usuarios-form" onSubmit={onSubmit}>
                    <label>
                        Usuario
                        <input
                            type="text"
                            name="username"
                            maxLength={100}
                            value={formEditar.username}
                            onChange={onChange}
                        />
                    </label>

                    <label>
                        Email
                        <input
                            type="email"
                            name="email"
                            maxLength={150}
                            value={formEditar.email}
                            readOnly={Boolean(usuarioEditando.firebase_uid)}
                            onChange={onChange}
                        />
                        {usuarioEditando.firebase_uid && <small>El correo de acceso se cambia desde el perfil del usuario, con verificación.</small>}
                    </label>

                    <label>
                        Nombre
                        <input
                            type="text"
                            name="nombre"
                            maxLength={100}
                            value={formEditar.nombre}
                            onChange={onChange}
                        />
                    </label>

                    <label>
                        Apellido
                        <input
                            type="text"
                            name="apellido"
                            maxLength={100}
                            value={formEditar.apellido}
                            onChange={onChange}
                        />
                    </label>

                    <label>
                        Estado
                        <select
                            name="estado"
                            value={formEditar.estado}
                            disabled={propiaCuenta}
                            onChange={onChange}
                        >
                            <option value="pendiente">Pendiente</option>
                            <option value="activo">Activo</option>
                            <option value="inactivo">Inactivo</option>
                        </select>
                        {propiaCuenta && <small>Tu propia cuenta debe permanecer activa.</small>}
                    </label>

                    <label>
                        Legajo
                        <input
                            type="text"
                            name="legajo"
                        maxLength={formEditar.rol === "chofer" ? 50 : undefined}
                            value={formEditar.legajo}
                            onChange={onChange}
                        />
                    </label>

                    {usuarioEditando.rol === "chofer" && (
                        <>
                            <label>
                                Licencia
                                <input
                                    type="text"
                                    name="licencia"
                        maxLength={50}
                                    value={formEditar.licencia}
                                    onChange={onChange}
                                />
                            </label>

                            <label>
                                Vencimiento licencia
                                <input
                                    type="date"
                                    name="vencimientoLicencia"
                                    value={formEditar.vencimientoLicencia}
                                    onChange={onChange}
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
                                onChange={onChange}
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
                                onChange={onChange}
                            />
                        </label>
                    )}

                    <div className="usuarios-modal__actions">
                        <button type="button" onClick={onClose}>
                            Cancelar
                        </button>

                        <button type="submit">
                            Guardar cambios
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default EditarUsuarioModal;
