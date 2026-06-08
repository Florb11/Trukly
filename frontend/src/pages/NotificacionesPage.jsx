import { useEffect, useState } from "react";
import { FaBell, FaCheckCircle } from "react-icons/fa";
import { fetchConToken } from "../utils/fetchConToken";
import "./NotificacionesPage.css";

function NotificacionesPage() {
  const [notificaciones, setNotificaciones] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");

  const cargarNotificaciones = async () => {
    try {
      setCargando(true);
      setError("");

      const resultado = await fetchConToken(
        "http://localhost:5000/api/notificaciones",
        {
          method: "GET",
        }
      );

      if (!resultado) return;

      const { respuesta, data } = resultado;

      if (!respuesta.ok) {
        throw new Error(
          data.mensaje || data.msg || "Error al cargar las notificaciones"
        );
      }

      setNotificaciones(data.notificaciones || []);
    } catch (error) {
      setError(error.message);
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarNotificaciones();
  }, []);

  const marcarComoLeida = async (idNotificacion) => {
    try {
      setMensaje("");
      setError("");

      const resultado = await fetchConToken(
        `http://localhost:5000/api/notificaciones/${idNotificacion}/leida`,
        {
          method: "PUT",
        }
      );

      if (!resultado) return;

      const { respuesta, data } = resultado;

      if (!respuesta.ok) {
        throw new Error(
          data.mensaje || data.msg || "Error al marcar la notificación"
        );
      }

      setNotificaciones((notificacionesActuales) =>
        notificacionesActuales.map((notificacion) =>
          notificacion.id_notificacion === idNotificacion
            ? data.notificacion
            : notificacion
        )
      );

      setMensaje(data.mensaje || "Notificación marcada como leída");
    } catch (error) {
      setError(error.message);
    }
  };

  if (cargando) {
    return (
      <section className="notificaciones-page">
        <p className="notificaciones-message">Cargando notificaciones...</p>
      </section>
    );
  }

  return (
    <section className="notificaciones-page">
      <div className="notificaciones-header">
        <div>
          <span>Centro de avisos</span>
          <h1>Notificaciones</h1>
          <p>
            Acá podés ver los avisos generados por el sistema, como reportes
            resueltos o cambios importantes.
          </p>
        </div>

        <div className="notificaciones-header__icon">
          <FaBell />
        </div>
      </div>

      {mensaje && (
        <p className="notificaciones-message notificaciones-message--ok">
          {mensaje}
        </p>
      )}

      {error && (
        <p className="notificaciones-message notificaciones-message--error">
          {error}
        </p>
      )}

      <div className="notificaciones-card">
        {notificaciones.length === 0 ? (
          <p className="notificaciones-empty">
            No tenés notificaciones por ahora.
          </p>
        ) : (
          <div className="notificaciones-list">
            {notificaciones.map((notificacion) => (
              <article
                key={notificacion.id_notificacion}
                className={`notificacion-item ${notificacion.leida ? "notificacion-item--leida" : ""
                  }`}
              >
                <div className="notificacion-item__icon">
                  <FaBell />
                </div>

                <div className="notificacion-item__content">
                  <div className="notificacion-item__top">
                    <h2>{notificacion.titulo}</h2>

                    <span
                      className={`notificacion-badge ${notificacion.leida ? "notificacion-badge--leida" : ""
                        }`}
                    >
                      {notificacion.leida ? "Leída" : "Nueva"}
                    </span>
                  </div>

                  <p>{notificacion.mensaje}</p>

                  {notificacion.usuario_destino && (
                    <span className="notificacion-destino">
                      Para: {notificacion.usuario_destino.nombre}{" "}
                      {notificacion.usuario_destino.apellido} (
                      {notificacion.usuario_destino.rol})
                    </span>
                  )}

                  <span className="notificacion-fecha">
                    {notificacion.fecha_hora}
                  </span>

                  {!notificacion.leida && (
                    <button
                      type="button"
                      className="notificacion-action"
                      onClick={() =>
                        marcarComoLeida(notificacion.id_notificacion)
                      }
                    >
                      <FaCheckCircle />
                      Marcar leída
                    </button>
                  )}
              </article>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}

export default NotificacionesPage;