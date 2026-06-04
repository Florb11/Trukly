import "./DetalleCamionModal.css";

function DetalleCamionModal({ camion, onClose }) {
    if (!camion) return null;

    return (
        <div className="detalle-camion-backdrop">
            <div className="detalle-camion-modal">
                <div className="detalle-camion-header">
                    <div>
                        <span>Detalle de camión</span>
                        <h2>
                            {camion.marca} {camion.modelo}
                        </h2>
                        <p>
                            #{camion.id_camion} · {camion.matricula}
                        </p>
                    </div>

                    <button
                        type="button"
                        className="detalle-camion-close"
                        onClick={onClose}
                    >
                        ×
                    </button>
                </div>

                <div className="detalle-camion-body">
                    <div className="detalle-camion-grid">
                        <div className="detalle-camion-item">
                            <span>ID</span>
                            <p>#{camion.id_camion}</p>
                        </div>

                        <div className="detalle-camion-item">
                            <span>Matrícula</span>
                            <p>{camion.matricula}</p>
                        </div>

                        <div className="detalle-camion-item">
                            <span>Marca</span>
                            <p>{camion.marca}</p>
                        </div>

                        <div className="detalle-camion-item">
                            <span>Modelo</span>
                            <p>{camion.modelo}</p>
                        </div>

                        <div className="detalle-camion-item">
                            <span>Capacidad de carga</span>
                            <p>{camion.capacidad_carga} kg</p>
                        </div>

                        <div className="detalle-camion-item">
                            <span>Estado</span>
                            <p>{camion.estado}</p>
                        </div>

                        <div className="detalle-camion-item">
                            <span>Nro. tanque</span>
                            <p>{camion.nroTanque}</p>
                        </div>
                    </div>
                </div>

                <div className="detalle-camion-footer">
                    <button
                        type="button"
                        className="detalle-camion-btn"
                        onClick={onClose}
                    >
                        Cerrar
                    </button>
                </div>
            </div>
        </div>
    );
}

export default DetalleCamionModal;