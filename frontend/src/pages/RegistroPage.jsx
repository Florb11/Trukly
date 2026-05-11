import "./RegistroPage.css";

function RegistroPage() {
  return (
    <section className="registro-page">
      <div className="registro-card">
        <div className="registro-header">
          <span className="registro-badge">Registro de chofer</span>
          <h1>Crear cuenta</h1>
          <p>
            Completá tus datos para solicitar el acceso como chofer dentro de
            Trukly.
          </p>
        </div>

        <form className="registro-form">
          <div className="registro-row">
            <div className="registro-field">
              <label htmlFor="nombre">Nombre</label>
              <input type="text" id="nombre" placeholder="Ingresá tu nombre" />
            </div>

            <div className="registro-field">
              <label htmlFor="apellido">Apellido</label>
              <input
                type="text"
                id="apellido"
                placeholder="Ingresá tu apellido"
              />
            </div>
          </div>

          <div className="registro-field">
            <label htmlFor="username">Usuario</label>
            <input
              type="text"
              id="username"
              placeholder="Elegí un nombre de usuario"
            />
          </div>

          <div className="registro-field">
            <label htmlFor="licencia">Licencia</label>
            <input
              type="text"
              id="licencia"
              placeholder="Ingresá tu número de licencia"
            />
          </div>

          <div className="registro-field">
            <label htmlFor="vencimientoLicencia">
              Vencimiento de licencia
            </label>
            <input type="date" id="vencimientoLicencia" />
          </div>

          <div className="registro-field">
            <label htmlFor="password">Contraseña</label>
            <input
              type="password"
              id="password"
              placeholder="Creá una contraseña"
            />
          </div>

          <button type="submit">Solicitar registro</button>
        </form>

        <p className="registro-info">
          Las cuentas de administrador, operador logístico y mecánico son
          creadas internamente por un administrador.
        </p>
      </div>
    </section>
  );
}

export default RegistroPage;