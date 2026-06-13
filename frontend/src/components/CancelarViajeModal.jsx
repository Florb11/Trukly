import { useState } from "react";
import "./CancelarViajeModal.css";
import { fetchConToken } from "../utils/fetchConToken";

function CancelarViajeModal({ viaje, onClose, onActualizado }) {
  const [motivo, setMotivo] = useState("");
  const [error, setError] = useState("");

  const confirmar = async () => {
    if (!motivo.trim()) {
      setError("El motivo es obligatorio.");
      return;
    }
    setError("");
    try {
      const resultado = await fetchConToken(
        `http://localhost:5000/api/operador/viajes/${viaje.id_viaje}/cancelar`,
        {
          method: "PUT",
          body: JSON.stringify({ motivo }),
        }
      );
      if (!resultado) return;
      const { respuesta, data } = resultado;
      if (!respuesta.ok) throw new Error(data.mensaje || "Error al cancelar");
      onActualizado();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="cancelar-modal-backdrop">
      <div className="cancelar-modal" onClick={(e) => e.stopPropagation()}>
        <div className="cancelar-modal__header">
          <div>
            <p className="cancelar-modal__kicker">Cancelar operación</p>
            <h2>Viaje #{viaje.id_viaje}</h2>
          </div>
          <button className="cancelar-modal__close" onClick={onClose}>×</button>
        </div>

        <div className="cancelar-modal__body">
          <p className="cancelar-modal__aviso">
            Esta acción no se puede deshacer. El viaje quedará cancelado.
          </p>

          {error && <p className="cancelar-modal__error">⚠ {error}</p>}

          <div className="cancelar-modal__field">
            <label>Motivo de cancelación</label>
            <textarea
              rows={4}
              value={motivo}
              onChange={(e) => setMotivo(e.target.value)}
              placeholder="Explicá el motivo de la cancelación..."
            />
          </div>
        </div>

        <div className="cancelar-modal__footer">
          <button className="cancelar-modal__btn cancelar-modal__btn--volver" onClick={onClose}>Volver</button>
          <button className="cancelar-modal__btn cancelar-modal__btn--confirmar" onClick={confirmar}>Confirmar cancelación</button>
        </div>
      </div>
    </div>
  );
}

export default CancelarViajeModal;