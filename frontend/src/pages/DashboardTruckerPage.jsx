import { useEffect, useState } from "react";
import { FaClipboardList, FaCheckCircle, FaClock } from "react-icons/fa";
import "./DashboardTruckerPage.css";
import { fetchConToken } from "../utils/fetchConToken";

function ChoferViajesPage({ title = "Panel del chofer" }) {
  const [viajes, setViajes] = useState([]);
  const [cargandoViajes, setCargandoViajes] = useState(true);
  const [errorViajes, setErrorViajes] = useState("");

  const usuario = JSON.parse(localStorage.getItem("usuario"));
  const idChofer = usuario?.id_usuario;

  const cargarViajes = async () => {
    try {
      setCargandoViajes(true);
      setErrorViajes("");

      const resultado = await fetchConToken("http://localhost:5000/api/viaje", {
        method: "GET",
      });

      if (!resultado) return;

      const { respuesta, data } = resultado;

      if (!respuesta.ok) {
        throw new Error(data.mensaje || data.msg || "Error al cargar viajes");
      }

      const misViajes = data.filter(
        (viaje) => viaje.Chofer_Usuario_idUsuario === idChofer,
      );

      setViajes(misViajes);
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

  const viajesActivos = viajes.filter((v) => v.estado === "en curso").length;
  const viajesPendientes = viajes.filter(
    (v) => v.estado === "pendiente",
  ).length;
  const viajesFinalizados = viajes.filter(
    (v) => v.estado === "finalizado",
  ).length;

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

      <article className="chofer-table-card">
        <div className="chofer-table-card__header">
          <h2>Mis viajes asignados</h2>
          <span>Esta semana</span>
        </div>

        {cargandoViajes ? (
          <p className="admin-message">Cargando viajes...</p>
        ) : errorViajes ? (
          <p className="admin-message admin-message--error">{errorViajes}</p>
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
                </tr>
              </thead>
              <tbody>
                {viajes.map((viaje) => (
                  <tr key={viaje.id_viaje}>
                    <td>{viaje.origen}</td>
                    <td>{viaje.destino}</td>
                    <td>{viaje.fecha_salida}</td>
                    <td>{viaje.fecha_llegada}</td>
                    <td>
                      <span
                        className={`chofer-badge chofer-badge--${viaje.estado.replace(" ", "-")}`}
                      >
                        {viaje.estado}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </article>
    </section>
  );
}

export default ChoferViajesPage;
