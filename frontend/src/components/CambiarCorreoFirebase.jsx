import { useRef, useState } from "react";
import { EmailAuthProvider, GoogleAuthProvider, reauthenticateWithCredential,
  signInWithEmailAndPassword, signInWithPopup, verifyBeforeUpdateEmail, reload } from "firebase/auth";
import { auth } from "../firebase";
import "./CambiarCorreoFirebase.css";
import { enviarCambioCorreo } from "../utils/correoVerificado";

const mensajes = {
  "auth/invalid-credential": "La contraseña actual no es correcta.",
  "auth/wrong-password": "La contraseña actual no es correcta.",
  "auth/email-already-in-use": "Ese correo ya está registrado.",
  "auth/popup-closed-by-user": "Cerraste la confirmación de Google antes de terminar.",
  "auth/requires-recent-login": "Volvé a iniciar sesión y repetí el cambio de correo.",
  "auth/user-token-expired": "Volvé a iniciar sesión con el correo nuevo para actualizar tu perfil.",
  "auth/network-request-failed": "No se pudo conectar. Revisá tu conexión e intentá nuevamente.",
};

export default function CambiarCorreoFirebase({ perfil, solicitar, onActualizado }) {
  const [nuevo, setNuevo] = useState("");
  const [password, setPassword] = useState("");
  const [ocupado, setOcupado] = useState(false);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");
  const bloqueo = useRef(false);
  const pedir = async (ruta, datos) => {
    const r = await solicitar(ruta, { method: "POST", body: JSON.stringify(datos), signal: AbortSignal.timeout(20000) });
    if (!r) throw new Error("La sesión venció. Volvé a ingresar.");
    if (!(r.respuesta || r.response).ok) throw new Error(r.data.mensaje || "No se pudo confirmar el cambio.");
    return r.data;
  };
  const ejecutar = async (accion) => {
    if (bloqueo.current) return;
    bloqueo.current = true; setOcupado(true); setError(""); setMensaje("");
    try { await accion(); }
    catch (e) { setError(mensajes[e.code] || (["TypeError", "TimeoutError"].includes(e.name) ? "No se pudo confirmar el cambio. Revisá tu conexión." : e.message)); }
    finally { bloqueo.current = false; setOcupado(false); }
  };
  const enviar = (google = false) => ejecutar(async () => {
    const email = await enviarCambioCorreo({ nuevo, actual: perfil.email, uid: perfil.firebase_uid,
      autenticar: async () => {
        if (google) return (await signInWithPopup(auth, new GoogleAuthProvider())).user;
        if (!password) throw new Error("Ingresá tu contraseña actual o confirmá con Google.");
        await auth.authStateReady();
        const actual = auth.currentUser;
        const credencial = actual?.uid === perfil.firebase_uid
          ? await reauthenticateWithCredential(actual, EmailAuthProvider.credential(actual.email, password))
          : await signInWithEmailAndPassword(auth, perfil.email, password);
        return credencial.user;
      },
      comprobar: (email) => pedir("/api/perfil/correo/disponibilidad", { email }),
      enviar: (cuenta, email) => verifyBeforeUpdateEmail(cuenta, email),
    });
    setPassword("");
    setMensaje(`Enviamos un enlace a ${email}. Abrilo para confirmar. Luego actualizá el correo aquí o iniciá sesión con la dirección nueva.`);
  });
  const sincronizar = () => ejecutar(async () => {
    await auth.authStateReady();
    const actual = auth.currentUser;
    if (!actual || actual.uid !== perfil.firebase_uid) throw new Error("Iniciá sesión con el correo nuevo para actualizar tu perfil.");
    await reload(actual);
    if (!actual.emailVerified || actual.email.toLowerCase() === (perfil.email || "").toLowerCase()) {
      throw new Error("El correo nuevo todavía no está confirmado. Abrí el enlace que recibiste.");
    }
    const datos = await pedir("/api/perfil/correo/sincronizar", { firebaseToken: await actual.getIdToken(true) });
    onActualizado(datos.perfil);
    setNuevo(""); setPassword(""); setMensaje(datos.mensaje);
  });
  return <section className="cambiar-correo">
    <h2>Cambiar correo de acceso</h2>
    <p>Tu correo actual se conserva hasta que verifiques la dirección nueva.</p>
    {error && <p className="cambiar-correo__error" role="alert">{error}</p>}
    {mensaje && <p role="status">{mensaje}</p>}
    <form onSubmit={(e) => { e.preventDefault(); enviar(); }}>
      <fieldset disabled={ocupado}>
        <label>Nuevo correo<input type="email" value={nuevo} onChange={(e) => setNuevo(e.target.value)} required maxLength={150} autoComplete="email" /></label>
        <label>Contraseña actual<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" /></label>
      </fieldset>
      <div className="cambiar-correo__acciones">
        <button type="submit" disabled={ocupado}>Enviar verificación</button>
        <button type="button" disabled={ocupado} onClick={() => enviar(true)}>Confirmar con Google</button>
        <button type="button" disabled={ocupado} onClick={sincronizar}>Ya verifiqué, actualizar correo</button>
      </div>
    </form>
  </section>;
}
