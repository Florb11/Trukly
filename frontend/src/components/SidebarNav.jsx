import { useState } from "react";
import "./SidebarNav.css";

const navItems = [
  {
    section: "Principal",
    items: [
      { label: "Inicio", path: "/" },
      { label: "Mis Cargas", path: "/cargas" },
      { label: "Rutas", path: "/rutas" },
    ],
  },
  {
    section: "Gestión",
    items: [
      { label: "Pedidos", path: "/pedidos" },
      { label: "Ingresos", path: "/ingresos" },
      { label: "Estadísticas", path: "/estadisticas" },
    ],
  },
  {
    section: "Cuenta",
    items: [
      { label: "Perfil", path: "/perfil" },
      { label: "Configuración", path: "/configuracion" },
      { label: "Cerrar sesión", path: "/logout" },
    ],
  },
];

export default function SidebarNav({ isOpen, onClose }) {
  const [activeItem, setActiveItem] = useState("Inicio");

  return (
    <>
      {isOpen && <div className="sidebar-overlay" onClick={onClose} />}

      <aside className={`sidebar ${isOpen ? "sidebar--open" : ""}`}>
        <div className="sidebar__header">
          <div className="sidebar__logo">
            <span className="sidebar__logo-icon"></span>
            <span className="sidebar__logo-text">TruckerHub</span>
          </div>
          <button className="sidebar__close-btn" onClick={onClose}>
            ✕
          </button>
        </div>

        <nav className="sidebar__nav">
          {navItems.map((group) => (
            <div key={group.section} className="sidebar__group">
              <span className="sidebar__group-label">{group.section}</span>
              <ul className="sidebar__list">
                {group.items.map((item) => (
                  <li key={item.label}>
                    <button
                      className={`sidebar__item ${activeItem === item.label ? "sidebar__item--active" : ""
                        }`}
                      onClick={() => {
                        setActiveItem(item.label);
                        onClose();
                      }}
                    >
                      <span className="sidebar__item-icon">{item.icon}</span>
                      <span className="sidebar__item-label">{item.label}</span>
                      {activeItem === item.label && (
                        <span className="sidebar__item-indicator" />
                      )}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </nav>

        <div className="sidebar__footer">
          <div className="sidebar__user">
            <div className="sidebar__avatar">JD</div>
            <div className="sidebar__user-info">
              <span className="sidebar__user-name">Juan Díaz</span>
              <span className="sidebar__user-role">Camionero verificado</span>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
