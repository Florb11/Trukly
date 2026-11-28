import { useRef, useState } from "react";
import { reload, verifyBeforeUpdateEmail } from "firebase/auth";
import { auth } from "../firebase";
import { confirmarPassword, mensajeAcceso } from "../utils/firebasePerfil";
import { enviarCambioCorreo } from "../utils/correoVerificado";

export default function CambiarCorreoFirebase({ perfil, pedir, onActualizado }) {
  const clavePendiente = "trukly_correo_pendiente:" + perfil.firebase_uid;
  const [pendiente, setPendiente] = useState(() => sessionStorage.getItem(clavePendiente) === perfil.email);
  const [nuevo, setNuevo] = useState("");
  const [password, setPassword] = useState("");
  const [ocupado, setOcupado] = useState(false);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");
  const bloqueo = useRef(false);

  async function ejecutar(accion) {
    if (bloqueo.current) return;
    bloqueo.current = true;
    setOcupado(true);
    setError("");
    setMensaje("");
    try {
      await accion();
    } catch (err) {
      setError(mensajeAcceso(err));
    } finally {
      bloqueo.current = false;
      setOcupado(false);
    }
  }

  function enviar(event) {
    event.preventDefault();
    return ejecutar(async () => {
      const email = await enviarCambioCorreo({
        nuevo, actual: perfil.email, uid: perfil.firebase_uid,
        autenticar: () => confirmarPassword(perfil, password),
        comprobar: (direccion) => pedir("/api/perfil/correo/disponibilidad", "POST", { email: direccion }),
        enviar: (cuenta, direccion) => verifyBeforeUpdateEmail(cuenta, direccion),
      });
      sessionStorage.setItem(clavePendiente, perfil.email);
      setPassword("");
      setPendiente(true);
      setMensaje("Enviamos un enlace de verificación a " + email + ".");
    });
  }

  function sincronizar() {
    return ejecutar(async () => {
      await auth.authStateReady();
      const cuenta = auth.currentUser;
      if (!cuenta || cuenta.uid !== perfil.firebase_uid) {
        throw new Error("Después de verificar, ingresá con tu correo nuevo y tu contraseña.");
      }
      await reload(cuenta);
      if (!cuenta.emailVerified || cuenta.email?.toLowerCase() === perfil.email.toLowerCase()) {
        throw new Error("Abrí el enlace que recibiste en el correo nuevo y volvé a intentar.");
      }
      const datos = await pedir("/api/perfil/correo/sincronizar", "POST", {
        firebaseToken: await cuenta.getIdToken(true),
      });
      sessionStorage.removeItem(clavePendiente);
      setPendiente(false);
      setNuevo("");
      onActualizado(datos.perfil);
      setMensaje(datos.mensaje);
    });
  }

  return (
    <div className="metodos-acceso__detalle">
      <h3>Cambiar correo de acceso</h3>
      {error && <p className="metodos-acceso__error" role="alert">{error}</p>}
      {mensaje && <p role="status">{mensaje}</p>}
      {pendiente ? (
        <>
          <p>Abrí el enlace del correo nuevo para confirmar el cambio.</p>
          <div className="metodos-acceso__acciones">
            <button type="button" className="metodos-acceso__principal" onClick={sincronizar} disabled={ocupado}>
              {ocupado ? "Comprobando..." : "Ya verifiqué, actualizar correo"}
            </button>
            <button type="button" disabled={ocupado} onClick={() => {
              sessionStorage.removeItem(clavePendiente);
              setNuevo("");
              setPendiente(false);
              setError("");
              setMensaje("");
            }}>
              Usar otra dirección
            </button>
          </div>
        </>
      ) : (
        <form onSubmit={enviar} autoComplete="off">
          <fieldset disabled={ocupado}>
            <label>
              Nuevo correo
              <input type="email" name="nuevo_correo_acceso" value={nuevo}
                onChange={(event) => setNuevo(event.target.value)} autoComplete="off" required maxLength={150} />
            </label>
            <label>
              Contraseña actual
              <input type="password" name="confirmacion_cambio_correo" value={password}
                onChange={(event) => setPassword(event.target.value)} autoComplete="current-password" required />
            </label>
          </fieldset>
          <button type="submit" className="metodos-acceso__principal" disabled={ocupado}>
            {ocupado ? "Enviando..." : "Enviar verificación"}
          </button>
        </form>
      )}
    </div>
  );
}
