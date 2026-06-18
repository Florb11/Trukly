import { useEffect, useState } from "react";
import { FaClipboardList, FaCheckCircle, FaClock } from "react-icons/fa";
import "./ViajesTruckerPage.css";
import { fetchConToken } from "../utils/fetchConToken";

function ViajesTruckerPage({ title = "Panel del chofer" }) {
  const [viajes, setViajes] = useState([]);
  const [cargandoViajes, setCargandoViajes] = useState(true);
  const [errorViajes, setErrorViajes] = useState("");
  const [accionando, setAccionando] = useState(null);

  const usuario = JSON.parse(localStorage.getItem("usuario"));

  const cargarViajes = async () => {
    try {
      setCargandoViajes(true);
      setErrorViajes("");

      const resultado = await fetchConToken("http://localhost:5000/api/choferes/mis-viajes", {
        method: "GET",
      });

      if (!resultado) return;

      const { respuesta, data } = resultado;

      if (!respuesta.ok) {
        throw new Error(data.mensaje || data.msg || "Error al cargar viajes");
      }

      setViajes(Array.isArray(data) ? data : []);
    } catch (error) {
      setErrorViajes(error.message);
      setViajes([]);
    } finally {
      setCargandoViajes(false);
    }
  };

  useEffect(() => {
    cargarViajes();
  }, []);

  const aceptarViaje = async (idViaje) => {
    setAccionando(idViaje);
    try {
      const resultado = await fetchConToken(
        `http://localhost:5000/api/choferes/viajes/${idViaje}/iniciar`,
        { method: "PUT" }
      );
      if (!resultado) return;
      const { respuesta, data } = resultado;
      if (!respuesta.ok) throw new Error(data.mensaje || "Error al aceptar el viaje");
      cargarViajes();
    } catch (error) {
      setErrorViajes(error.message);
    } finally {
      setAccionando(null);
    }
  };

  const finalizarViaje = async (idViaje) => {
    setAccionando(idViaje);
    try {
      const resultado = await fetchConToken(
        `http://localhost:5000/api/choferes/viajes/${idViaje}/finalizar`,
        { method: "PUT" }
      );
      if (!resultado) return;
      const { respuesta, data } = resultado;
      if (!respuesta.ok) throw new Error(data.mensaje || "Error al finalizar el viaje");
      cargarViajes();
    } catch (error) {
      setErrorViajes(error.message);
    } finally {
      setAccionando(null);
    }
  };

  const viajesActivos = viajes.filter((v) => v.estado?.toLowerCase() === "en curso").length;
  const viajesPendientes = viajes.filter((v) => v.estado?.toLowerCase() === "pendiente").length;
  const viajesFinalizados = viajes.filter((v) => v.estado?.toLowerCase() === "finalizado").length;

  return (
    <section className="chofer-page">
      <div className="chofer-page__header">
        <span>Dashboard</span>
        <h1>{title}</h1>
        <p>
          Bienvenido, {usuario?.nombre}. Aquí podés ver tus viajes asignados y
          su estado actual.
        </p>
      </div>

      <div className="chofer-page__grid">
        <article className="chofer-card chofer-card--info">
          <div>
            <span>Viajes en curso</span>
            <strong>{viajesActivos}</strong>
            <p>Activos ahora</p>
          </div>
          <div className="chofer-card__icon">
            <FaClipboardList />
          </div>
        </article>

        <article className="chofer-card chofer-card--warning">
          <div>
            <span>Viajes pendientes</span>
            <strong>{viajesPendientes}</strong>
            <p>Sin iniciar</p>
          </div>
          <div className="chofer-card__icon">
            <FaClock />
          </div>
        </article>

        <article className="chofer-card chofer-card--success">
          <div>
            <span>Viajes finalizados</span>
            <strong>{viajesFinalizados}</strong>
            <p>Completados</p>
          </div>
          <div className="chofer-card__icon">
            <FaCheckCircle />
          </div>
        </article>
      </div>

      {errorViajes && (
        <p className="admin-message admin-message--error">{errorViajes}</p>
      )}

      <article className="chofer-table-card">
        <div className="chofer-table-card__header">
          <h2>Mis viajes asignados</h2>
          <span>Esta semana</span>
        </div>

        {cargandoViajes ? (
          <p className="admin-message">Cargando viajes...</p>
        ) : viajes.length === 0 ? (
          <p className="admin-message">No tenés viajes asignados.</p>
        ) : (
          <div className="chofer-table-wrap">
            <table className="chofer-table">
              <thead>
                <tr>
                  <th>Origen</th>
                  <th>Destino</th>
                  <th>Fecha salida</th>
                  <th>Fecha llegada</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {viajes.map((viaje) => {
                  const estadoLower = viaje.estado?.toLowerCase();
                  return (
                    <tr key={viaje.id_viaje}>
                      <td>{viaje.origen}</td>
                      <td>{viaje.destino}</td>
                      <td>{viaje.fecha_salida}</td>
                      <td>{viaje.fecha_llegada || "-"}</td>
                      <td>
                        <span
                          className={`chofer-badge chofer-badge--${estadoLower?.replace(" ", "-")}`}
                        >
                          {viaje.estado}
                        </span>
                      </td>
                      <td>
                        {estadoLower === "pendiente" && (
                          <button
                            type="button"
                            className="chofer-btn-accion chofer-btn-accion--aceptar"
                            disabled={accionando === viaje.id_viaje}
                            onClick={() => aceptarViaje(viaje.id_viaje)}
                          >
                            {accionando === viaje.id_viaje ? "Procesando..." : "Aceptar viaje"}
                          </button>
                        )}
                        {estadoLower === "en curso" && (
                          <button
                            type="button"
                            className="chofer-btn-accion chofer-btn-accion--finalizar"
                            disabled={accionando === viaje.id_viaje}
                            onClick={() => finalizarViaje(viaje.id_viaje)}
                          >
                            {accionando === viaje.id_viaje ? "Procesando..." : "Finalizar viaje"}
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </article>
    </section>
  );
}

export default ViajesTruckerPage;