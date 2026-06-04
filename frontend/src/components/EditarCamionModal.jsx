import "./EditarCamionModal.css";

function EditarCamionModal({
    camionEditando,
    formEditar,
    errorEditar,
    onChange,
    onSubmit,
    onClose,
}) {
    if (!camionEditando) return null;

    return (
        <div className="editar-camion-backdrop">
            <div className="editar-camion-modal">
                <div className="editar-camion-header">
                    <div>
                        <span>Editar camión</span>
                        <h2>
                            {camionEditando.marca} {camionEditando.modelo}
                        </h2>
                        <p>
                            #{camionEditando.id_camion} · {camionEditando.matricula}
                        </p>
                    </div>

                    <button
                        type="button"
                        className="editar-camion-close"
                        onClick={onClose}
                    >
                        ×
                    </button>
                </div>

                <form className="editar-camion-form" onSubmit={onSubmit}>
                    {errorEditar && (
                        <p className="editar-camion-error">{errorEditar}</p>
                    )}

                    <div className="editar-camion-grid">
                        <div className="editar-camion-field">
                            <label htmlFor="editar-matricula">Matrícula</label>
                            <input
                                type="text"
                                id="editar-matricula"
                                name="matricula"
                                value={formEditar.matricula}
                                onChange={onChange}
                            />
                        </div>

                        <div className="editar-camion-field">
                            <label htmlFor="editar-marca">Marca</label>
                            <input
                                type="text"
                                id="editar-marca"
                                name="marca"
                                value={formEditar.marca}
                                onChange={onChange}
                            />
                        </div>

                        <div className="editar-camion-field">
                            <label htmlFor="editar-modelo">Modelo</label>
                            <input
                                type="text"
                                id="editar-modelo"
                                name="modelo"
                                value={formEditar.modelo}
                                onChange={onChange}
                            />
                        </div>

                        <div className="editar-camion-field">
                            <label htmlFor="editar-capacidad">Capacidad de carga</label>
                            <input
                                type="number"
                                id="editar-capacidad"
                                name="capacidad_carga"
                                value={formEditar.capacidad_carga}
                                onChange={onChange}
                            />
                        </div>

                        <div className="editar-camion-field">
                            <label htmlFor="editar-estado">Estado</label>
                            <select
                                id="editar-estado"
                                name="estado"
                                value={formEditar.estado}
                                onChange={onChange}
                            >
                                <option value="disponible">Disponible</option>
                                <option value="en viaje">En viaje</option>
                                <option value="en mantenimiento">En mantenimiento</option>
                                <option value="inactivo">Inactivo</option>
                            </select>
                        </div>

                        <div className="editar-camion-field">
                            <label htmlFor="editar-nroTanque">Nro. tanque</label>
                            <input
                                type="number"
                                id="editar-nroTanque"
                                name="nroTanque"
                                value={formEditar.nroTanque}
                                onChange={onChange}
                            />
                        </div>
                    </div>

                    <div className="editar-camion-footer">
                        <button
                            type="button"
                            className="editar-camion-btn editar-camion-btn--cancelar"
                            onClick={onClose}
                        >
                            Cancelar
                        </button>

                        <button
                            type="submit"
                            className="editar-camion-btn editar-camion-btn--guardar"
                        >
                            Guardar cambios
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default EditarCamionModal;