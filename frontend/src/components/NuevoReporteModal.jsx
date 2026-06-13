import "./NuevoReporteModal.css";

function NuevoReporteModal({
  formNuevo,
  errorNuevo,
  onChange,
  onSubmit,
  onClose,
}) {
  return (
    <div className="reporte-modal-overlay" onClick={onClose}>
      <div className="reporte-modal" onClick={(e) => e.stopPropagation()}>
        <div className="reporte-modal__header">
          <h2>Nuevo reporte de falla</h2>
          <button
            type="button"
            className="reporte-modal__close"
            onClick={onClose}
            aria-label="Cerrar"
          >
            ✕
          </button>
        </div>

        <form className="reporte-modal__form" onSubmit={onSubmit}>
          
   
          <div className="reporte-modal__field">
            <label htmlFor="id_camion">ID del camión</label>
            <input
              type="number"
              id="id_camion"
              name="id_camion"
              value={formNuevo.id_camion || ""}
              onChange={onChange}
              placeholder="Ej: 3"
              min="1"
              required
            />
          </div>

          <div className="reporte-modal__field">
            <label htmlFor="descripcion">Descripción de la falla</label>
            <textarea
              id="descripcion"
              name="descripcion"
              value={formNuevo.descripcion || ""}
              onChange={onChange}
              placeholder="Describí la falla con el mayor detalle posible..."
              rows={4}
              required
            />
          </div>

          {errorNuevo && <p className="reporte-modal__error">⚠ {errorNuevo}</p>}

          <div className="reporte-modal__actions">
            <button
              type="button"
              className="reporte-modal__btn reporte-modal__btn--cancelar"
              onClick={onClose}
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="reporte-modal__btn reporte-modal__btn--guardar"
            >
              Enviar reporte
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default NuevoReporteModal;