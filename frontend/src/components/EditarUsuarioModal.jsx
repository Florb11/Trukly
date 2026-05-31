import "./EditarUsuarioModal.css"

function EditarUsuarioModal({
    usuarioEditando,
    formEditar,
    errorEditar,
    onChange,
    onSubmit,
    onClose,
}) {
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
                            value={formEditar.username}
                            onChange={onChange}
                        />
                    </label>

                    <label>
                        Email
                        <input
                            type="email"
                            name="email"
                            value={formEditar.email}
                            onChange={onChange}
                        />
                    </label>

                    <label>
                        Nombre
                        <input
                            type="text"
                            name="nombre"
                            value={formEditar.nombre}
                            onChange={onChange}
                        />
                    </label>

                    <label>
                        Apellido
                        <input
                            type="text"
                            name="apellido"
                            value={formEditar.apellido}
                            onChange={onChange}
                        />
                    </label>

                    <label>
                        Estado
                        <select
                            name="estado"
                            value={formEditar.estado}
                            onChange={onChange}
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
                            onChange={onChange}
                            placeholder="Dejar vacío para no cambiar"
                        />
                    </label>

                    <label>
                        Legajo
                        <input
                            type="text"
                            name="legajo"
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