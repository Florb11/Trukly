import "./DetalleViajeModal.css";

function DetalleViajeModal({ viaje, onClose }) {
  if (!viaje) return null;

  const formatearFecha = (fechaISO) => {
    if (!fechaISO) return "-";
    const [year, month, day] = fechaISO.split("-");
    return `${day}/${month}/${year}`;
  };

  return (
    <div className="detalle-modal-backdrop">
      <div className="detalle-modal">
        <div className="detalle-modal-header">
          <div>
            <p className="detalle-modal-kicker">Detalle de operación</p>
            <h2>Viaje #{viaje.id_viaje}</h2>
          </div>

          <button className="detalle-modal-close" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="detalle-modal-body">
          <div className="detalle-section">
            <h3>Ruta y Tiempos</h3>

            <div className="detalle-grid">
              <div>
                <span>Origen</span>
                <p>{viaje.origen}</p>
              </div>

              <div>
                <span>Destino</span>
                <p>{viaje.destino}</p>
              </div>

              <div>
                <span>Distancia / Recorrido</span>
                <p>{viaje.recorrido} km</p>
              </div>

              <div>
                <span>Estado</span>
                <p>{viaje.estado}</p>
              </div>

              <div>
                <span>Fecha de Salida</span>
                <p>{formatearFecha(viaje.fecha_salida)}</p>
              </div>

              <div>
                <span>Fecha de Llegada</span>
                <p>
                  {viaje.fecha_llegada
                    ? formatearFecha(viaje.fecha_llegada)
                    : "Pendiente"}
                </p>
              </div>
            </div>
          </div>

          <div className="detalle-section">
            <h3>Asignaciones Logísticas</h3>

            <div className="detalle-grid">
              <div>
                <span>ID Chofer asignado</span>
                <p>#{viaje.Chofer_Usuario_idUsuario}</p>
              </div>

              <div>
                <span>ID Camión asignado</span>
                <p>#{viaje.Camion_id_camion}</p>
              </div>

              <div>
                <span>ID Operador responsable</span>
                <p>#{viaje.OperadorLogistico_Usuario_idUsuario}</p>
              </div>
            </div>
          </div>

          <div className="detalle-section">
            <h3>Observaciones</h3>
            {viaje.observaciones ? (
              <p style={{ marginTop: "8px", lineHeight: "1.5" }}>
                {viaje.observaciones}
              </p>
            ) : (
              <p className="detalle-empty">
                Este viaje no tiene observaciones registradas.
              </p>
            )}
          </div>
        </div>

        <div className="detalle-modal-footer">
          <button className="detalle-btn-cerrar" onClick={onClose}>
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
}

export default DetalleViajeModal;
