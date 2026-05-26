import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { FaBars } from "react-icons/fa";
import { useAuth } from "../context/AuthContext";
import "./Navbar.css";
import logoTrukly from "../assets/logo-truklynav.png";

function Navbar() {
  const [menuAbierto, setMenuAbierto] = useState(false);
  const { usuario, estaLogueado, logout } = useAuth();
  const navigate = useNavigate();

  const cerrarMenu = () => {
    setMenuAbierto(false);
  };

  const handleLogout = () => {
    logout();
    cerrarMenu();
    navigate("/login");
  };

  const obtenerRutaDashboard = () => {
    if (usuario?.rol === "admin") {
      return "/dashboardAdmin";
    }

    if (usuario?.rol === "chofer") {
      return "/dashboardTrucker";
    }

    if (usuario?.rol === "mecanico") {
      return "/dashboardMechanic";
    }

    if (usuario?.rol === "operador") {
      return "/dashboardOperator";
    }

    return "/login";
  };

  return (
    <nav className="trukly-navbar">
      <Link to="/" className="navbar-brand" onClick={cerrarMenu}>
        <img src={logoTrukly} alt="Logo de Trukly" />
        <span>Trukly</span>
      </Link>

      <button
        className="navbar-toggle"
        onClick={() => setMenuAbierto(!menuAbierto)}
        aria-label="Abrir menú"
        aria-expanded={menuAbierto}
      >
        <FaBars />
      </button>

      <div className={`navbar-menu ${menuAbierto ? "active" : ""}`}>
        <div className="navbar-links">
          <Link to="/" onClick={cerrarMenu}>
            Inicio
          </Link>

          <a href="#funcionalidades" onClick={cerrarMenu}>
            Funcionalidades
          </a>

          <a href="#roles" onClick={cerrarMenu}>
            Roles
          </a>

          <a href="#contacto" onClick={cerrarMenu}>
            Contacto
          </a>
        </div>

        <div className="navbar-actions">
          {estaLogueado ? (
            <>
              <span className="navbar-user">Hola, {usuario?.nombre}</span>

              <Link
                to={obtenerRutaDashboard()}
                className="login-link"
                onClick={cerrarMenu}
              >
                Dashboard
              </Link>

              <button className="logout-button" onClick={handleLogout}>
                Cerrar sesión
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="login-link" onClick={cerrarMenu}>
                Iniciar sesión
              </Link>

              <Link
                to="/registro"
                className="register-button"
                onClick={cerrarMenu}
              >
                Registrarse
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}

export default Navbar;