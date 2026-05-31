import "./DetalleUsuarioModal.css";

function DetalleUsuarioModal({ usuario, onClose }) {
  if (!usuario) return null;

  return (
    <div className="detalle-modal-backdrop">
      <div className="detalle-modal">
        <div className="detalle-modal-header">
          <div>
            <p className="detalle-modal-kicker">Detalle de usuario</p>
            <h2>
              {usuario.nombre} {usuario.apellido}
            </h2>
          </div>

          <button className="detalle-modal-close" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="detalle-modal-body">
          <div className="detalle-section">
            <h3>Datos generales</h3>

            <div className="detalle-grid">
              <div>
                <span>Usuario</span>
                <p>{usuario.username}</p>
              </div>

              <div>
                <span>Email</span>
                <p>{usuario.email}</p>
              </div>

              <div>
                <span>Nombre</span>
                <p>{usuario.nombre}</p>
              </div>

              <div>
                <span>Apellido</span>
                <p>{usuario.apellido}</p>
              </div>

              <div>
                <span>Rol</span>
                <p>{usuario.rol}</p>
              </div>

              <div>
                <span>Estado</span>
                <p>{usuario.estado}</p>
              </div>
            </div>
          </div>

          <div className="detalle-section">
            <h3>Datos específicos</h3>

            <div className="detalle-grid">
              {usuario.legajo && (
                <div>
                  <span>Legajo</span>
                  <p>{usuario.legajo}</p>
                </div>
              )}

              {usuario.licencia && (
                <div>
                  <span>Licencia</span>
                  <p>{usuario.licencia}</p>
                </div>
              )}

              {usuario.vencimientoLicencia && (
                <div>
                  <span>Vencimiento de licencia</span>
                  <p>{usuario.vencimientoLicencia}</p>
                </div>
              )}

              {usuario.especialidad && (
                <div>
                  <span>Especialidad</span>
                  <p>{usuario.especialidad}</p>
                </div>
              )}

              {usuario.sector && (
                <div>
                  <span>Sector</span>
                  <p>{usuario.sector}</p>
                </div>
              )}
            </div>

            {!usuario.legajo &&
              !usuario.licencia &&
              !usuario.vencimientoLicencia &&
              !usuario.especialidad &&
              !usuario.sector && (
                <p className="detalle-empty">
                  Este usuario no tiene datos específicos cargados.
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

export default DetalleUsuarioModal;