import { useEffect, useState } from "react";
import { fetchConToken } from "../utils/fetchConToken";
import "./DetalleViajeModal.css";

function DetalleViajeModal({ viaje: viajeInicial, onClose }) {
  const [detalle, setDetalle] = useState(null);
  const [errorAsignaciones, setErrorAsignaciones] = useState("");
  const idViaje = viajeInicial?.id_viaje;
  const faltanAsignaciones = Boolean(viajeInicial && (!viajeInicial.chofer_nombre || !viajeInicial.camion_nombre || !viajeInicial.operador_nombre));
  useEffect(() => {
    if (!idViaje || !faltanAsignaciones) return;
    const controlador = new AbortController();
    fetchConToken(`${import.meta.env.VITE_API_URL || "http://localhost:5000"}/api/viaje/${idViaje}`, {
      method: "GET", signal: controlador.signal,
    }).then((resultado) => {
      if (!resultado || controlador.signal.aborted) return;
      if (!resultado.respuesta.ok) throw new Error(resultado.data.mensaje || "No se pudieron cargar las asignaciones del viaje.");
      const datos = resultado.data;
      setDetalle(datos);
      if (!datos.chofer_nombre || !datos.camion_nombre || !datos.operador_nombre) {
        setErrorAsignaciones("No se pudieron obtener todas las asignaciones de este viaje. Volvé a abrir el detalle para reintentar.");
      } else setErrorAsignaciones("");
    }).catch((error) => {
      if (!controlador.signal.aborted) setErrorAsignaciones(error.message);
    });
    return () => controlador.abort();
  }, [idViaje, faltanAsignaciones]);
  if (!viajeInicial) return null;
  const viaje = detalle?.id_viaje === idViaje ? { ...viajeInicial, ...detalle } : viajeInicial;
  const cargandoAsignaciones = faltanAsignaciones && detalle?.id_viaje !== idViaje && !errorAsignaciones;

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
            {errorAsignaciones && <p role="alert" className="detalle-empty">{errorAsignaciones}</p>}

            <div className="detalle-grid">
              <div>
                <span>Chofer asignado</span>
                <p>{viaje.chofer_nombre || (cargandoAsignaciones ? "Cargando nombre..." : "Sin datos del chofer")}</p>
              </div>

              <div>
                <span>Camión asignado</span>
                <p>{viaje.camion_nombre || (viaje.camion ? `${viaje.camion.marca} ${viaje.camion.modelo} (${viaje.camion.matricula})` : cargandoAsignaciones ? "Cargando camión..." : "Sin datos del camión")}</p>
              </div>

              <div>
                <span>Operador responsable</span>
                <p>{viaje.operador_nombre || (cargandoAsignaciones ? "Cargando nombre..." : "Sin datos del operador")}</p>
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
