import { Link } from "react-router-dom";
import {
  FaBolt,
  FaClipboardList,
  FaMapMarkerAlt,
  FaTools,
} from "react-icons/fa";
import "./LoginPage.css";
import logoTrukly from "../assets/logo-trukly.png";

function LoginPage() {
  return (
    <section className="auth-page login-page">
      <div className="auth-shell">
        <aside className="auth-panel">
          <span className="auth-panel-badge">
            <FaBolt />
            Plataforma logística
          </span>

          <h1>Operaciones más simples, flota más eficiente.</h1>

          <p>
            Ingresá a Trukly para coordinar viajes, revisar estados de flota y
            mantener los reportes de falla siempre ordenados.
          </p>

          <ul className="auth-feature-list">
            <li>
              <span>
                <FaMapMarkerAlt />
              </span>
              Seguimiento claro de viajes y asignaciones.
            </li>
            <li>
              <span>
                <FaTools />
              </span>
              Reportes mecánicos centralizados por unidad.
            </li>
            <li>
              <span>
                <FaClipboardList />
              </span>
              Información útil para cada rol del equipo.
            </li>
          </ul>

          <div className="auth-role-row">
            <span>Choferes</span>
            <span>Mecánicos</span>
            <span>Operadores</span>
            <span>Administradores</span>
          </div>
        </aside>

        <div className="auth-card">
          <div className="auth-brand">
            <img src={logoTrukly} alt="Logo de Trukly" />
            <span>Trukly</span>
          </div>

          <div className="auth-header">
            <span>Bienvenido de nuevo</span>
            <h2>Ingresá a tu cuenta</h2>
            <p>Usá tus credenciales para continuar con la gestión logística.</p>
          </div>

          <form className="auth-form">
            <label className="auth-field" htmlFor="username">
              <span>Usuario</span>
              <input type="text" id="username" placeholder="tu.usuario" />
            </label>

            <label className="auth-field" htmlFor="password">
              <span>Contraseña</span>
              <input type="password" id="password" placeholder="••••••••" />
            </label>

            <div className="auth-options">
              <label className="auth-check">
                <input type="checkbox" />
                <span>Recordarme</span>
              </label>
              <a href="#contacto">Necesito ayuda</a>
            </div>

            <button type="submit">Entrar</button>
          </form>

          <p className="auth-switch">
            ¿Todavía no tenés cuenta? <Link to="/registro">Solicitá acceso</Link>
          </p>
        </div>
      </div>
    </section>
  );
}

export default LoginPage;