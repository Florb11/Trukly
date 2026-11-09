import { useState, useEffect } from "react";
import { fetchConToken } from "../utils/fetchConToken";
import "./NuevoReporteModal.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

function NuevoReporteModal({ onCreated, onClose }) {
  const [viajeActivo, setViajeActivo] = useState(null);
  const [cargandoViaje, setCargandoViaje] = useState(true);
  const [descripcion, setDescripcion] = useState("");
  const [errorNuevo, setErrorNuevo] = useState("");
  const [guardando, setGuardando] = useState(false);

  useEffect(() => {
    const controlador = new AbortController();
    const { signal } = controlador;
    const mensajeError = "No pudimos consultar tu viaje en curso. Volvé a abrir el formulario para reintentar.";

    const cargarViaje = async () => {
      try {
        const resultado = await fetchConToken(`${API_URL}/api/choferes/mis-viajes`, { signal });
        if (!resultado || signal.aborted) return;

        const { respuesta, data } = resultado;
        if (!respuesta.ok || !Array.isArray(data)) {
          setErrorNuevo(mensajeError);
          return;
        }

        const viaje = data.find(
          (v) => v.estado?.toLowerCase() === "en curso" && v.Camion_id_camion > 0,
        );
        setViajeActivo(viaje ?? null);
      } catch {
        if (!signal.aborted) setErrorNuevo(mensajeError);
      } finally {
        if (!signal.aborted) setCargandoViaje(false);
      }
    };

    cargarViaje();
    return () => controlador.abort();
  }, []);

  const guardarReporte = async (e) => {
    e.preventDefault();
    if (!viajeActivo || guardando) return;

    const texto = descripcion.trim();
    if (!texto) {
      setErrorNuevo("La descripción es obligatoria.");
      return;
    }

    setGuardando(true);
    setErrorNuevo("");
    try {
      const resultado = await fetchConToken(`${API_URL}/api/reportes`, {
        method: "POST",
        body: JSON.stringify({
          descripcion: texto,
          Camion_id_camion: viajeActivo.Camion_id_camion,
        }),
      });
      if (!resultado) return;
      if (resultado.respuesta.ok) {
        onCreated();
      } else {
        setErrorNuevo(resultado.data?.mensaje || "No se pudo crear el reporte.");
      }
    } catch {
      setErrorNuevo("No se pudo crear el reporte.");
    } finally {
      setGuardando(false);
    }
  };

  return (
    <div className="reporte-modal-overlay" onClick={guardando ? undefined : onClose}>
      <div className="reporte-modal" onClick={(e) => e.stopPropagation()}>
        <div className="reporte-modal__header">
          <h2>Nuevo reporte de falla</h2>
          <button
            type="button"
            className="reporte-modal__close"
            onClick={onClose}
            disabled={guardando}
            aria-label="Cerrar"
          >
            ✕
          </button>
        </div>

        <form className="reporte-modal__form" onSubmit={guardarReporte}>
          {cargandoViaje && <span role="status">Buscando tu viaje en curso…</span>}
          {!cargandoViaje && !viajeActivo && !errorNuevo && (
            <span role="status">Necesitás un viaje en curso con un camión asignado para reportar una falla.</span>
          )}
          {viajeActivo && (
            <>
              <div className="reporte-modal__field">
                <label htmlFor="camion_asignado">Camión asignado</label>
                <input
                  id="camion_asignado"
                  value={viajeActivo.camion_nombre || `Camión #${viajeActivo.Camion_id_camion}`}
                  readOnly
                />
              </div>

              <div className="reporte-modal__field">
                <label htmlFor="descripcion">Descripción de la falla</label>
                <textarea
                  id="descripcion"
                  maxLength={200}
                  value={descripcion}
                  onChange={(e) => setDescripcion(e.target.value)}
                  placeholder="Describí la falla con el mayor detalle posible..."
                  rows={4}
                  required
                  disabled={guardando}
                />
              </div>
            </>
          )}

          {errorNuevo && <p className="reporte-modal__error" role="alert">{errorNuevo}</p>}

          <div className="reporte-modal__actions">
            <button
              type="button"
              className="reporte-modal__btn reporte-modal__btn--cancelar"
              onClick={onClose}
              disabled={guardando}
            >
              Cancelar
            </button>
            {viajeActivo && (
              <button
                type="submit"
                className="reporte-modal__btn reporte-modal__btn--guardar"
                disabled={guardando}
              >
                {guardando ? "Enviando…" : "Enviar reporte"}
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}

export default NuevoReporteModal;
