import { useCallback, useEffect, useRef, useState } from "react";
import { FaBell, FaHome, FaQrcode, FaRoute, FaTools, FaUser } from "react-icons/fa";
import { Link, NavLink, Outlet } from "react-router-dom";
import { apiFetch } from "../utils/api";
import { useAuth } from "../context/AuthContext";
import ThemeToggle from "./ThemeToggle";

const navItems = [
  { to: "/", label: "Inicio", icon: FaHome, end: true },
  { to: "/viajes", label: "Viajes", icon: FaRoute },
  { to: "/escanear", label: "Escanear", icon: FaQrcode, primary: true },
  { to: "/fallas", label: "Fallas", icon: FaTools },
  { to: "/perfil", label: "Perfil", icon: FaUser },
];

export default function MobileShell() {
  const { usuario } = useAuth();
  const mecanico = usuario?.rol === "mecanico";
  const gestion = mecanico || usuario?.rol === "operador";
  const items = gestion ? [
    { to: "/", label: "Reportes", icon: FaTools, end: true },
    { to: "/notificaciones", label: "Avisos", icon: FaBell },
    { to: "/perfil", label: "Perfil", icon: FaUser },
  ] : navItems;
  const [notificaciones, setNotificaciones] = useState([]);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");
  const consultando = useRef(false);
  const cargar = useCallback(async () => {
    if (consultando.current) return;
    consultando.current = true;
    try {
      const resultado = await apiFetch("/api/notificaciones", { signal: AbortSignal.timeout(20000) });
      if (!resultado) return;
      if (!resultado.response.ok) throw new Error(resultado.data.mensaje || "No se pudieron cargar los avisos.");
      setNotificaciones(resultado.data.notificaciones || []);
      setError("");
    } catch {
      setError("No se pudieron actualizar los avisos. Revisá tu conexión y volvé a intentar.");
    } finally {
      consultando.current = false;
      setCargando(false);
    }
  }, []);
  useEffect(() => {
    const inicial = setTimeout(cargar, 0);
    const actualizar = () => { if (document.visibilityState === "visible") cargar(); };
    const intervalo = setInterval(actualizar, 30000);
    window.addEventListener("focus", actualizar);
    document.addEventListener("visibilitychange", actualizar);
    return () => {
      clearTimeout(inicial);
      clearInterval(intervalo);
      window.removeEventListener("focus", actualizar);
      document.removeEventListener("visibilitychange", actualizar);
    };
  }, [cargar]);
  const noLeidas = notificaciones.filter((aviso) => !aviso.leida).length;
  return (
    <div className="mobile-shell">
      <header className="mobile-topbar">
        <img src="/pwa-192.png" alt="" />
        <div><strong>Trukly</strong><span>{mecanico ? "Taller" : gestion ? "Operación" : "Choferes"}</span></div>
        <ThemeToggle />
        <Link className="notification-bell icon-button" to="/notificaciones" title="Notificaciones" aria-label={`Notificaciones, ${noLeidas} sin leer`}>
          <FaBell />{noLeidas > 0 && <b>{noLeidas > 99 ? "99+" : noLeidas}</b>}
        </Link>
      </header>
      <main className="mobile-content"><Outlet context={{ notificaciones, setNotificaciones, cargando, error, cargar }} /></main>
      <nav className="mobile-bottom-nav" style={gestion ? { gridTemplateColumns: "repeat(3, 1fr)" } : undefined} aria-label="Navegación principal">
        {items.map(({ to, label, icon: Icon, end, primary }) => (
          <NavLink key={to} to={to} end={end} className={({ isActive }) => `${isActive ? "active" : ""} ${primary ? "primary" : ""}`}>
            <Icon /><span>{label}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
