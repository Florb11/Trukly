import { useState } from "react";
import { Link } from "react-router-dom";
import "./Navbar.css";
import logoTrukly from "../assets/logo-truklynav.png";

function Navbar() {
  const [menuAbierto, setMenuAbierto] = useState(false);

  const cerrarMenu = () => {
    setMenuAbierto(false);
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
      >
        ☰
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
          <Link to="/login" className="login-link" onClick={cerrarMenu}>
            Iniciar sesión
          </Link>

          <Link to="/registro" className="register-button" onClick={cerrarMenu}>
            Registrarse
          </Link>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;