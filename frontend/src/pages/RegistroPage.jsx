import { useRef, useState } from "react";
import { Link } from "react-router-dom";
import { FaEye, FaEyeSlash, FaGoogle, FaIdCard, FaShieldAlt, FaTruckMoving } from "react-icons/fa";
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  GoogleAuthProvider,
  signInWithPopup,
} from "firebase/auth";
import "./RegistroPage.css";
import logoTrukly from "../assets/logo-trukly.png";
import { auth } from "../firebase";
import { obtenerMensajeAuth } from "../utils/authErrors";
import { completarRegistro } from "../utils/authFlows";

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
  const [vinculandoGoogle, setVinculandoGoogle] = useState(false);
  const [mostrarPassword, setMostrarPassword] = useState(false);
  const [registrando, setRegistrando] = useState(false);
  const envioEnCurso = useRef(false);
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

    const respuesta = await fetch(`${import.meta.env.VITE_API_URL || "http://localhost:5000"}/api/auth/registro-firebase`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        ...datosPerfil,
        firebaseToken,
      }),
      signal: AbortSignal.timeout(20000),
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
    if (vinculandoGoogle || envioEnCurso.current) return;

    setMensaje("");
    setError("");
    setVinculandoGoogle(true);

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
      setMensaje("Cuenta de Google vinculada. Confirmá tus datos básicos.");
    } catch (error) {
      setError(obtenerMensajeAuth(error, "No se pudo vincular la cuenta de Google"));
    } finally {
      setVinculandoGoogle(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (envioEnCurso.current || vinculandoGoogle) return;
    envioEnCurso.current = true;
    setRegistrando(true);

    setMensaje("");
    setError("");

    try {
      const data = await completarRegistro({
        crearCuenta: async () => (await createUserWithEmailAndPassword(auth, formulario.email.trim(), formulario.password)).user,
        iniciarSesion: async () => (await signInWithEmailAndPassword(auth, formulario.email.trim(), formulario.password)).user,
        obtenerCuentaGoogle: registroConGoogle ? async () => {
          await auth.authStateReady();
          if (!auth.currentUser) throw new Error("Volvé a vincular tu cuenta de Google.");
          return auth.currentUser;
        } : null,
        enviarRegistro: enviarRegistroAlBackend,
      });
      setMensaje(data.mensaje);
      limpiarFormulario();
    } catch (error) {
      setError(["TypeError", "TimeoutError"].includes(error.name)
        ? "No se pudo confirmar el registro. Revisá tu conexión y volvé a enviarlo con los mismos datos."
        : obtenerMensajeAuth(error, "No se pudo completar el registro."));
    } finally {
      envioEnCurso.current = false;
      setRegistrando(false);
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
              <p>Nombre, usuario y email para iniciar la solicitud de alta.</p>
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
            disabled={vinculandoGoogle || registrando}
          >
            <FaGoogle />
            {vinculandoGoogle ? "Conectando..." : "Continuar con Google"}
          </button>

          <div className="registro-divider">
            <span>
              {registroConGoogle
                ? "confirmá tus datos básicos"
                : "o registrate con email"}
            </span>
          </div>

          <form className="registro-form" onSubmit={handleSubmit}>
            <div className="registro-row">
              <label className="registro-field" htmlFor="nombre">
                <span>Nombre</span>
                <input
                  type="text"
                  id="nombre"
                  name="nombre"
                  required
                  maxLength={100}
                  pattern="[\p{L} ]+"
                  title="Solo letras y espacios, incluidas tildes y ñ. Sin números ni símbolos."
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
                  required
                  maxLength={100}
                  pattern="[\p{L} ]+"
                  title="Solo letras y espacios, incluidas tildes y ñ. Sin números ni símbolos."
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

            {!registroConGoogle && (
              <label className="registro-field" htmlFor="password-registro">
                <span>Contraseña</span>
                <div className="registro-password-field">
                  <input
                    type={mostrarPassword ? "text" : "password"}
                    id="password-registro"
                    name="password"
                    value={formulario.password}
                    onChange={handleChange}
                    placeholder="Creá una contraseña"
                    pattern="(?=.*\d).{8,}"
                    title="La contraseña debe tener mínimo 8 caracteres y al menos un número."
                    aria-describedby="password-ayuda"
                  />
                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() => setMostrarPassword((visible) => !visible)}
                    aria-label={mostrarPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
                    aria-pressed={mostrarPassword}
                  >
                    {mostrarPassword ? <FaEyeSlash /> : <FaEye />}
                  </button>
                </div>
                <small id="password-ayuda" className="registro-ayuda">
                  La contraseña debe tener mínimo 8 caracteres y al menos un número.
                </small>
              </label>
            )}

            <button type="submit" disabled={registrando || vinculandoGoogle}>
              {registroConGoogle ? "Solicitar alta con Google" : "Solicitar registro"}
            </button>
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
