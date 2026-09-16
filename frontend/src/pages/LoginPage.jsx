import { useState } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import {
  FaBolt,
  FaClipboardList,
  FaGoogle,
  FaMapMarkerAlt,
  FaTools,
} from "react-icons/fa";
import {
  browserLocalPersistence,
  browserSessionPersistence,
  GoogleAuthProvider,
  sendPasswordResetEmail,
  signInWithEmailAndPassword,
  signInWithPopup,
  setPersistence,
} from "firebase/auth";
import "./LoginPage.css";
import logoTrukly from "../assets/logo-trukly.png";
import { useAuth } from "../context/AuthContext";
import { auth } from "../firebase";
import { obtenerMensajeAuth } from "../utils/authErrors";

function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const params = new URLSearchParams(location.search);
  const sesionExpirada = params.get("sesionExpirada");

  const [formulario, setFormulario] = useState({
    email: "",
    password: "",
  });

  const [mensaje, setMensaje] = useState("");
  const [error, setError] = useState("");
  const [googleProcesando, setGoogleProcesando] = useState(false);
  const [recordarSesion, setRecordarSesion] = useState(true);
  const [emailRecuperacion, setEmailRecuperacion] = useState("");
  const [mostrarRecuperacion, setMostrarRecuperacion] = useState(false);
  const [enviandoRecuperacion, setEnviandoRecuperacion] = useState(false);
  const googleProvider = new GoogleAuthProvider();

  const handleChange = (e) => {
    setFormulario({
      ...formulario,
      [e.target.name]: e.target.value,
    });
  };

  const redirigirPorRol = (rol) => {
    if (rol === "admin") {
      navigate("/dashboardAdmin");
    } else if (rol === "chofer") {
      navigate("/dashboardTrucker");
    } else if (rol === "mecanico") {
      navigate("/dashboardMechanic");
    } else if (rol === "operador") {
      navigate("/dashboardOperator");
    } else {
      navigate("/dashboardTrucker");
    }
  };

  const loginConBackendFirebase = async (firebaseToken) => {
    const respuesta = await fetch("http://localhost:5000/api/auth/firebase-login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ token: firebaseToken }),
    });

    const data = await respuesta.json();

    if (!respuesta.ok) {
      throw new Error(data.mensaje || "No se pudo iniciar sesión");
    }

    login(data.token, data.usuario, recordarSesion);
    setMensaje("Inicio de sesión correcto");
    redirigirPorRol(data.usuario.rol);
  };

  const loginConBackendTradicional = async () => {
    const respuesta = await fetch("http://localhost:5000/api/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username: formulario.email,
        password: formulario.password,
      }),
    });

    const data = await respuesta.json();

    if (!respuesta.ok) {
      throw new Error(data.mensaje || "No se pudo iniciar sesión");
    }

    login(data.token, data.usuario, recordarSesion);
    setMensaje("Inicio de sesión correcto");
    redirigirPorRol(data.usuario.rol);
  };

  const aplicarPersistenciaFirebase = async () => {
    await setPersistence(
      auth,
      recordarSesion ? browserLocalPersistence : browserSessionPersistence
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setMensaje("");
    setError("");

    try {
      await aplicarPersistenciaFirebase();

      const credencial = await signInWithEmailAndPassword(
        auth,
        formulario.email,
        formulario.password
      );

      const firebaseToken = await credencial.user.getIdToken();
      await loginConBackendFirebase(firebaseToken);
    } catch (error) {
      try {
        await loginConBackendTradicional();
      } catch (errorBackend) {
        const mensajeFirebase = obtenerMensajeAuth(
          error,
          "No se pudo iniciar sesión"
        );

        setError(errorBackend.message || mensajeFirebase);
      }
    }
  };

  const handleGoogleLogin = async () => {
    if (googleProcesando) return;

    setMensaje("");
    setError("");
    setGoogleProcesando(true);

    try {
      await aplicarPersistenciaFirebase();

      const credencial = await signInWithPopup(auth, googleProvider);
      const firebaseToken = await credencial.user.getIdToken();

      await loginConBackendFirebase(firebaseToken);
    } catch (error) {
      setError(obtenerMensajeAuth(error, "No se pudo iniciar sesión con Google"));
    } finally {
      setGoogleProcesando(false);
    }
  };

  const recuperarPassword = async (e) => {
    e.preventDefault();

    try {
      setMensaje("");
      setError("");
      setEnviandoRecuperacion(true);

      await sendPasswordResetEmail(
        auth,
        emailRecuperacion || formulario.email
      );

      setMensaje("Te enviamos un email para recuperar tu contraseña.");
      setMostrarRecuperacion(false);
    } catch (error) {
      setError(obtenerMensajeAuth(error, "No se pudo enviar el email de recuperación"));
    } finally {
      setEnviandoRecuperacion(false);
    }
  };

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

          <form className="auth-form" onSubmit={handleSubmit}>
            <label className="auth-field" htmlFor="email">
              <span>Email</span>
              <input
                type="email"
                id="email"
                name="email"
                value={formulario.email}
                onChange={handleChange}
                placeholder="tu@email.com"
              />
            </label>

            <label className="auth-field" htmlFor="password">
              <span>Contraseña</span>
              <input
                type="password"
                id="password"
                name="password"
                value={formulario.password}
                onChange={handleChange}
                placeholder="••••••••"
              />
            </label>

            <div className="auth-options">
              <label className="auth-check">
                <input
                  type="checkbox"
                  checked={recordarSesion}
                  onChange={(e) => setRecordarSesion(e.target.checked)}
                />
                <span>Recordarme</span>
              </label>
              <button
                type="button"
                className="auth-link-button"
                onClick={() => {
                  setEmailRecuperacion(formulario.email);
                  setMostrarRecuperacion((visible) => !visible);
                }}
              >
                Olvidé mi contraseña
              </button>
            </div>

            <button type="submit">Entrar</button>
          </form>

          {mostrarRecuperacion && (
            <form className="auth-reset-form" onSubmit={recuperarPassword}>
              <label className="auth-field" htmlFor="email-recuperacion">
                <span>Email</span>
                <input
                  type="email"
                  id="email-recuperacion"
                  value={emailRecuperacion}
                  onChange={(e) => setEmailRecuperacion(e.target.value)}
                  placeholder="tu@email.com"
                  required
                />
              </label>

              <button type="submit" disabled={enviandoRecuperacion}>
                {enviandoRecuperacion ? "Enviando..." : "Enviar recuperación"}
              </button>
            </form>
          )}

          <div className="auth-divider">
            <span>o</span>
          </div>

          <button
            type="button"
            className="auth-google-button"
            onClick={handleGoogleLogin}
            disabled={googleProcesando}
          >
            <FaGoogle />
            {googleProcesando ? "Conectando..." : "Continuar con Google"}
          </button>

          {sesionExpirada && (
            <p className="login-mensaje error">
              Tu sesión expiró, volvé a iniciar sesión.
            </p>
          )}

          {mensaje && <p className="login-mensaje exito">{mensaje}</p>}
          {error && <p className="login-mensaje error">{error}</p>}

          <p className="auth-switch">
            ¿Todavía no tenés cuenta? <Link to="/registro">Solicitá acceso</Link>
          </p>
        </div>
      </div>
    </section>
  );
}

export default LoginPage;
