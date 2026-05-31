import "./NuevoUsuarioModal.css";
function NuevoUsuarioModal({
    formNuevo,
    errorNuevo,
    onChange,
    onSubmit,
    onClose,
}) {
    return (
        <div className="usuarios-modal-backdrop">
            <div className="usuarios-modal">
                <div className="usuarios-modal__header">
                    <div>
                        <span>Nuevo usuario</span>
                        <h2>Registrar usuario</h2>
                    </div>

                    <button type="button" onClick={onClose}>
                        ×
                    </button>
                </div>

                {errorNuevo && (
                    <p className="usuarios-feedback usuarios-feedback--error">
                        {errorNuevo}
                    </p>
                )}

                <form className="usuarios-form" onSubmit={onSubmit}>
                    <label>
                        Rol
                        <select
                            name="rol"
                            value={formNuevo.rol}
                            onChange={onChange}
                        >
                            <option value="admin">Administrador</option>
                            <option value="chofer">Chofer</option>
                            <option value="mecanico">Mecánico</option>
                            <option value="operador">Operador</option>
                        </select>
                    </label>

                    <label>
                        Usuario
                        <input
                            type="text"
                            name="username"
                            value={formNuevo.username}
                            onChange={onChange}
                        />
                    </label>

                    <label>
                        Email
                        <input
                            type="email"
                            name="email"
                            value={formNuevo.email}
                            onChange={onChange}
                        />
                    </label>

                    <label>
                        Contraseña
                        <input
                            type="password"
                            name="password"
                            value={formNuevo.password}
                            onChange={onChange}
                        />
                    </label>

                    <label>
                        Nombre
                        <input
                            type="text"
                            name="nombre"
                            value={formNuevo.nombre}
                            onChange={onChange}
                        />
                    </label>

                    <label>
                        Apellido
                        <input
                            type="text"
                            name="apellido"
                            value={formNuevo.apellido}
                            onChange={onChange}
                        />
                    </label>

                    <label>
                        Estado
                        <select
                            name="estado"
                            value={formNuevo.estado}
                            onChange={onChange}
                        >
                            <option value="activo">Activo</option>
                            <option value="pendiente">Pendiente</option>
                            <option value="inactivo">Inactivo</option>
                        </select>
                    </label>

                    <label>
                        Legajo
                        <input
                            type="text"
                            name="legajo"
                            value={formNuevo.legajo}
                            onChange={onChange}
                        />
                    </label>

                    {formNuevo.rol === "chofer" && (
                        <>
                            <label>
                                Licencia
                                <input
                                    type="text"
                                    name="licencia"
                                    value={formNuevo.licencia}
                                    onChange={onChange}
                                />
                            </label>

                            <label>
                                Vencimiento licencia
                                <input
                                    type="date"
                                    name="vencimientoLicencia"
                                    value={formNuevo.vencimientoLicencia}
                                    onChange={onChange}
                                />
                            </label>
                        </>
                    )}

                    {formNuevo.rol === "mecanico" && (
                        <label>
                            Especialidad
                            <input
                                type="text"
                                name="especialidad"
                                value={formNuevo.especialidad}
                                onChange={onChange}
                            />
                        </label>
                    )}

                    {formNuevo.rol === "operador" && (
                        <label>
                            Sector
                            <input
                                type="text"
                                name="sector"
                                value={formNuevo.sector}
                                onChange={onChange}
                            />
                        </label>
                    )}

                    <div className="usuarios-modal__actions">
                        <button type="button" onClick={onClose}>
                            Cancelar
                        </button>

                        <button type="submit">
                            Registrar usuario
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default NuevoUsuarioModal;