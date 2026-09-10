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
  GoogleAuthProvider,
  signInWithEmailAndPassword,
  signInWithPopup,
} from "firebase/auth";
import "./LoginPage.css";
import logoTrukly from "../assets/logo-trukly.png";
import { useAuth } from "../context/AuthContext";
import { auth } from "../firebase";

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

  const loginBackendTradicional = async () => {
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

    login(data.token, data.usuario);
    setMensaje("Inicio de sesión correcto");
    redirigirPorRol(data.usuario.rol);
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

    login(data.token, data.usuario);
    setMensaje("Inicio de sesión correcto");
    redirigirPorRol(data.usuario.rol);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setMensaje("");
    setError("");

    try {
      const credencial = await signInWithEmailAndPassword(
        auth,
        formulario.email,
        formulario.password
      );

      const firebaseToken = await credencial.user.getIdToken();
      await loginConBackendFirebase(firebaseToken);
    } catch {
      try {
        await loginBackendTradicional();
      } catch {
        setError("No se pudo iniciar sesión con Firebase o con el backend");
      }
    }
  };

  const handleGoogleLogin = async () => {
    setMensaje("");
    setError("");

    try {
      const credencial = await signInWithPopup(auth, googleProvider);
      const firebaseToken = await credencial.user.getIdToken();

      await loginConBackendFirebase(firebaseToken);
    } catch {
      setError("No se pudo iniciar sesión con Google");
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
                <input type="checkbox" />
                <span>Recordarme</span>
              </label>
              <a href="#contacto">Necesito ayuda</a>
            </div>

            <button type="submit">Entrar</button>
          </form>

          <div className="auth-divider">
            <span>o</span>
          </div>

          <button
            type="button"
            className="auth-google-button"
            onClick={handleGoogleLogin}
          >
            <FaGoogle />
            Continuar con Google
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
