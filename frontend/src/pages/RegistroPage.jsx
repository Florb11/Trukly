import { useState } from "react";
import { Link } from "react-router-dom";
import { FaIdCard, FaShieldAlt, FaTruckMoving } from "react-icons/fa";
import "./RegistroPage.css";
import logoTrukly from "../assets/logo-trukly.png";

function RegistroPage() {
  const [formulario, setFormulario] = useState({
    nombre: "",
    apellido: "",
    username: "",
    email: "",
    licencia: "",
    vencimientoLicencia: "",
    password: "",
    legajo: "",
  });

  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setFormulario({
      ...formulario,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setMensaje("");
    setError("");

    try {
      const respuesta = await fetch("http://localhost:5000/api/auth/registro", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formulario),
      });

      const data = await respuesta.json();

      if (respuesta.ok) {
        setMensaje(data.mensaje);

        setFormulario({
          nombre: "",
          apellido: "",
          username: "",
          email: "",
          licencia: "",
          vencimientoLicencia: "",
          password: "",
          legajo: "",
        });
      } else {
        setError(data.mensaje || "No se pudo registrar el chofer");
      }
    } catch (error) {
      setError("No se pudo conectar con el backend");
    }
  };

  return (
    <section className="auth-page registro-page">
      <div className="registro-shell">
        <aside className="registro-panel">
          <span className="registro-panel-badge">
            <FaTruckMoving />
            Alta de chofer
          </span>

          <h1>Pedí tu acceso y empezá a operar desde Trukly.</h1>
          <p>
            El registro permite solicitar una cuenta de chofer. Luego un
            administrador valida los datos y habilita el acceso correspondiente.
          </p>

          <div className="registro-panel-list">
            <div>
              <span>
                <FaIdCard />
              </span>
              <strong>Datos personales</strong>
              <p>Nombre, usuario, email y licencia para identificar tu perfil.</p>
            </div>

            <div>
              <span>
                <FaShieldAlt />
              </span>
              <strong>Validación interna</strong>
              <p>Las cuentas operativas se revisan antes de quedar activas.</p>
            </div>
          </div>
        </aside>

        <div className="registro-card">
          <div className="auth-brand">
            <img src={logoTrukly} alt="Logo de Trukly" />
            <span>Trukly</span>
          </div>

          <div className="registro-header">
            <span className="registro-badge">Registro de chofer</span>
            <h2>Crear cuenta</h2>
            <p>Completá tus datos para solicitar acceso a la plataforma.</p>
          </div>

          <form className="registro-form" onSubmit={handleSubmit}>
            <div className="registro-row">
              <label className="registro-field" htmlFor="nombre">
                <span>Nombre</span>
                <input
                  type="text"
                  id="nombre"
                  name="nombre"
                  value={formulario.nombre}
                  onChange={handleChange}
                  placeholder="Ingresá tu nombre"
                />
              </label>

              <label className="registro-field" htmlFor="apellido">
                <span>Apellido</span>
                <input
                  type="text"
                  id="apellido"
                  name="apellido"
                  value={formulario.apellido}
                  onChange={handleChange}
                  placeholder="Ingresá tu apellido"
                />
              </label>
            </div>

            <label className="registro-field" htmlFor="username-registro">
              <span>Usuario</span>
              <input
                type="text"
                id="username-registro"
                name="username"
                value={formulario.username}
                onChange={handleChange}
                placeholder="Elegí un nombre de usuario"
              />
            </label>

            <label className="registro-field" htmlFor="email-registro">
              <span>Email</span>
              <input
                type="email"
                id="email-registro"
                name="email"
                value={formulario.email}
                onChange={handleChange}
                placeholder="Ingresá tu email"
              />
            </label>

            <label className="registro-field" htmlFor="licencia">
              <span>Licencia</span>
              <input
                type="text"
                id="licencia"
                name="licencia"
                value={formulario.licencia}
                onChange={handleChange}
                placeholder="Ingresá tu número de licencia"
              />
            </label>

            <label className="registro-field" htmlFor="vencimientoLicencia">
              <span>Vencimiento de licencia</span>
              <input
                type="date"
                id="vencimientoLicencia"
                name="vencimientoLicencia"
                value={formulario.vencimientoLicencia}
                onChange={handleChange}
              />
            </label>

            <label className="registro-field" htmlFor="legajo">
              <span>Legajo</span>
              <input
                type="text"
                id="legajo"
                name="legajo"
                value={formulario.legajo}
                onChange={handleChange}
                placeholder="Ingresá tu legajo"
              />
            </label>

            <label className="registro-field" htmlFor="password-registro">
              <span>Contraseña</span>
              <input
                type="password"
                id="password-registro"
                name="password"
                value={formulario.password}
                onChange={handleChange}
                placeholder="Creá una contraseña"
              />
            </label>

            <button type="submit">Solicitar registro</button>
          </form>

          {mensaje && <p className="registro-mensaje exito">{mensaje}</p>}
          {error && <p className="registro-mensaje error">{error}</p>}

          <p className="registro-info">
            Las cuentas de administrador, operador logístico y mecánico son
            creadas internamente por un administrador.
          </p>

          <p className="auth-switch">
            ¿Ya tenés cuenta? <Link to="/login">Iniciá sesión</Link>
          </p>
        </div>
      </div>
    </section>
  );
}

export default RegistroPage;