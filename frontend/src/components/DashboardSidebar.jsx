import { NavLink, useNavigate } from "react-router-dom";
import {
  FaChartLine,
  FaHome,
  FaMapMarkedAlt,
  FaSignOutAlt,
  FaTruck,
  FaTruckLoading,
  FaUser,
  FaUsers,
  FaWrench,
  FaClipboardList,
  FaTools,
  FaRoute,
} from "react-icons/fa";
import { useAuth } from "../context/AuthContext";
import "./DashboardSidebar.css";

const menusPorRol = {
  chofer: {
    dashboard: "/dashboardTrucker",
    titulo: "Panel de chofer",
    avatar: "CH",
    rolTexto: "Usuario operativo",
    grupos: [
      {
        section: "Principal",
        items: [
          { label: "Inicio", path: "/dashboardTrucker", icon: <FaHome /> },
          {
            label: "Mis viajes",
            path: "/dashboardTrucker/viajes",
            icon: <FaTruckLoading />,
          },
          {
            label: "Rutas",
            path: "/dashboardTrucker/rutas",
            icon: <FaMapMarkedAlt />,
          },
        ],
      },
      {
        section: "Gestión",
        items: [
          {
            label: "Reportar falla",
            path: "/dashboardTrucker/fallas",
            icon: <FaWrench />,
          },
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
          {
            label: "Perfil",
            path: "/dashboardTrucker/perfil",
            icon: <FaUser />,
          },
        ],
      },
    ],
  },

  admin: {
    dashboard: "/dashboardAdmin",
    titulo: "Panel de administrador",
    avatar: "AD",
    rolTexto: "Administrador",
    grupos: [
      {
        section: "Principal",
        items: [
          { label: "Inicio", path: "/dashboardAdmin", icon: <FaHome /> },
          {
            label: "Usuarios",
            path: "/dashboardAdmin/usuarios",
            icon: <FaUsers />,
          },
          {
            label: "Camiones",
            path: "/dashboardAdmin/camiones",
            icon: <FaTruck />,
          },
          {
            label: "Viajes",
            path: "/dashboardAdmin/viajes",
            icon: <FaRoute />,
          },
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
            icon: <FaTools />,
          },
          {
            label: "Estadísticas",
            path: "/dashboardAdmin/estadisticas",
            icon: <FaChartLine />,
          },
        ],
      },
      {
        section: "Cuenta",
        items: [
          {
            label: "Perfil",
            path: "/dashboardAdmin/perfil",
            icon: <FaUser />,
          },
        ],
      },
    ],
  },

  mecanico: {
    dashboard: "/dashboardMechanic",
    titulo: "Panel de mecánico",
    avatar: "ME",
    rolTexto: "Mecánico",
    grupos: [
      {
        section: "Principal",
        items: [
          { label: "Inicio", path: "/dashboardMechanic", icon: <FaHome /> },
          {
            label: "Reportes asignados",
            path: "/dashboardMechanic/reportes",
            icon: <FaWrench />,
          },
          {
            label: "Mantenimiento",
            path: "/dashboardMechanic/mantenimiento",
            icon: <FaTools />,
          },
        ],
      },
      {
        section: "Cuenta",
        items: [
          {
            label: "Perfil",
            path: "/dashboardMechanic/perfil",
            icon: <FaUser />,
          },
        ],
      },
    ],
  },

  operador: {
    dashboard: "/dashboardOperator",
    titulo: "Panel de operador",
    avatar: "OP",
    rolTexto: "Operador logístico",
    grupos: [
      {
        section: "Principal",
        items: [
          { label: "Inicio", path: "/dashboardOperator", icon: <FaHome /> },
          {
            label: "Viajes",
            path: "/dashboardOperator/crear-viaje",
            icon: <FaTruckLoading />,
          },
          {
            label: "Camiones",
            path: "/dashboardOperator/camiones",
            icon: <FaTruck />,
          },
        ],
      },
      {
        section: "Gestión",
        items: [
          {
            label: "Choferes",
            path: "/dashboardOperator/choferes",
            icon: <FaUsers />,
          },
          {
            label: "Estadísticas",
            path: "/dashboardOperator/estadisticas",
            icon: <FaChartLine />,
          },
        ],
      },
      {
        section: "Cuenta",
        items: [
          {
            label: "Perfil",
            path: "/dashboardOperator/perfil",
            icon: <FaUser />,
          },
        ],
      },
    ],
  },
};

function DashboardSidebar({ isOpen, onClose }) {
  const { usuario, logout } = useAuth();
  const navigate = useNavigate();

  const rol = usuario?.rol || "chofer";
  const menu = menusPorRol[rol] || menusPorRol.chofer;

  const API_URL = "http://localhost:5000";

  const fotoPerfil = usuario?.foto_perfil
    ? `${API_URL}${usuario.foto_perfil}`
    : null;

  const handleLogout = () => {
    logout();
    onClose();
    navigate("/login");
  };

  const inicialUsuario = usuario?.nombre
    ? usuario.nombre.charAt(0).toUpperCase()
    : menu.avatar;

  return (
    <>
      {isOpen && <div className="sidebar-overlay" onClick={onClose} />}

      <aside
        className={`sidebar sidebar--${rol} ${
          isOpen ? "sidebar--open" : ""
        }`}
      >
        <div className="sidebar__header">
          <NavLink
            to={menu.dashboard}
            className="sidebar__logo"
            onClick={onClose}
          >
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

        <nav className="sidebar__nav" aria-label="Navegación del dashboard">
          {menu.grupos.map((group) => (
            <div key={group.section} className="sidebar__group">
              <span className="sidebar__group-label">{group.section}</span>

              <ul className="sidebar__list">
                {group.items.map((item) => (
                  <li key={item.label}>
                    <NavLink
                      to={item.path}
                      end={item.path === menu.dashboard}
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

        <button className="sidebar__logout" type="button" onClick={handleLogout}>
          <span className="sidebar__item-icon">
            <FaSignOutAlt />
          </span>
          <span>Cerrar sesión</span>
        </button>

        <div className="sidebar__footer">
          <div className="sidebar__user">
            <div className="sidebar__avatar">
              {fotoPerfil ? (
                <img src={fotoPerfil} alt="Foto de perfil" />
              ) : (
                inicialUsuario
              )}
            </div>

            <div className="sidebar__user-info">
              <span className="sidebar__user-name">
                {usuario?.nombre
                  ? `${usuario.nombre} ${usuario.apellido || ""}`
                  : "Usuario Trukly"}
              </span>
              <span className="sidebar__user-role">{menu.rolTexto}</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}

export default DashboardSidebar;