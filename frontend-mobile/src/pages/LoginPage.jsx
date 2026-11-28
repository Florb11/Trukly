import { useState } from "react";
import { FaEye, FaEyeSlash, FaGoogle, FaLock, FaTruck } from "react-icons/fa";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { GoogleAuthProvider, sendPasswordResetEmail, signInWithEmailAndPassword, signInWithPopup, signOut } from "firebase/auth";
import { useAuth } from "../context/AuthContext";
import { auth } from "../firebase";
import { API_URL } from "../utils/api";
import ThemeToggle from "../components/ThemeToggle";

export default function LoginPage() {
  const { token, usuario, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ username: "", password: "" });
  const [mostrar, setMostrar] = useState(false);
  const [cargando, setCargando] = useState(false);
  const [googleProcesando, setGoogleProcesando] = useState(false);
  const [error, setError] = useState("");
  const [mostrarRecuperacion, setMostrarRecuperacion] = useState(false);
  const [correoRecuperacion, setCorreoRecuperacion] = useState("");
  const [recuperando, setRecuperando] = useState(false);
  const [mensaje, setMensaje] = useState("");

  if (token && ["chofer", "mecanico", "operador"].includes(usuario?.rol)) return <Navigate to="/" replace />;

  const submit = async (event) => {
    event.preventDefault();
    setCargando(true);
    setError("");
    setMensaje("");
    try {
      const response = await fetch(`${API_URL}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      let data = await response.json();
      if ([401, 409].includes(response.status) && form.username.includes("@")) {
        try {
          const credencial = await signInWithEmailAndPassword(auth, form.username, form.password);
          const firebaseToken = await credencial.user.getIdToken();
          const firebaseResponse = await fetch(`${API_URL}/api/auth/firebase-login`, {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ token: firebaseToken }), signal: AbortSignal.timeout(20000),
          });
          let firebaseData = await firebaseResponse.json();
          if (firebaseResponse.status === 409 && firebaseData.codigo === "migracion_pendiente") {
            const migracion = await fetch(`${API_URL}/api/auth/login`, {
              method: "POST", headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ ...form, firebaseToken }), signal: AbortSignal.timeout(20000),
            });
            firebaseData = await migracion.json();
            if (!migracion.ok) throw new Error(firebaseData.mensaje || "No se pudo vincular el acceso.");
          } else
          if (!firebaseResponse.ok) throw new Error(firebaseData.mensaje || "No se pudo iniciar sesión");
          if (!["chofer", "mecanico", "operador"].includes(firebaseData.usuario?.rol)) throw new Error("Tu rol no tiene acceso a mobile.");
          login(firebaseData.token, firebaseData.usuario);
          navigate("/", { replace: true });
          return;
        } catch (err) {
          throw new Error(err.code ? data.mensaje : err.message, { cause: err });
        }
      }
      if (!response.ok) throw new Error(data.mensaje || "No se pudo iniciar sesión");
      if (!["chofer", "mecanico", "operador"].includes(data.usuario?.rol)) throw new Error("Ingresá con una cuenta de chofer, mecánico u operador.");
      login(data.token, data.usuario);
      navigate("/", { replace: true });
    } catch (err) { setError(err.message); } finally { setCargando(false); }
  };

  const loginGoogle = async () => {
    if (googleProcesando) return;
    setGoogleProcesando(true);
    setError("");
    setMensaje("");

    try {
      const credencial = await signInWithPopup(auth, new GoogleAuthProvider());
      const firebaseToken = await credencial.user.getIdToken();
      const response = await fetch(`${API_URL}/api/auth/firebase-login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token: firebaseToken }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.mensaje || "No se pudo iniciar sesión con Google");
      if (!["chofer", "mecanico", "operador"].includes(data.usuario?.rol)) {
        await signOut(auth);
        throw new Error("Ingresá con una cuenta de chofer, mecánico u operador.");
      }
      login(data.token, data.usuario);
      navigate("/", { replace: true });
    } catch (err) {
      const mensajes = {
        "auth/popup-closed-by-user": "Se cerró la ventana de Google antes de completar el acceso.",
        "auth/popup-blocked": "El navegador bloqueó la ventana de Google. Permití popups para este sitio.",
        "auth/unauthorized-domain": "Este dominio no está autorizado en Firebase Authentication.",
        "auth/cancelled-popup-request": "Ya hay una ventana de Google abierta.",
      };
      setError(mensajes[err.code] || err.message || "No se pudo iniciar sesión con Google");
    } finally {
      setGoogleProcesando(false);
    }
  };

  const recuperarPassword = async (event) => {
    event.preventDefault();
    if (recuperando) return;
    const confirmacion = "Si el correo tiene acceso por contraseña, vas a recibir un enlace para recuperarla.";
    setRecuperando(true);
    setError("");
    setMensaje("");
    try {
      await sendPasswordResetEmail(auth, correoRecuperacion.trim());
      setMensaje(confirmacion);
      setMostrarRecuperacion(false);
    } catch (err) {
      if (err.code === "auth/user-not-found") {
        setMensaje(confirmacion);
        setMostrarRecuperacion(false);
      } else {
        setError("No se pudo enviar la recuperación. Volvé a intentarlo.");
      }
    } finally {
      setRecuperando(false);
    }
  };

  const params = new URLSearchParams(location.search);
  return (
    <main className="login-page">
      <div className="login-theme"><ThemeToggle /></div>
      <section className="login-brand">
        <img src="/pwa-192.png" alt="Logo de Trukly" />
        <span>TRUKLY MOBILE</span>
        <h1>Tu operación, desde el camino.</h1>
        <p>Consultá viajes, registrá movimientos y reportá fallas desde el celular.</p>
      </section>
      <section className="login-card">
        <div className="login-card-title"><FaTruck /><div><h2>Iniciar sesión</h2><p>Choferes, mecánicos y operadores.</p></div></div>
        {(params.get("sesionExpirada") || params.get("rolInvalido")) && <p className="feedback error">Volvé a iniciar sesión con una cuenta habilitada.</p>}
        {error && <p className="feedback error">{error}</p>}
        {mensaje && <p className="feedback ok" role="status">{mensaje}</p>}
        <form onSubmit={submit}>
          <label>Usuario o email<input value={form.username} onChange={(event) => setForm({ ...form, username: event.target.value })} autoComplete="username" required /></label>
          <label>Contraseña<div className="password-field"><FaLock /><input type={mostrar ? "text" : "password"} value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} autoComplete="current-password" required /><button type="button" onClick={() => setMostrar(!mostrar)} aria-label={mostrar ? "Ocultar contraseña" : "Mostrar contraseña"}>{mostrar ? <FaEyeSlash /> : <FaEye />}</button></div></label>
          <button className="button primary wide" disabled={cargando}>{cargando ? "Ingresando..." : "Entrar"}</button>
        </form>
        {mostrarRecuperacion ? (
          <form onSubmit={recuperarPassword}>
            <label>
              Correo de recuperación
              <input type="email" autoComplete="email" value={correoRecuperacion} required
                onChange={(event) => setCorreoRecuperacion(event.target.value)} />
            </label>
            <button className="button primary wide" type="submit" disabled={recuperando}>
              {recuperando ? "Enviando..." : "Enviar recuperación"}
            </button>
            <button className="button secondary wide" type="button" disabled={recuperando}
              onClick={() => setMostrarRecuperacion(false)}>Cancelar</button>
          </form>
        ) : (
          <button className="button secondary wide" type="button" disabled={cargando || googleProcesando}
            onClick={() => {
              setCorreoRecuperacion(form.username.includes("@") ? form.username : "");
              setError("");
              setMensaje("");
              setMostrarRecuperacion(true);
            }}>Olvidé mi contraseña</button>
        )}
        <div className="login-divider"><span>o</span></div>
        <button className="button google wide" type="button" onClick={loginGoogle} disabled={googleProcesando || cargando}>
          <FaGoogle /> {googleProcesando ? "Conectando..." : "Continuar con Google"}
        </button>
        <Link className="button secondary wide" to="/registro">Solicitar acceso</Link>
      </section>
    </main>
  );
}
