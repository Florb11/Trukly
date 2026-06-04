import "./NuevoCamionModal.css";

function NuevoCamionModal({ formNuevo, errorNuevo, onChange, onSubmit, onClose }) {
    return (
        <div className="nuevo-camion-backdrop">
            <div className="nuevo-camion-modal">
                <div className="nuevo-camion-header">
                    <div>
                        <span>Nuevo camión</span>
                        <h2>Registrar camión</h2>
                        <p>Completá los datos principales del vehículo.</p>
                    </div>

                    <button
                        type="button"
                        className="nuevo-camion-close"
                        onClick={onClose}
                    >
                        ×
                    </button>
                </div>

                <form className="nuevo-camion-form" onSubmit={onSubmit}>
                    {errorNuevo && (
                        <p className="nuevo-camion-error">{errorNuevo}</p>
                    )}

                    <div className="nuevo-camion-grid">
                        <div className="nuevo-camion-field">
                            <label htmlFor="matricula">Matrícula</label>
                            <input
                                type="text"
                                id="matricula"
                                name="matricula"
                                value={formNuevo.matricula}
                                onChange={onChange}
                                placeholder="Ej: ABC1234"
                            />
                        </div>

                        <div className="nuevo-camion-field">
                            <label htmlFor="marca">Marca</label>
                            <input
                                type="text"
                                id="marca"
                                name="marca"
                                value={formNuevo.marca}
                                onChange={onChange}
                                placeholder="Ej: Volvo"
                            />
                        </div>

                        <div className="nuevo-camion-field">
                            <label htmlFor="modelo">Modelo</label>
                            <input
                                type="text"
                                id="modelo"
                                name="modelo"
                                value={formNuevo.modelo}
                                onChange={onChange}
                                placeholder="Ej: FH"
                            />
                        </div>

                        <div className="nuevo-camion-field">
                            <label htmlFor="capacidad_carga">Capacidad de carga</label>
                            <input
                                type="number"
                                id="capacidad_carga"
                                name="capacidad_carga"
                                value={formNuevo.capacidad_carga}
                                onChange={onChange}
                                placeholder="Ej: 28000"
                            />
                        </div>

                        <div className="nuevo-camion-field">
                            <label htmlFor="estado">Estado</label>
                            <select
                                id="estado"
                                name="estado"
                                value={formNuevo.estado}
                                onChange={onChange}
                            >
                                <option value="disponible">Disponible</option>
                                <option value="en viaje">En viaje</option>
                                <option value="en mantenimiento">En mantenimiento</option>
                                <option value="inactivo">Inactivo</option>
                            </select>
                        </div>

                        <div className="nuevo-camion-field">
                            <label htmlFor="nroTanque">Nro. tanque</label>
                            <input
                                type="number"
                                id="nroTanque"
                                name="nroTanque"
                                value={formNuevo.nroTanque}
                                onChange={onChange}
                                placeholder="Ej: 1"
                            />
                        </div>
                    </div>

                    <div className="nuevo-camion-footer">
                        <button
                            type="button"
                            className="nuevo-camion-btn nuevo-camion-btn--cancelar"
                            onClick={onClose}
                        >
                            Cancelar
                        </button>

                        <button
                            type="submit"
                            className="nuevo-camion-btn nuevo-camion-btn--guardar"
                        >
                            Guardar camión
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default NuevoCamionModal;