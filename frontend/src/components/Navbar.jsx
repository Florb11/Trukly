import "./Navbar.css";
import iconoTrukly from "../assets/logo-truklynav.png";

function Navbar() {
  return (
    <nav className="trukly-navbar">
      <div className="navbar-left">
        <div className="navbar-brand">
          <img src={iconoTrukly} alt="Icono de Trukly" />
          <span>Trukly</span>
        </div>

        <div className="navbar-links">
          <a href="/">Inicio</a>
          <a href="#funcionalidades">Funcionalidades</a>
          <a href="#soluciones">Soluciones</a>
          <a href="#contacto">Contacto</a>
        </div>
      </div>

      <div className="navbar-actions">
        <a href="/" className="login-link">
          Iniciar sesión
        </a>
        <a href="/registro" className="register-button">
          Registrarse
        </a>
      </div>
    </nav>
  );
}

export default Navbar;