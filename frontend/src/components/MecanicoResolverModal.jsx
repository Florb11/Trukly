import { FaCheckCircle, FaTimes } from "react-icons/fa";
import "./MecanicoResolverModal.css";

function MecanicoResolverModal({
  reporte,
  notaReparacion,
  setNotaReparacion,
  resolviendo,
  onClose,
  onSubmit,
}) {
  if (!reporte) return null;

  return (
    <div className="mecanico-modal-overlay">
      <div className="mecanico-modal">
        <div className="mecanico-modal__header">
          <div>
            <span>Resolver reporte</span>
            <h2>Reporte #{reporte.id_reporte}</h2>
          </div>

          <button
            type="button"
            className="mecanico-modal__close"
            onClick={onClose}
            disabled={resolviendo}
          >
            <FaTimes />
          </button>
        </div>

        <p className="mecanico-modal__description">{reporte.descripcion}</p>

        <form onSubmit={onSubmit} className="mecanico-modal__form">
          <label>
            <span>Nota de reparación</span>
            <textarea
              value={notaReparacion}
              onChange={(e) => setNotaReparacion(e.target.value)}
              placeholder="Ej: Se revisó el sistema de frenos y se cambió una manguera dañada."
              rows="5"
            />
          </label>

          <div className="mecanico-modal__actions">
            <button
              type="button"
              className="mecanico-btn-secondary"
              onClick={onClose}
              disabled={resolviendo}
            >
              Cancelar
            </button>

            <button
              type="submit"
              className="mecanico-action-btn"
              disabled={resolviendo}
            >
              <FaCheckCircle />
              {resolviendo ? "Guardando..." : "Confirmar resolución"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default MecanicoResolverModal;