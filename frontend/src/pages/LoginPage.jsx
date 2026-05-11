import "./LoginPage.css";
import logoTrukly from "../assets/logo-trukly.png";

import {
  FaMapMarkerAlt,
  FaTools,
  FaClipboardList,
  FaBolt,
} from "react-icons/fa";

function LoginPage() {
  return (
    <section className="login-page">
      <div className="login-left">
        <div className="login-content">
          <div className="login-logo">
            <img
              src={logoTrukly}
              alt="Logo de Trukly"
              className="login-logo-img"
            />
          </div>

          <h1 className="login-title">Ingresá a tu cuenta</h1>

          <p className="login-subtitle">
            Gestioná tus operaciones desde un solo lugar.
          </p>

          <form>
            <div className="login-field">
              <label htmlFor="username">Usuario</label>
              <input
                type="text"
                id="username"
                placeholder="Ingresá tu usuario"
              />
            </div>

            <div className="login-field">
              <label htmlFor="password">Contraseña</label>
              <input
                type="password"
                id="password"
                placeholder="Ingresá tu contraseña"
              />
            </div>

            <button type="submit">Entrar</button>
          </form>

          <p className="login-footer">
            Plataforma para choferes, mecánicos, operadores logísticos y
            administradores.
          </p>
        </div>
      </div>

      <div className="login-right">
        <span className="login-right-badge">
          <FaBolt className="login-badge-icon" />
          Plataforma logística
        </span>

        <h2 className="login-right-title">
          Operaciones más simples, flota más eficiente.
        </h2>

        <p className="login-right-desc">
          Todo lo que necesitás para gestionar tu equipo y tus vehículos en un
          solo lugar.
        </p>

        <ul className="login-features">
          <li>
            <span className="login-feature-icon">
              <FaMapMarkerAlt />
            </span>
            Seguimiento en tiempo real de toda tu flota.
          </li>

          <li>
            <span className="login-feature-icon">
              <FaTools />
            </span>
            Coordinación de mantenimiento y alertas mecánicas.
          </li>

          <li>
            <span className="login-feature-icon">
              <FaClipboardList />
            </span>
            Asignación de tareas y control de entregas.
          </li>
        </ul>

        <div className="login-right-divider" />

        <p className="login-roles-label">Para todo el equipo</p>

        <div className="login-roles">
          <span className="login-role-chip">Choferes</span>
          <span className="login-role-chip">Mecánicos</span>
          <span className="login-role-chip">Operadores</span>
          <span className="login-role-chip">Administradores</span>
        </div>
      </div>
    </section>
  );
}

export default LoginPage;