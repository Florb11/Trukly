import { NavLink } from "react-router-dom";
import {
  FaChartPie,
  FaClipboardList,
  FaCog,
  FaHome,
  FaSignOutAlt,
  FaTruck,
  FaUserShield,
  FaUsers,
  FaWrench,
} from "react-icons/fa";
import "./SidebarNav.css";

const adminNavItems = [
  {
    section: "Principal",
    items: [
      { label: "Inicio", path: "/dashboardAdmin", icon: <FaHome /> },
      { label: "Usuarios", path: "/dashboardAdmin/usuarios", icon: <FaUsers /> },
      { label: "Camiones", path: "/dashboardAdmin/camiones", icon: <FaTruck /> },
    ],
  },
  {
    section: "Gestión",
    items: [
      {
        label: "Reportes",
        path: "/dashboardAdmin/reportes",
        icon: <FaClipboardList />,
      },
      {
        label: "Mantenimiento",
        path: "/dashboardAdmin/mantenimiento",
        icon: <FaWrench />,
      },
      {
        label: "Estadísticas",
        path: "/dashboardAdmin/estadisticas",
        icon: <FaChartPie />,
      },
    ],
  },
  {
    section: "Cuenta",
    items: [
      { label: "Perfil admin", path: "/dashboardAdmin/perfil", icon: <FaUserShield /> },
      {
        label: "Configuración",
        path: "/dashboardAdmin/configuracion",
        icon: <FaCog />,
      },
      { label: "Cerrar sesión", path: "/login", icon: <FaSignOutAlt /> },
    ],
  },
];

function AdminSidebarNav({ isOpen, onClose }) {
  return (
    <>
      {isOpen && <div className="sidebar-overlay" onClick={onClose} />}

      <aside
        className={`sidebar sidebar--admin ${isOpen ? "sidebar--open" : ""}`}
      >
        <div className="sidebar__header">
          <NavLink
            to="/dashboardAdmin"
            className="sidebar__logo"
            onClick={onClose}
          >
            <span className="sidebar__logo-icon">A</span>
            <span className="sidebar__logo-text">Trukly Admin</span>
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

        <nav className="sidebar__nav" aria-label="Navegación del administrador">
          {adminNavItems.map((group) => (
            <div key={group.section} className="sidebar__group">
              <span className="sidebar__group-label">{group.section}</span>
              <ul className="sidebar__list">
                {group.items.map((item) => (
                  <li key={item.label}>
                    <NavLink
                      to={item.path}
                      end={item.path === "/dashboardAdmin"}
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
            <div className="sidebar__avatar">AD</div>
            <div className="sidebar__user-info">
              <span className="sidebar__user-name">Admin Trukly</span>
              <span className="sidebar__user-role">Control del sistema</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}

export default AdminSidebarNav;