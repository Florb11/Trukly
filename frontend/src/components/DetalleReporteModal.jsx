import "./DetalleReporteModal.css";

function DetalleReporteModal({ reporte, onClose }) {
    if (!reporte) return null;

    return (
        <div className="detalle-reporte-backdrop">
            <div className="detalle-reporte-modal">
                <div className="detalle-reporte-header">
                    <div>
                        <span>Detalle de reporte</span>
                        <h2>Reporte #{reporte.id_reporte}</h2>
                        <p>{reporte.fecha_hora}</p>
                    </div>

                    <button
                        type="button"
                        className="detalle-reporte-close"
                        onClick={onClose}
                    >
                        ×
                    </button>
                </div>

                <div className="detalle-reporte-body">
                    <div className="detalle-reporte-section">
                        <h3>Datos del reporte</h3>

                        <div className="detalle-reporte-grid">
                            <div className="detalle-reporte-item">
                                <span>ID</span>
                                <p>#{reporte.id_reporte}</p>
                            </div>

                            <div className="detalle-reporte-item">
                                <span>Fecha y hora</span>
                                <p>{reporte.fecha_hora}</p>
                            </div>

                            <div className="detalle-reporte-item">
                                <span>Estado</span>
                                <p>{reporte.estado}</p>
                            </div>

                            <div className="detalle-reporte-item">
                                <span>Camión</span>
                                <p>#{reporte.Camion_id_camion}</p>
                            </div>

                            <div className="detalle-reporte-item">
                                <span>Chofer</span>
                                <p>#{reporte.Chofer_Usuario_idUsuario}</p>
                            </div>

                            <div className="detalle-reporte-item">
                                <span>Mecánico</span>
                                <p>
                                    {reporte.Mecanico_Usuario_idUsuario
                                        ? `#${reporte.Mecanico_Usuario_idUsuario}`
                                        : "Sin asignar"}
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="detalle-reporte-section">
                        <h3>Descripción de la falla</h3>

                        <div className="detalle-reporte-description">
                            <p>{reporte.descripcion}</p>
                        </div>
                    </div>
                </div>

                <div className="detalle-reporte-footer">
                    <button
                        type="button"
                        className="detalle-reporte-btn"
                        onClick={onClose}
                    >
                        Cerrar
                    </button>
                </div>
            </div>
        </div>
    );
}

export default DetalleReporteModal;