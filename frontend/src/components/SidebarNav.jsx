import { NavLink } from "react-router-dom";
import {
  FaChartLine,
  FaCog,
  FaHome,
  FaMapMarkedAlt,
  FaSignOutAlt,
  FaTruckLoading,
  FaUser,
  FaWrench,
} from "react-icons/fa";
import "./SidebarNav.css";

const navItems = [
  {
    section: "Principal",
    items: [
      { label: "Inicio", path: "/dashboardTrucker", icon: <FaHome /> },
      { label: "Mis viajes", path: "/dashboardTrucker/viajes", icon: <FaTruckLoading /> },
      { label: "Rutas", path: "/dashboardTrucker/rutas", icon: <FaMapMarkedAlt /> },
    ],
  },
  {
    section: "Gestión",
    items: [
      { label: "Reportar falla", path: "/dashboardTrucker/fallas", icon: <FaWrench /> },
      {
        label: "Estadísticas",
        path: "/dashboardTrucker/estadisticas",
        icon: <FaChartLine />,
      },
    ],
  },
  {
    section: "Cuenta",
    items: [
      { label: "Perfil", path: "/dashboardTrucker/perfil", icon: <FaUser /> },
      { label: "Configuración", path: "/dashboardTrucker/configuracion", icon: <FaCog /> },
      { label: "Cerrar sesión", path: "/login", icon: <FaSignOutAlt /> },
    ],
  },
];

function SidebarNav({ isOpen, onClose }) {
  return (
    <>
      {isOpen && <div className="sidebar-overlay" onClick={onClose} />}

      <aside className={`sidebar ${isOpen ? "sidebar--open" : ""}`}>
        <div className="sidebar__header">
          <NavLink to="/dashboardTrucker" className="sidebar__logo" onClick={onClose}>
            <span className="sidebar__logo-icon">T</span>
            <span className="sidebar__logo-text">Trukly</span>
          </NavLink>
          <button
            className="sidebar__close-btn"
            onClick={onClose}
            type="button"
            aria-label="Cerrar menú"
          >
            x
          </button>
        </div>

        <nav className="sidebar__nav" aria-label="Navegación del chofer">
          {navItems.map((group) => (
            <div key={group.section} className="sidebar__group">
              <span className="sidebar__group-label">{group.section}</span>
              <ul className="sidebar__list">
                {group.items.map((item) => (
                  <li key={item.label}>
                    <NavLink
                      to={item.path}
                      end={item.path === "/dashboardTrucker"}
                      className={({ isActive }) =>
                        `sidebar__item ${
                          isActive ? "sidebar__item--active" : ""
                        }`
                      }
                      onClick={onClose}
                    >
                      <span className="sidebar__item-icon">{item.icon}</span>
                      <span className="sidebar__item-label">{item.label}</span>
                      <span className="sidebar__item-indicator" />
                    </NavLink>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </nav>

        <div className="sidebar__footer">
          <div className="sidebar__user">
            <div className="sidebar__avatar">CH</div>
            <div className="sidebar__user-info">
              <span className="sidebar__user-name">Chofer Trukly</span>
              <span className="sidebar__user-role">Usuario operativo</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}

export default SidebarNav;