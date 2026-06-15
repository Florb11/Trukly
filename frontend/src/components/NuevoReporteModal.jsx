import { useState, useEffect } from "react";
import { fetchConToken } from "../utils/fetchConToken"; 
import "./NuevoReporteModal.css";

function NuevoReporteModal({
  formNuevo,
  errorNuevo,
  onChange,
  onSubmit,
  onClose,
}) {
  const [camiones, setCamiones] = useState([]);

useEffect(() => {
    fetchConToken("http://localhost:5000/api/choferes/camiones")
      .then(({ data }) => {
        console.log("respuesta camiones:", data);
        setCamiones(data.camiones || []);
      })
      .catch((err) => {
        console.log("error:", err);
        setCamiones([]);
      });
  }, []);
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
            <label htmlFor="id_camion">Camión</label>
            <select
              id="id_camion"
              name="id_camion"
              value={formNuevo.id_camion || ""}
              onChange={onChange}
              required
            >
              <option value="">Seleccioná un camión</option>
              {camiones.map((camion) => (
                <option key={camion.id_camion} value={camion.id_camion}>
                  Camión {camion.id_camion} — {camion.marca} {camion.modelo} ({camion.matricula})
                </option>
              ))}
            </select>
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