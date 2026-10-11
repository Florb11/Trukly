import { useEffect, useState } from "react";
import { FaArrowLeft, FaMapMarkerAlt, FaSignInAlt, FaSignOutAlt, FaTruck } from "react-icons/fa";
import { Link } from "react-router-dom";
import { apiFetch } from "../utils/api";

function formatearFecha(fecha) {
  if (!fecha) return { fecha: "-", hora: "-" };
  const valor = new Date(fecha);
  if (Number.isNaN(valor.getTime())) return { fecha, hora: "-" };
  return {
    fecha: valor.toLocaleDateString("es-AR", { day: "2-digit", month: "short", year: "numeric" }),
    hora: valor.toLocaleTimeString("es-AR", { hour: "2-digit", minute: "2-digit" }),
  };
}

export default function HistorialPage() {
  const [registros, setRegistros] = useState([]);
  const [filtro, setFiltro] = useState("todos");
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const id = requestAnimationFrame(async () => {
      const resultado = await apiFetch("/api/choferes/mis-registros");
      if (resultado?.response.ok) {
        setRegistros(Array.isArray(resultado.data) ? resultado.data : []);
      } else {
        setError(resultado?.data.mensaje || "No se pudo cargar el historial");
      }
      setCargando(false);
    });
    return () => cancelAnimationFrame(id);
  }, []);

  const visibles = registros.filter((registro) => (
    filtro === "todos" || registro.tipo_registro === filtro
  ));

  return (
    <section className="page-stack">
      <header className="page-heading history-heading">
        <Link to="/viajes" aria-label="Volver a viajes"><FaArrowLeft /></Link>
        <div><span>TRAZABILIDAD</span><h1>Historial</h1><p>Ingresos y salidas registrados.</p></div>
      </header>

      <div className="segmented">
        <button className={filtro === "todos" ? "active" : ""} onClick={() => setFiltro("todos")}>Todos</button>
        <button className={filtro === "ingreso" ? "active" : ""} onClick={() => setFiltro("ingreso")}>Check-in</button>
        <button className={filtro === "salida" ? "active" : ""} onClick={() => setFiltro("salida")}>Check-out</button>
      </div>

      {error && <p className="feedback error">{error}</p>}
      {cargando ? <p className="empty">Cargando movimientos...</p> : visibles.length === 0 ? (
        <p className="empty">Todavía no hay movimientos registrados.</p>
      ) : (
        <div className="history-list">
          {visibles.map((registro) => {
            const esIngreso = registro.tipo_registro === "ingreso";
            const fecha = formatearFecha(registro.fecha_hora);
            const Icono = esIngreso ? FaSignInAlt : FaSignOutAlt;
            return (
              <article key={registro.id_registro} className={esIngreso ? "check-in" : "check-out"}>
                <div className="history-icon"><Icono /></div>
                <div className="history-content">
                  <div className="history-top"><span>{esIngreso ? "Check-in" : "Check-out"}</span><time>{fecha.hora}</time></div>
                  <h2>Viaje #{registro.id_viaje}</h2>
                  <p><FaMapMarkerAlt /> {registro.origen} → {registro.destino}</p>
                  <div className="history-meta"><span><FaTruck /> Camión #{registro.id_camion}</span><time>{fecha.fecha}</time></div>
                  {registro.observacion && <blockquote>{registro.observacion}</blockquote>}
                </div>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}
