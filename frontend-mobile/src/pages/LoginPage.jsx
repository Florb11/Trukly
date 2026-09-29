import { useState } from "react";
import { FaEye, FaEyeSlash, FaLock, FaTruck } from "react-icons/fa";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { API_URL } from "../utils/api";

export default function LoginPage() {
  const { token, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ username: "", password: "" });
  const [mostrar, setMostrar] = useState(false);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState("");

  if (token) return <Navigate to="/" replace />;

  const submit = async (event) => {
    event.preventDefault();
    setCargando(true);
    setError("");
    try {
      const response = await fetch(`${API_URL}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.mensaje || "No se pudo iniciar sesión");
      if (data.usuario?.rol !== "chofer") throw new Error("Esta aplicación es para cuentas de chofer.");
      login(data.token, data.usuario);
      navigate("/", { replace: true });
    } catch (err) { setError(err.message); } finally { setCargando(false); }
  };

  const params = new URLSearchParams(location.search);
  return (
    <main className="login-page">
      <section className="login-brand">
        <img src="/pwa-192.png" alt="Logo de Trukly" />
        <span>TRUKLY MOBILE</span>
        <h1>Tu operación, desde el camino.</h1>
        <p>Consultá viajes, registrá movimientos y reportá fallas desde el celular.</p>
      </section>
      <section className="login-card">
        <div className="login-card-title"><FaTruck /><div><h2>Iniciar sesión</h2><p>Ingresá con tu cuenta de chofer.</p></div></div>
        {(params.get("sesionExpirada") || params.get("rolInvalido")) && <p className="feedback error">Volvé a iniciar sesión con una cuenta de chofer.</p>}
        {error && <p className="feedback error">{error}</p>}
        <form onSubmit={submit}>
          <label>Usuario o email<input value={form.username} onChange={(event) => setForm({ ...form, username: event.target.value })} autoComplete="username" required /></label>
          <label>Contraseña<div className="password-field"><FaLock /><input type={mostrar ? "text" : "password"} value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} autoComplete="current-password" required /><button type="button" onClick={() => setMostrar(!mostrar)} aria-label={mostrar ? "Ocultar contraseña" : "Mostrar contraseña"}>{mostrar ? <FaEyeSlash /> : <FaEye />}</button></div></label>
          <button className="button primary wide" disabled={cargando}>{cargando ? "Ingresando..." : "Entrar"}</button>
        </form>
      </section>
    </main>
  );
}
