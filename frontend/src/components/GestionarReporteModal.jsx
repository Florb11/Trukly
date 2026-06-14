import { useState, useEffect } from "react";
import "./GestionarReporteModal.css";
import { fetchConToken } from "../utils/fetchConToken";

function GestionarReporteModal({ reporte, onClose, onActualizado }) {
  const [mecanicos, setMecanicos] = useState([]);
  const [tab, setTab] = useState("estado");
  const [nuevoEstado, setNuevoEstado] = useState(reporte.estado || "pendiente");
  const [idMecanico, setIdMecanico] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    cargarMecanicos();
  }, []);

  const cargarMecanicos = async () => {
    try {
      const resultado = await fetchConToken("http://localhost:5000/api/operador/mecanicos", { method: "GET" });
      if (!resultado) return;
      const { respuesta, data } = resultado;
      if (!respuesta.ok) return;
      setMecanicos(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Error cargando mecánicos:", err);
    }
  };

  const guardarEstado = async () => {
    setError("");
    try {
      const resultado = await fetchConToken(
        `http://localhost:5000/api/reportes/${reporte.id_reporte}/estado`,
        {
          method: "PUT",
          body: JSON.stringify({ estado: nuevoEstado }),
        }
      );
      if (!resultado) return;
      const { respuesta, data } = resultado;
      if (!respuesta.ok) throw new Error(data.mensaje || "Error al cambiar estado");
      onActualizado();
    } catch (err) {
      setError(err.message);
    }
  };

  const asignarMecanico = async () => {
    if (!idMecanico) {
      setError("Seleccioná un mecánico.");
      return;
    }
    setError("");
    try {
      const resultado = await fetchConToken(
        `http://localhost:5000/api/reportes/${reporte.id_reporte}/asignar-mecanico`,
        {
          method: "PUT",
          body: JSON.stringify({ Mecanico_Usuario_idUsuario: Number(idMecanico) }),
        }
      );
      if (!resultado) return;
      const { respuesta, data } = resultado;
      if (!respuesta.ok) throw new Error(data.mensaje || "Error al asignar mecánico");
      onActualizado();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="gestionar-backdrop">
      <div className="gestionar-modal">
        <div className="gestionar-header">
          <div>
            <span>Gestionar reporte</span>
            <h2>Reporte #{reporte.id_reporte}</h2>
            <p>Estado actual: {reporte.estado}</p>
          </div>
          <button type="button" className="gestionar-close" onClick={onClose}>×</button>
        </div>

        <div className="gestionar-tabs">
          <button
            type="button"
            className={`gestionar-tab ${tab === "estado" ? "gestionar-tab--active" : ""}`}
            onClick={() => { setTab("estado"); setError(""); }}
          >
            Cambiar estado
          </button>
          <button
            type="button"
            className={`gestionar-tab ${tab === "mecanico" ? "gestionar-tab--active" : ""}`}
            onClick={() => { setTab("mecanico"); setError(""); }}
          >
            Asignar mecánico
          </button>
        </div>

        <div className="gestionar-body">
          {error && <p className="gestionar-error">⚠ {error}</p>}

          {tab === "estado" && (
            <div className="gestionar-field">
              <label>Nuevo estado</label>
              <select value={nuevoEstado} onChange={(e) => setNuevoEstado(e.target.value)}>
                {!reporte.Mecanico_Usuario_idUsuario && (
                  <option value="pendiente">Pendiente</option>
                )}
                <option value="en revision">En revisión</option>
                <option value="cancelado">Cancelado</option>
              </select>
            </div>
          )}

          {tab === "mecanico" && (
            <div className="gestionar-field">
              <label>Seleccioná un mecánico</label>
              <select value={idMecanico} onChange={(e) => setIdMecanico(e.target.value)}>
                <option value="">-- Elegir mecánico --</option>
                {mecanicos.map((m) => (
                  <option key={m.id_usuario} value={m.id_usuario}>
                    #{m.id_usuario} — {m.nombre} {m.apellido} ({m.especialidad})
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        <div className="gestionar-footer">
          <button type="button" className="gestionar-btn gestionar-btn--cancelar" onClick={onClose}>Cancelar</button>
          <button
            type="button"
            className="gestionar-btn gestionar-btn--guardar"
            onClick={tab === "estado" ? guardarEstado : asignarMecanico}
          >
            {tab === "estado" ? "Guardar estado" : "Asignar mecánico"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default GestionarReporteModal;