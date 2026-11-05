export async function enviarCambioCorreo({ nuevo, actual, uid, autenticar, comprobar, enviar }) {
  const email = nuevo.trim().toLowerCase();
  if (email.length > 150 || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email) || email === (actual || "").toLowerCase()) {
    throw new Error("Ingresá un correo nuevo válido y diferente al actual.");
  }
  const cuenta = await autenticar();
  if (cuenta.uid !== uid) throw new Error("La cuenta confirmada no corresponde a tu perfil.");
  await comprobar(email);
  await enviar(cuenta, email);
  return email;
}
