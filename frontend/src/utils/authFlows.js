// Un reintento confirma la misma identidad; nunca elimina una cuenta de Firebase.
export async function completarRegistro({ crearCuenta, iniciarSesion, obtenerCuentaGoogle, enviarRegistro }) {
  let cuenta;
  if (obtenerCuentaGoogle) {
    cuenta = await obtenerCuentaGoogle();
  } else {
    try {
      cuenta = await crearCuenta();
    } catch (error) {
      if (error.code !== "auth/email-already-in-use") throw error;
      cuenta = await iniciarSesion();
    }
  }
  const token = await cuenta.getIdToken(true);
  const { respuesta, data } = await enviarRegistro(token);
  if (!respuesta.ok) throw new Error(data.mensaje || "No se pudo completar el registro. Volvé a intentarlo.");
  return data;
}

export async function iniciarSesionConRespaldo({ autenticarFirebase, loginFirebase, loginLocal }) {
  let token = null;
  try {
    token = await autenticarFirebase();
    return await loginFirebase(token);
  } catch (error) {
    // Una identidad válida no debe ocultar rechazos de aprobación, permisos o red.
    if (token && !(error.status === 409 && error.codigo === "migracion_pendiente")) throw error;
    try {
      return await loginLocal(token);
    } catch (errorLocal) {
      if (errorLocal.status === 401 && error.code === "auth/invalid-credential") throw error;
      throw errorLocal;
    }
  }
}
