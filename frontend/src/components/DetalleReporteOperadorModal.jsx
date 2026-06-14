import "./DetalleReporteOperadorModal.css";

function DetalleReporteOperadorModal({ reporte, onClose }) {
  if (!reporte) return null;

  return (
    <div className="det-rep-backdrop">
      <div className="det-rep-modal">
        <div className="det-rep-header">
          <div>
            <span>Detalle de reporte</span>
            <h2>Reporte #{reporte.id_reporte}</h2>
            <p>{reporte.fecha_hora}</p>
          </div>
          <button type="button" className="det-rep-close" onClick={onClose}>×</button>
        </div>

        <div className="det-rep-body">
          <div className="det-rep-section">
            <h3>Datos del reporte</h3>
            <div className="det-rep-grid">
              <div><span>ID</span><p>#{reporte.id_reporte}</p></div>
              <div><span>Fecha y hora</span><p>{reporte.fecha_hora}</p></div>
              <div><span>Estado</span><p>{reporte.estado}</p></div>
              <div><span>Camión</span><p>#{reporte.Camion_id_camion}</p></div>
              <div><span>Chofer</span><p>#{reporte.Chofer_Usuario_idUsuario}</p></div>
              <div>
                <span>Mecánico</span>
                <p>{reporte.Mecanico_Usuario_idUsuario ? `#${reporte.Mecanico_Usuario_idUsuario}` : "Sin asignar"}</p>
              </div>
            </div>
          </div>

          <div className="det-rep-section">
            <h3>Descripción de la falla</h3>
            <div className="det-rep-description"><p>{reporte.descripcion}</p></div>
          </div>

          {reporte.nota_reparacion && (
            <div className="det-rep-section">
              <h3>Nota de reparación</h3>
              <div className="det-rep-description"><p>{reporte.nota_reparacion}</p></div>
            </div>
          )}
        </div>

        <div className="det-rep-footer">
          <button type="button" className="det-rep-btn" onClick={onClose}>Cerrar</button>
        </div>
      </div>
    </div>
  );
}

export default DetalleReporteOperadorModal;