import { useRef, useState } from "react";
import { Link } from "react-router-dom";
import { createUserWithEmailAndPassword, GoogleAuthProvider, signInWithPopup } from "firebase/auth";
import { FaGoogle } from "react-icons/fa";
import { auth } from "../firebase";
import { API_URL } from "../utils/api";
import ThemeToggle from "../components/ThemeToggle";

export default function RegistroPage() {
  const [form, setForm] = useState({ nombre: "", apellido: "", username: "", email: "", password: "" });
  const credencial = useRef(null);
  const [vinculado, setVinculado] = useState(false);
  const [google, setGoogle] = useState(false);
  const [ocupado, setOcupado] = useState(false);
  const [error, setError] = useState("");
  const [enviado, setEnviado] = useState(false);
  const vincular = async () => {
    setOcupado(true); setError("");
    try {
      const resultado = await signInWithPopup(auth, new GoogleAuthProvider());
      credencial.current = resultado.user;
      setVinculado(true);
      const [nombre = "", ...apellido] = (resultado.user.displayName || "").split(" ");
      setForm((actual) => ({ ...actual, nombre: actual.nombre || nombre, apellido: actual.apellido || apellido.join(" "), email: resultado.user.email || "", password: "" }));
      setGoogle(true);
    } catch { setError("No se pudo vincular Google. Volvé a intentar."); }
    finally { setOcupado(false); }
  };
  const enviar = async (event) => {
    event.preventDefault();
    if (ocupado) return;
    setOcupado(true); setError("");
    try {
      if (!credencial.current) {
        const resultado = await createUserWithEmailAndPassword(auth, form.email, form.password);
        credencial.current = resultado.user;
        setVinculado(true);
      }
      const firebaseToken = await credencial.current.getIdToken();
      const respuesta = await fetch(`${API_URL}/api/auth/registro-firebase`, {
        method: "POST", headers: { "Content-Type": "application/json" }, signal: AbortSignal.timeout(20000),
        body: JSON.stringify({ nombre: form.nombre, apellido: form.apellido, username: form.username, email: form.email, firebaseToken }),
      });
      const datos = await respuesta.json();
      if (!respuesta.ok) throw new Error(datos.mensaje || "No se pudo enviar la solicitud.");
      setEnviado(true);
    } catch (err) {
      const mensajes = {
        "auth/email-already-in-use": "Este email ya tiene una cuenta. Ingresá con ella o solicitá ayuda al administrador.",
        "auth/weak-password": "La contraseña es demasiado débil.",
      };
      setError(mensajes[err.code] || (["TypeError", "TimeoutError", "SyntaxError"].includes(err.name)
        ? "No se pudo confirmar la solicitud. Consultá con el administrador antes de volver a enviarla." : err.message));
    } finally { setOcupado(false); }
  };
  return <main className="login-page">
    <div className="login-theme"><ThemeToggle /></div>
    <section className="login-card"><h1>Solicitar acceso</h1><p>Alta de chofer</p>
      {enviado ? <><p className="feedback ok" role="status">Solicitud enviada. El administrador debe aprobar tu cuenta. Después completá tu licencia y legajo en Perfil.</p><Link className="button secondary wide" to="/login">Volver al login</Link></> : <>
        {error && <p className="feedback error" role="alert">{error}</p>}
        <p>Tu solicitud quedará pendiente de aprobación.</p>
        {!vinculado && <button type="button" className="button google wide" disabled={ocupado} onClick={vincular}><FaGoogle /> Continuar con Google</button>}
        <form onSubmit={enviar}><fieldset disabled={ocupado} className="registration-fields">
          {[["nombre", "Nombre", "text"], ["apellido", "Apellido", "text"], ["username", "Usuario", "text"], ["email", "Email", "email"]].map(([campo, texto, tipo]) => <label key={campo}>{texto}<input required type={tipo} readOnly={campo === "email" && vinculado} value={form[campo]} onChange={(event) => setForm({ ...form, [campo]: event.target.value })} /></label>)}
          {!google && !vinculado && <label>Contraseña<input required type="password" minLength={8} pattern="(?=.*[0-9]).{8,}" title="Mínimo 8 caracteres y un número" autoComplete="new-password" value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} /></label>}
          <button className="button primary wide">{ocupado ? "Enviando..." : "Solicitar acceso"}</button>
        </fieldset></form>
        <Link className="button secondary wide" to="/login">Ya tengo cuenta</Link>
      </>}
    </section>
  </main>;
}
