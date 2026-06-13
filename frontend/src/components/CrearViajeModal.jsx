import "./CrearViajeModal.css";

function CrearViajeModal({ form, error, onChange, onSubmit, onClose }) {
  return (
    <div className="viaje-modal-overlay" onClick={onClose}>
      <div className="viaje-modal" onClick={(e) => e.stopPropagation()}>
        <div className="viaje-modal__header">
          <div>
            <span>Operador logístico</span>
            <h2>Nuevo viaje</h2>
          </div>
          <button type="button" onClick={onClose} aria-label="Cerrar">✕</button>
        </div>

        <form className="viaje-modal__form" onSubmit={onSubmit}>
          <div className="viaje-modal__row">
            <div className="viaje-modal__field">
              <label htmlFor="origen">Origen</label>
              <input
                type="text"
                id="origen"
                name="origen"
                value={form.origen}
                onChange={onChange}
                placeholder="Ej: Buenos Aires"
                maxLength={45}
              />
            </div>
            <div className="viaje-modal__field">
              <label htmlFor="destino">Destino</label>
              <input
                type="text"
                id="destino"
                name="destino"
                value={form.destino}
                onChange={onChange}
                placeholder="Ej: Rosario"
                maxLength={45}
              />
            </div>
          </div>

          <div className="viaje-modal__row">
            <div className="viaje-modal__field">
              <label htmlFor="fecha_salida">Fecha de salida</label>
              <input
                type="date"
                id="fecha_salida"
                name="fecha_salida"
                value={form.fecha_salida}
                onChange={onChange}
              />
            </div>
            <div className="viaje-modal__field">
              <label htmlFor="fecha_llegada">Fecha de llegada</label>
              <input
                type="date"
                id="fecha_llegada"
                name="fecha_llegada"
                value={form.fecha_llegada}
                onChange={onChange}
              />
            </div>
          </div>

          <div className="viaje-modal__row">
            <div className="viaje-modal__field">
              <label htmlFor="Chofer_Usuario_idUsuario">ID del chofer</label>
              <input
                type="number"
                id="Chofer_Usuario_idUsuario"
                name="Chofer_Usuario_idUsuario"
                value={form.Chofer_Usuario_idUsuario}
                onChange={onChange}
                placeholder="Ej: 5"
                min="1"
              />
            </div>
            <div className="viaje-modal__field">
              <label htmlFor="Camion_id_camion">ID del camión</label>
              <input
                type="number"
                id="Camion_id_camion"
                name="Camion_id_camion"
                value={form.Camion_id_camion}
                onChange={onChange}
                placeholder="Ej: 3"
                min="1"
              />
            </div>
          </div>

          <div className="viaje-modal__field">
            <label htmlFor="recorrido">Recorrido (km)</label>
            <input
              type="number"
              id="recorrido"
              name="recorrido"
              value={form.recorrido}
              onChange={onChange}
              placeholder="Ej: 300"
              min="0"
              step="0.1"
            />
          </div>

          <div className="viaje-modal__field">
            <label htmlFor="observaciones">Observaciones</label>
            <textarea
              id="observaciones"
              name="observaciones"
              value={form.observaciones}
              onChange={onChange}
              placeholder="Indicaciones especiales, notas del viaje..."
              rows={3}
              maxLength={200}
            />
          </div>

          {error && <p className="viaje-modal__error">⚠ {error}</p>}

          <div className="viaje-modal__actions">
            <button type="button" className="viaje-modal__btn viaje-modal__btn--cancelar" onClick={onClose}>
              Cancelar
            </button>
            <button type="submit" className="viaje-modal__btn viaje-modal__btn--guardar">
              Crear viaje
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CrearViajeModal;