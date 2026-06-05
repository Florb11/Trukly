import { useEffect, useState } from "react";
import {
  FaEye,
  FaTimesCircle,
  FaRoute,
  FaTruck,
  FaUser,
  FaMapMarkerAlt,
} from "react-icons/fa";
import { fetchConToken } from "../utils/fetchConToken";
import "./AdminViajesPage.css";

function AdminViajesPage() {
  const [viajes, setViajes] = useState([]);
  const [viajeDetalle, setViajeDetalle] = useState(null);
  const [viajeCancelar, setViajeCancelar] = useState(null);
  const [motivoCancelacion, setMotivoCancelacion] = useState("");
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");

  const cargarViajes = async () => {
    try {
      setCargando(true);
      setError("");
      setMensaje("");

      const resultado = await fetchConToken(
        "http://localhost:5000/api/admin/viajes",
        { method: "GET" }
      );

      if (!resultado) return;

      const { respuesta, data } = resultado;

      if (!respuesta.ok) {
        throw new Error(data.mensaje || data.msg || "Error al cargar viajes");
      }

      setViajes(data);
    } catch (err) {
      setError(err.message);
      setViajes([]);
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarViajes();
  }, []);

  const abrirDetalle = async (idViaje) => {
    try {
      setError("");
      setMensaje("");

      const resultado = await fetchConToken(
        `http://localhost:5000/api/admin/viajes/${idViaje}`,
        { method: "GET" }
      );

      if (!resultado) return;

      const { respuesta, data } = resultado;

      if (!respuesta.ok) {
        throw new Error(data.mensaje || data.msg || "Error al obtener detalle");
      }

      setViajeDetalle(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const abrirCancelar = (viaje) => {
    setViajeCancelar(viaje);
    setMotivoCancelacion("");
    setError("");
    setMensaje("");
  };

  const cerrarModales = () => {
    setViajeDetalle(null);
    setViajeCancelar(null);
    setMotivoCancelacion("");
  };

  const cancelarViaje = async () => {
    if (!motivoCancelacion.trim()) {
      setError("Tenés que ingresar un motivo de cancelación");
      return;
    }

    try {
      setGuardando(true);
      setError("");
      setMensaje("");

      const resultado = await fetchConToken(
        `http://localhost:5000/api/admin/viajes/${viajeCancelar.id_viaje}/cancelar`,
        {
          method: "PUT",
          body: JSON.stringify({
            motivo: motivoCancelacion,
          }),
        }
      );

      if (!resultado) return;

      const { respuesta, data } = resultado;

      if (!respuesta.ok) {
        throw new Error(data.mensaje || data.msg || "Error al cancelar viaje");
      }

      setMensaje(data.mensaje || "Viaje cancelado correctamente");

      setViajes((prevViajes) =>
        prevViajes.map((viaje) =>
          viaje.id_viaje === viajeCancelar.id_viaje ? data.viaje : viaje
        )
      );

      cerrarModales();
    } catch (err) {
      setError(err.message);
    } finally {
      setGuardando(false);
    }
  };

  const formatearFecha = (fecha) => {
    if (!fecha) return "-";

    const partes = fecha.split("-");
    if (partes.length !== 3) return fecha;

    return `${partes[2]}/${partes[1]}/${partes[0]}`;
  };

  const puedeCancelarse = (estado) => {
    if (!estado) return false;

    const estadoNormalizado = estado.toLowerCase();

    return estadoNormalizado !== "cancelado" && estadoNormalizado !== "finalizado";
  };

  return (
    <section className="admin-viajes-page">
      <div className="admin-viajes-header">
        <div>
          <span>Supervisión</span>
          <h1>Viajes</h1>
          <p>
            Visualizá los viajes del sistema y cancelá operaciones cuando sea
            necesario.
          </p>
        </div>

        <div className="admin-viajes-header__icon">
          <FaRoute />
        </div>
      </div>

      <div className="admin-viajes-stats">
        <article className="admin-viajes-stat">
          <span>Total viajes</span>
          <strong>{viajes.length}</strong>
        </article>

        <article className="admin-viajes-stat">
          <span>Activos</span>
          <strong>
            {
              viajes.filter(
                (v) =>
                  v.estado &&
                  v.estado.toLowerCase() !== "cancelado" &&
                  v.estado.toLowerCase() !== "finalizado"
              ).length
            }
          </strong>
        </article>

        <article className="admin-viajes-stat">
          <span>Cancelados</span>
          <strong>
            {
              viajes.filter(
                (v) => v.estado && v.estado.toLowerCase() === "cancelado"
              ).length
            }
          </strong>
        </article>
      </div>

      {mensaje && <p className="admin-message admin-message--ok">{mensaje}</p>}
      {error && <p className="admin-message admin-message--error">{error}</p>}

      <article className="admin-viajes-card">
        <div className="admin-viajes-card__header">
          <div>
            <h2>Listado general</h2>
            <span>Todos los viajes registrados</span>
          </div>
        </div>

        {cargando ? (
          <p className="admin-message">Cargando viajes...</p>
        ) : viajes.length === 0 ? (
          <p className="admin-message">No hay viajes registrados.</p>
        ) : (
          <div className="admin-viajes-table-wrap">
            <table className="admin-viajes-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Origen</th>
                  <th>Destino</th>
                  <th>Salida</th>
                  <th>Llegada</th>
                  <th>Recorrido</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>

              <tbody>
                {viajes.map((viaje) => (
                  <tr key={viaje.id_viaje}>
                    <td data-label="#">#{viaje.id_viaje}</td>
                    <td data-label="Origen">{viaje.origen}</td>
                    <td data-label="Destino">{viaje.destino}</td>
                    <td data-label="Salida">
                      {formatearFecha(viaje.fecha_salida)}
                    </td>
                    <td data-label="Llegada">
                      {formatearFecha(viaje.fecha_llegada)}
                    </td>
                    <td data-label="Recorrido">{viaje.recorrido} km</td>
                    <td data-label="Estado">
                      <span
                        className={`admin-viajes-badge admin-viajes-badge--${viaje.estado}`}
                      >
                        {viaje.estado}
                      </span>
                    </td>
                    <td data-label="Acciones">
                      <div className="admin-viajes-actions">
                        <button
                          type="button"
                          className="admin-viajes-btn admin-viajes-btn--view"
                          onClick={() => abrirDetalle(viaje.id_viaje)}
                        >
                          <FaEye />
                          Ver
                        </button>

                        {puedeCancelarse(viaje.estado) && (
                          <button
                            type="button"
                            className="admin-viajes-btn admin-viajes-btn--cancel"
                            onClick={() => abrirCancelar(viaje)}
                          >
                            <FaTimesCircle />
                            Cancelar
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </article>

      {viajeDetalle && (
        <div className="admin-viajes-modal-backdrop">
          <div className="admin-viajes-modal">
            <div className="admin-viajes-modal__header">
              <h2>Detalle del viaje #{viajeDetalle.id_viaje}</h2>
              <button type="button" onClick={cerrarModales}>
                x
              </button>
            </div>

            <div className="admin-viajes-detail-grid">
              <div>
                <span>
                  <FaMapMarkerAlt /> Origen
                </span>
                <strong>{viajeDetalle.origen}</strong>
              </div>

              <div>
                <span>
                  <FaMapMarkerAlt /> Destino
                </span>
                <strong>{viajeDetalle.destino}</strong>
              </div>

              <div>
                <span>Fecha salida</span>
                <strong>{formatearFecha(viajeDetalle.fecha_salida)}</strong>
              </div>

              <div>
                <span>Fecha llegada</span>
                <strong>{formatearFecha(viajeDetalle.fecha_llegada)}</strong>
              </div>

              <div>
                <span>
                  <FaUser /> Chofer
                </span>
                <strong>#{viajeDetalle.Chofer_Usuario_idUsuario}</strong>
              </div>

              <div>
                <span>
                  <FaTruck /> Camión
                </span>
                <strong>#{viajeDetalle.Camion_id_camion}</strong>
              </div>

              <div>
                <span>Operador</span>
                <strong>
                  #{viajeDetalle.OperadorLogistico_Usuario_idUsuario}
                </strong>
              </div>

              <div>
                <span>Recorrido</span>
                <strong>{viajeDetalle.recorrido} km</strong>
              </div>
            </div>

            <div className="admin-viajes-observaciones">
              <span>Observaciones</span>
              <p>{viajeDetalle.observaciones || "Sin observaciones"}</p>
            </div>

            <div className="admin-viajes-modal__footer">
              <button
                type="button"
                className="admin-viajes-btn admin-viajes-btn--secondary"
                onClick={cerrarModales}
              >
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}

      {viajeCancelar && (
        <div className="admin-viajes-modal-backdrop">
          <div className="admin-viajes-modal">
            <div className="admin-viajes-modal__header">
              <h2>Cancelar viaje #{viajeCancelar.id_viaje}</h2>
              <button type="button" onClick={cerrarModales}>
                x
              </button>
            </div>

            <p className="admin-viajes-warning">
              Esta acción cambiará el estado del viaje a cancelado. Ingresá el
              motivo para dejarlo registrado en observaciones.
            </p>

            <label className="admin-viajes-field">
              <span>Motivo de cancelación</span>
              <textarea
                value={motivoCancelacion}
                onChange={(e) => setMotivoCancelacion(e.target.value)}
                placeholder="Ej: El camión tuvo una falla mecánica"
                rows="4"
              />
            </label>

            <div className="admin-viajes-modal__footer">
              <button
                type="button"
                className="admin-viajes-btn admin-viajes-btn--secondary"
                onClick={cerrarModales}
                disabled={guardando}
              >
                Volver
              </button>

              <button
                type="button"
                className="admin-viajes-btn admin-viajes-btn--cancel"
                onClick={cancelarViaje}
                disabled={guardando}
              >
                {guardando ? "Cancelando..." : "Confirmar cancelación"}
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

export default AdminViajesPage;