import { useState } from "react";
import "./EditarViajeModal.css";
import { fetchConToken } from "../utils/fetchConToken";

function EditarViajeModal({ viaje, onClose, onActualizado }) {
  const [form, setForm] = useState({
    origen: viaje.origen || "",
    destino: viaje.destino || "",
    fecha_salida: viaje.fecha_salida || "",
    fecha_llegada: viaje.fecha_llegada || "",
    Chofer_Usuario_idUsuario: viaje.Chofer_Usuario_idUsuario || "",
    Camion_id_camion: viaje.Camion_id_camion || "",
    recorrido: viaje.recorrido || "",
    observaciones: viaje.observaciones || "",
  });
  const [error, setError] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const guardar = async () => {
    if (!form.origen.trim() || !form.destino.trim() || !form.fecha_salida) {
      setError("Origen, destino y fecha de salida son obligatorios.");
      return;
    }
    setError("");
    try {
      const resultado = await fetchConToken(
        `http://localhost:5000/api/operador/viajes/${viaje.id_viaje}`,
        {
          method: "PUT",
          body: JSON.stringify({
            ...form,
            Chofer_Usuario_idUsuario: Number(form.Chofer_Usuario_idUsuario),
            Camion_id_camion: Number(form.Camion_id_camion),
            recorrido: Number(form.recorrido),
          }),
        }
      );
      if (!resultado) return;
      const { respuesta, data } = resultado;
      if (!respuesta.ok) throw new Error(data.mensaje || "Error al editar");
      onActualizado();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="editar-modal-backdrop">
      <div className="editar-modal" onClick={(e) => e.stopPropagation()}>
        <div className="editar-modal__header">
          <div>
            <p className="editar-modal__kicker">Editar operación</p>
            <h2>Viaje #{viaje.id_viaje}</h2>
          </div>
          <button className="editar-modal__close" onClick={onClose}>×</button>
        </div>

        <div className="editar-modal__body">
          {error && <p className="editar-modal__error">⚠ {error}</p>}

          <div className="editar-modal__row">
            <div className="editar-modal__field">
              <label>Origen</label>
              <input name="origen" value={form.origen} onChange={handleChange} placeholder="Ej: Buenos Aires" maxLength={45} />
            </div>
            <div className="editar-modal__field">
              <label>Destino</label>
              <input name="destino" value={form.destino} onChange={handleChange} placeholder="Ej: Rosario" maxLength={45} />
            </div>
          </div>

          <div className="editar-modal__row">
            <div className="editar-modal__field">
              <label>Fecha de salida</label>
              <input type="date" name="fecha_salida" value={form.fecha_salida} onChange={handleChange} />
            </div>
            <div className="editar-modal__field">
              <label>Fecha de llegada</label>
              <input type="date" name="fecha_llegada" value={form.fecha_llegada} onChange={handleChange} />
            </div>
          </div>

          <div className="editar-modal__row">
            <div className="editar-modal__field">
              <label>ID Chofer</label>
              <input type="number" name="Chofer_Usuario_idUsuario" value={form.Chofer_Usuario_idUsuario} onChange={handleChange} min="1" />
            </div>
            <div className="editar-modal__field">
              <label>ID Camión</label>
              <input type="number" name="Camion_id_camion" value={form.Camion_id_camion} onChange={handleChange} min="1" />
            </div>
          </div>

          <div className="editar-modal__field">
            <label>Recorrido (km)</label>
            <input type="number" name="recorrido" value={form.recorrido} onChange={handleChange} min="0" step="0.1" />
          </div>

          <div className="editar-modal__field">
            <label>Observaciones</label>
            <textarea name="observaciones" value={form.observaciones} onChange={handleChange} rows={3} maxLength={200} placeholder="Notas del viaje..." />
          </div>
        </div>

        <div className="editar-modal__footer">
          <button className="editar-modal__btn editar-modal__btn--cancelar" onClick={onClose}>Cancelar</button>
          <button className="editar-modal__btn editar-modal__btn--guardar" onClick={guardar}>Guardar cambios</button>
        </div>
      </div>
    </div>
  );
}

export default EditarViajeModal;