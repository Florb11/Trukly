import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { FaBell, FaArrowRight } from "react-icons/fa";
import { fetchConToken } from "../utils/fetchConToken";
import "./NotificationPromptCard.css";

function NotificationPromptCard({
  to,
  tone = "mechanic",
  title = "Centro de avisos",
}) {
  const [cantidadSinLeer, setCantidadSinLeer] = useState(0);
  const [ultimaNotificacion, setUltimaNotificacion] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const cargarNotificaciones = async () => {
      try {
        setCargando(true);
        setError("");

        const resultado = await fetchConToken(
          "http://localhost:5000/api/notificaciones",
          { method: "GET" }
        );

        if (!resultado) return;

        const { respuesta, data } = resultado;

        if (!respuesta.ok) {
          throw new Error(
            data.mensaje || data.msg || "Error al cargar notificaciones"
          );
        }

        const notificaciones = data.notificaciones || [];
        const sinLeer = notificaciones.filter(
          (notificacion) => !notificacion.leida
        );

        setCantidadSinLeer(sinLeer.length);
        setUltimaNotificacion(sinLeer[0] || notificaciones[0] || null);
      } catch (error) {
        setError(error.message);
      } finally {
        setCargando(false);
      }
    };

    cargarNotificaciones();
  }, []);

  const mensaje = () => {
    if (cargando) return "Revisando tus avisos...";

    if (error) return "No se pudieron consultar las notificaciones ahora.";

    if (cantidadSinLeer > 0) {
      return `Tenes ${cantidadSinLeer} notificacion${
        cantidadSinLeer === 1 ? "" : "es"
      } sin leer.`;
    }

    return "No tenes notificaciones nuevas, pero podes revisar el historial.";
  };

  return (
    <article className={`notification-prompt notification-prompt--${tone}`}>
      <div className="notification-prompt__icon">
        <FaBell />
      </div>

      <div className="notification-prompt__content">
        <span>{title}</span>
        <h2>{mensaje()}</h2>

        {ultimaNotificacion && (
          <p>
            Ultimo aviso: <strong>{ultimaNotificacion.titulo}</strong>
          </p>
        )}
      </div>

      <Link to={to} className="notification-prompt__action">
        Ver notificaciones
        <FaArrowRight />
      </Link>
    </article>
  );
}

export default NotificationPromptCard;