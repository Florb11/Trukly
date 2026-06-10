import "./CambiarEstadoReporteModal.css";

function CambiarEstadoReporteModal({
    reporte,
    nuevoEstado,
    errorEstado,
    onChange,
    onSubmit,
    onClose,
}) {
    if (!reporte) return null;

    const tieneMecanicoAsignado = Boolean(
        reporte.Mecanico_Usuario_idUsuario
    );

    return (
        <div className="cambiar-estado-reporte-backdrop">
            <div className="cambiar-estado-reporte-modal">
                <div className="cambiar-estado-reporte-header">
                    <div>
                        <span>Cambiar estado</span>
                        <h2>Reporte #{reporte.id_reporte}</h2>
                        <p>Estado actual: {reporte.estado}</p>
                    </div>

                    <button
                        type="button"
                        className="cambiar-estado-reporte-close"
                        onClick={onClose}
                    >
                        ×
                    </button>
                </div>

                <form className="cambiar-estado-reporte-form" onSubmit={onSubmit}>
                    {errorEstado && (
                        <p className="cambiar-estado-reporte-error">{errorEstado}</p>
                    )}

                    <div className="cambiar-estado-reporte-field">
                        <label htmlFor="nuevoEstadoReporte">Nuevo estado</label>
                        <select
                            id="nuevoEstadoReporte"
                            value={nuevoEstado}
                            onChange={onChange}
                        >
                            {!tieneMecanicoAsignado && (
                                <option value="pendiente">Pendiente</option>
                            )}
                            <option value="en revision">En revisión</option>
                            <option value="cancelado">Cancelado</option>
                        </select>
                    </div>

                    <div className="cambiar-estado-reporte-footer">
                        <button
                            type="button"
                            className="cambiar-estado-reporte-btn cambiar-estado-reporte-btn--cancelar"
                            onClick={onClose}
                        >
                            Cancelar
                        </button>

                        <button
                            type="submit"
                            className="cambiar-estado-reporte-btn cambiar-estado-reporte-btn--guardar"
                        >
                            Guardar estado
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default CambiarEstadoReporteModal;
