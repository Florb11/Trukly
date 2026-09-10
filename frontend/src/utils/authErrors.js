export const obtenerMensajeAuth = (error, mensajeFallback) => {
  const codigo = error?.code;

  if (codigo === "auth/popup-closed-by-user") {
    return "Se cerró la ventana de Google antes de completar el acceso.";
  }

  if (codigo === "auth/cancelled-popup-request") {
    return "Ya había una ventana de Google abierta. Cerrala o esperá unos segundos y volvé a intentar.";
  }

  if (codigo === "auth/popup-blocked") {
    return "El navegador bloqueó la ventana de Google. Permití popups para este sitio.";
  }

  if (codigo === "auth/unauthorized-domain") {
    return "Este dominio no está autorizado en Firebase Authentication.";
  }

  if (codigo === "auth/operation-not-allowed") {
    return "El proveedor de Google no está habilitado en Firebase Authentication.";
  }

  if (codigo === "auth/account-exists-with-different-credential") {
    return "Ya existe una cuenta con ese email usando otro método de inicio de sesión.";
  }

  if (codigo === "auth/email-already-in-use") {
    return "Ya existe una cuenta con ese email.";
  }

  if (codigo === "auth/invalid-email") {
    return "El email no tiene un formato válido.";
  }

  if (codigo === "auth/weak-password") {
    return "La contraseña es demasiado débil.";
  }

  if (codigo === "auth/user-not-found") {
    return "No existe una cuenta de Firebase con ese email.";
  }

  if (codigo === "auth/invalid-credential") {
    return "El email o la contraseña no son correctos.";
  }

  return error?.message || mensajeFallback;
};
