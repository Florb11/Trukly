import { useEffect, useState } from "react";
import { FaArrowRight, FaClock, FaQrcode, FaRoute, FaTruck } from "react-icons/fa";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { apiFetch } from "../utils/api";

export default function HomePage() {
  const { usuario } = useAuth();
  const [viajes, setViajes] = useState([]);
  const [cargando, setCargando] = useState(true);

  useEffect(() => {
    const id = requestAnimationFrame(async () => {
      const result = await apiFetch("/api/choferes/mis-viajes");
      if (result?.response.ok) setViajes(Array.isArray(result.data) ? result.data : []);
      setCargando(false);
    });
    return () => cancelAnimationFrame(id);
  }, []);

  const activo = viajes.find((viaje) => viaje.estado?.toLowerCase() === "en curso");
  const pendientes = viajes.filter((viaje) => viaje.estado?.toLowerCase() === "pendiente").length;

  return (
    <section className="page-stack">
      <header className="page-heading"><span>BUEN DÍA</span><h1>{usuario?.nombre || "Chofer"}</h1><p>Este es el estado de tu operación.</p></header>
      <div className="quick-grid">
        <article><FaTruck /><strong>{cargando ? "-" : viajes.length}</strong><span>Viajes asignados</span></article>
        <article><FaClock /><strong>{cargando ? "-" : pendientes}</strong><span>Pendientes</span></article>
      </div>
      <article className="current-trip">
        <div className="section-title"><div><FaRoute /><span>VIAJE ACTUAL</span></div><Link to="/viajes">Ver todos <FaArrowRight /></Link></div>
        {activo ? <><span className="status live">En curso</span><h2>{activo.origen} → {activo.destino}</h2><p>Viaje #{activo.id_viaje}</p></> : <><h2>No hay un viaje en curso</h2><p>{pendientes ? "Tenés viajes pendientes para iniciar." : "Cuando tengas una asignación aparecerá acá."}</p></>}
      </article>
      <Link className="scan-cta" to="/escanear"><FaQrcode /><div><strong>Escanear punto de control</strong><span>Realizá check-in o check-out</span></div><FaArrowRight /></Link>
    </section>
  );
}
