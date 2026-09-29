import { FaHome, FaQrcode, FaRoute, FaTools, FaUser } from "react-icons/fa";
import { NavLink, Outlet } from "react-router-dom";

const navItems = [
  { to: "/", label: "Inicio", icon: FaHome, end: true },
  { to: "/viajes", label: "Viajes", icon: FaRoute },
  { to: "/escanear", label: "Escanear", icon: FaQrcode, primary: true },
  { to: "/fallas", label: "Fallas", icon: FaTools },
  { to: "/perfil", label: "Perfil", icon: FaUser },
];

export default function MobileShell() {
  return (
    <div className="mobile-shell">
      <header className="mobile-topbar">
        <img src="/pwa-192.png" alt="" />
        <div><strong>Trukly</strong><span>App de choferes</span></div>
      </header>
      <main className="mobile-content"><Outlet /></main>
      <nav className="mobile-bottom-nav" aria-label="Navegación principal">
        {navItems.map(({ to, label, icon: Icon, end, primary }) => (
          <NavLink key={to} to={to} end={end} className={({ isActive }) => `${isActive ? "active" : ""} ${primary ? "primary" : ""}`}>
            <Icon /><span>{label}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  );
}
