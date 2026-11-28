import {
  EmailAuthProvider,
  GoogleAuthProvider,
  linkWithPopup,
  reauthenticateWithCredential,
  reauthenticateWithPopup,
  signInWithEmailAndPassword,
  signInWithPopup,
  signOut,
  unlink,
} from "firebase/auth";
import { auth } from "../firebase";

function proveedorGoogle(email) {
  const proveedor = new GoogleAuthProvider();
  proveedor.setCustomParameters({ prompt: "select_account", login_hint: email });
  return proveedor;
}

function googleVinculado(cuenta) {
  return cuenta?.providerData.find((proveedor) => proveedor.providerId === "google.com");
}

async function comprobarCuenta(cuenta, perfil) {
  if (cuenta.uid !== perfil.firebase_uid) {
    await signOut(auth).catch(() => {});
    throw new Error("La cuenta elegida no corresponde a tu perfil.");
  }
  return cuenta;
}

export async function confirmarPassword(perfil, password) {
  await auth.authStateReady();
  const actual = auth.currentUser;
  const resultado = actual?.uid === perfil.firebase_uid
    ? await reauthenticateWithCredential(actual, EmailAuthProvider.credential(actual.email, password))
    : await signInWithEmailAndPassword(auth, perfil.email, password);
  return comprobarCuenta(resultado.user, perfil);
}

export async function confirmarGoogle(perfil) {
  const actual = auth.currentUser?.uid === perfil.firebase_uid ? auth.currentUser : null;
  const proveedor = proveedorGoogle(googleVinculado(actual)?.email || perfil.email);
  const resultado = actual
    ? await reauthenticateWithPopup(actual, proveedor)
    : await signInWithPopup(auth, proveedor);
  return comprobarCuenta(resultado.user, perfil);
}

export async function elegirGoogleParaVincular(cuenta, perfil) {
  const existente = googleVinculado(cuenta);
  const correo = perfil.email.toLowerCase();
  if (existente && existente.email?.toLowerCase() !== correo) {
    throw new Error("Quitá el vínculo pendiente para elegir Google con el mismo correo del perfil.");
  }

  const proveedor = proveedorGoogle(perfil.email);
  if (existente) {
    const resultado = await reauthenticateWithPopup(cuenta, proveedor);
    return comprobarCuenta(resultado.user, perfil);
  }

  const resultado = await linkWithPopup(cuenta, proveedor);
  const usuario = await comprobarCuenta(resultado.user, perfil);
  if (googleVinculado(usuario)?.email?.toLowerCase() !== correo) {
    try {
      await unlink(usuario, "google.com");
    } catch {
      throw new Error("Quitá el vínculo pendiente para elegir Google con el mismo correo del perfil.");
    }
    throw new Error("Elegí la cuenta de Google que usa el mismo correo que tu perfil.");
  }

  const credencial = GoogleAuthProvider.credentialFromResult(resultado);
  if (!credencial) throw new Error("Volvé a confirmar tu cuenta de Google para completar la vinculación.");
  const confirmacion = await reauthenticateWithCredential(usuario, credencial);
  return comprobarCuenta(confirmacion.user, perfil);
}

const mensajes = {
  "auth/invalid-credential": "La contraseña no es correcta.",
  "auth/wrong-password": "La contraseña no es correcta.",
  "auth/user-mismatch": "La cuenta elegida no corresponde a tu perfil.",
  "auth/popup-closed-by-user": "Cerraste la ventana de Google antes de confirmar.",
  "auth/popup-blocked": "Permití que el navegador abra la ventana de Google y volvé a intentar.",
  "auth/cancelled-popup-request": "Ya hay una ventana de Google abierta.",
  "auth/credential-already-in-use": "Esa cuenta de Google está vinculada a otro perfil.",
  "auth/email-already-in-use": "Ese correo ya está registrado.",
  "auth/requires-recent-login": "Volvé a confirmar tu identidad e intentá nuevamente.",
  "auth/user-token-expired": "Volvé a iniciar sesión para continuar.",
  "auth/network-request-failed": "Revisá tu conexión y volvé a intentar.",
};

export function mensajeAcceso(error) {
  if (mensajes[error.code]) return mensajes[error.code];
  if (error.code || ["TypeError", "TimeoutError"].includes(error.name)) {
    return "No se pudo completar la acción. Revisá tu conexión y volvé a intentar.";
  }
  return error.message;
}
