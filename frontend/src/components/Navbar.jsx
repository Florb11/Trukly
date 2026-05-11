import { useState } from "react";
import { Link } from "react-router-dom";
import "./Navbar.css";
import logoTrukly from "../assets/logo-truklynav.png";

function Navbar() {
  const [menuAbierto, setMenuAbierto] = useState(false);

  return (
    <nav className="trukly-navbar">
      <div className="navbar-brand">
        <img src={logoTrukly} alt="Logo de Trukly" />
        <span>Trukly</span>
      </div>

      <button
        className="navbar-toggle"
        onClick={() => setMenuAbierto(!menuAbierto)}
      >
        ☰
      </button>

      <div className={`navbar-menu ${menuAbierto ? "active" : ""}`}>
        <div className="navbar-links">
          <Link to="/">Inicio</Link>
          <a href="#funcionalidades">Funcionalidades</a>
          <a href="#roles">Roles</a>
          <a href="#contacto">Contacto</a>
        </div>

        <div className="navbar-actions">
          <Link to="/" className="login-link">
            Iniciar sesión
          </Link>

          <Link to="/registro" className="register-button">
            Registrarse
          </Link>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;