import "./LoginPage.css";
import logoTrukly from "../assets/logo-trukly.png";

function LoginPage() {
  return (
    <section className="login-page">
      <div className="login-card">
        <img src={logoTrukly} alt="Logo de Trukly" className="login-logo" />

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
          Plataforma para choferes, mecánicos y operadores logísticos.
        </p>
      </div>
    </section>
  );
}

export default LoginPage;