import { useState } from "react";
import { Link } from "react-router-dom";
import { FaGoogle, FaIdCard, FaShieldAlt, FaTruckMoving } from "react-icons/fa";
import {
  createUserWithEmailAndPassword,
  deleteUser,
  GoogleAuthProvider,
  signInWithPopup,
} from "firebase/auth";
import "./RegistroPage.css";
import logoTrukly from "../assets/logo-trukly.png";
import { auth } from "../firebase";

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
  const [firebaseTokenGoogle, setFirebaseTokenGoogle] = useState("");
  const registroConGoogle = !!firebaseTokenGoogle;
  const googleProvider = new GoogleAuthProvider();

  const handleChange = (e) => {
    setFormulario({
      ...formulario,
      [e.target.name]: e.target.value,
    });
  };

  const enviarRegistroAlBackend = async (firebaseToken) => {
    const datosPerfil = { ...formulario };
    delete datosPerfil.password;

    const respuesta = await fetch("http://localhost:5000/api/auth/registro-firebase", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        ...datosPerfil,
        firebaseToken,
      }),
    });

    const data = await respuesta.json();

    return { respuesta, data };
  };

  const limpiarFormulario = () => {
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
    setFirebaseTokenGoogle("");
  };

  const handleGoogleRegistro = async () => {
    setMensaje("");
    setError("");

    try {
      const credencial = await signInWithPopup(auth, googleProvider);
      const firebaseToken = await credencial.user.getIdToken();
      const [nombreGoogle = "", ...apellidosGoogle] = (
        credencial.user.displayName || ""
      ).split(" ");

      setFirebaseTokenGoogle(firebaseToken);
      setFormulario((formularioActual) => ({
        ...formularioActual,
        nombre: formularioActual.nombre || nombreGoogle,
        apellido: formularioActual.apellido || apellidosGoogle.join(" "),
        email: credencial.user.email || formularioActual.email,
        username:
          formularioActual.username ||
          (credencial.user.email ? credencial.user.email.split("@")[0] : ""),
        password: "",
      }));
      setMensaje("Cuenta de Google vinculada. Completá los datos de Trukly.");
    } catch {
      setError("No se pudo vincular la cuenta de Google");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setMensaje("");
    setError("");

    try {
      let credencial = null;
      let firebaseToken = firebaseTokenGoogle;

      if (!registroConGoogle) {
        credencial = await createUserWithEmailAndPassword(
          auth,
          formulario.email,
          formulario.password
        );
        firebaseToken = await credencial.user.getIdToken();
      }

      const { respuesta, data } = await enviarRegistroAlBackend(firebaseToken);

      if (respuesta.ok) {
        setMensaje(data.mensaje);
        limpiarFormulario();
      } else {
        if (credencial) {
          try {
            await deleteUser(credencial.user);
          } catch {
            // Si Firebase no permite borrar, el backend igual devuelve el error real.
          }
        }

        setError(data.mensaje || "No se pudo registrar el chofer");
      }
    } catch {
      setError("No se pudo registrar con Firebase o conectar con el backend");
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

          <button
            type="button"
            className="registro-google-button"
            onClick={handleGoogleRegistro}
          >
            <FaGoogle />
            Continuar con Google
          </button>

          <div className="registro-divider">
            <span>o completá el registro manual</span>
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
                readOnly={registroConGoogle}
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
    placeholder="Ej: ABC123"
    pattern="[A-Za-z0-9]+"
    title="La licencia solo puede contener letras y números, sin espacios ni guiones."
    aria-describedby="licencia-ayuda"
  />
  <small id="licencia-ayuda" className="registro-ayuda">
    La licencia solo puede contener letras y números, sin espacios ni guiones.
  </small>
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

            {!registroConGoogle && (
              <label className="registro-field" htmlFor="password-registro">
                <span>Contraseña</span>
                <input
                  type="password"
                  id="password-registro"
                  name="password"
                  value={formulario.password}
                  onChange={handleChange}
                  placeholder="Creá una contraseña"
                  pattern="(?=.*\d).{8,}"
                  title="La contraseña debe tener mínimo 8 caracteres y al menos un número."
                  aria-describedby="password-ayuda"
                />
                <small id="password-ayuda" className="registro-ayuda">
                  La contraseña debe tener mínimo 8 caracteres y al menos un número.
                </small>
              </label>
            )}

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
