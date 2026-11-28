import { useCallback, useEffect, useRef, useState } from "react";
import { FaGoogle } from "react-icons/fa";
import CambiarCorreoFirebase from "./CambiarCorreoFirebase";
import {
  confirmarGoogle, confirmarPassword, elegirGoogleParaVincular, mensajeAcceso,
} from "../utils/firebasePerfil";
import "./CambiarCorreoFirebase.css";

const nombres = {
  vincular: "Vincular Google",
  desvincular: "Desvincular Google",
  configurar: "Configurar contraseña",
  password: "Cambiar contraseña",
  correo: "Cambiar correo de acceso",
};

function BotonGoogle({ children, destacado = false, type = "button", onClick, disabled }) {
  const clase = destacado
    ? "metodos-acceso__google metodos-acceso__google--destacado"
    : "metodos-acceso__google";

  return (
    <button type={type} className={clase} onClick={onClick} disabled={disabled}>
      <span className="metodos-acceso__google-icono" aria-hidden="true">
        <FaGoogle focusable="false" />
      </span>
      <span className="metodos-acceso__google-texto">{children}</span>
    </button>
  );
}

export default function MetodosAcceso({ perfil, solicitar, onActualizado }) {
  const [acceso, setAcceso] = useState(null);
  const [errorConsulta, setErrorConsulta] = useState("");
  const [accion, setAccion] = useState("");
  const [password, setPassword] = useState("");
  const [nueva, setNueva] = useState("");
  const [confirmacion, setConfirmacion] = useState("");
  const [vinculo, setVinculo] = useState(null);
  const [ocupado, setOcupado] = useState(false);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");
  const bloqueo = useRef(false);

  const pedir = useCallback(async (ruta, method = "GET", datos) => {
    const respuesta = await solicitar(ruta, {
      method,
      ...(datos ? { body: JSON.stringify(datos) } : {}),
      signal: AbortSignal.timeout(20000),
    });
    if (!respuesta) throw new Error("La sesión venció. Volvé a ingresar.");
    if (!(respuesta.respuesta || respuesta.response).ok) {
      throw new Error(respuesta.data.mensaje || "No se pudo completar la acción.");
    }
    return respuesta.data;
  }, [solicitar]);

  useEffect(() => {
    if (!perfil.firebase_uid) return;
    let vigente = true;
    pedir("/api/perfil/acceso")
      .then((datos) => { if (vigente) setAcceso(datos.acceso); })
      .catch((err) => { if (vigente) setErrorConsulta(mensajeAcceso(err)); });
    return () => { vigente = false; };
  }, [pedir, perfil.firebase_uid]);

  async function cargarAcceso() {
    try {
      const datos = await pedir("/api/perfil/acceso");
      setAcceso(datos.acceso);
      setErrorConsulta("");
    } catch (err) {
      setAcceso(null);
      setErrorConsulta(mensajeAcceso(err));
    }
  }

  function abrir(nuevaAccion) {
    setAccion(nuevaAccion);
    setPassword("");
    setNueva("");
    setConfirmacion("");
    setVinculo(null);
    setError("");
    setMensaje("");
  }

  async function ejecutar(operacion, actualizarAcceso = false) {
    if (bloqueo.current) return;
    bloqueo.current = true;
    setOcupado(true);
    setError("");
    setMensaje("");
    try {
      const resultado = await operacion();
      if (resultado) {
        abrir("");
        setMensaje(resultado.mensaje);
      }
    } catch (err) {
      setError(mensajeAcceso(err));
    } finally {
      if (actualizarAcceso) await cargarAcceso();
      bloqueo.current = false;
      setOcupado(false);
    }
  }

  function enviar(event) {
    event.preventDefault();

    if (accion === "vincular" && vinculo) {
      return ejecutar(async () => {
        const cuenta = await elegirGoogleParaVincular(vinculo.cuenta, perfil);
        return pedir("/api/perfil/acceso/google", "POST", {
          firebaseTokenPassword: vinculo.token,
          firebaseTokenGoogle: await cuenta.getIdToken(true),
        });
      }, true);
    }

    return ejecutar(async () => {
      if (accion === "vincular") {
        const cuenta = await confirmarPassword(perfil, password);
        setVinculo({ cuenta, token: await cuenta.getIdToken(true) });
        setPassword("");
        return;
      }

      if (accion === "desvincular") {
        const cuenta = await confirmarPassword(perfil, password);
        return pedir("/api/perfil/acceso/google", "DELETE", { firebaseToken: await cuenta.getIdToken(true) });
      }

      if (nueva !== confirmacion) throw new Error("Las contraseñas nuevas no coinciden.");
      const datos = { password_nueva: nueva, confirmar_password: confirmacion };
      if (accion === "configurar") {
        const cuenta = await confirmarGoogle(perfil);
        datos.firebaseToken = await cuenta.getIdToken(true);
        return pedir("/api/perfil/acceso/password", "POST", datos);
      }

      if (perfil.firebase_uid && !perfil.password_local) {
        const cuenta = await confirmarPassword(perfil, password);
        datos.firebaseToken = await cuenta.getIdToken(true);
      }
      return pedir("/api/perfil/password", "PUT", { ...datos, password_actual: password });
    }, accion === "configurar" || accion === "desvincular");
  }

  const google = acceso?.google_vinculado;
  const tienePassword = acceso?.tiene_password;
  const accesoListo = !perfil.firebase_uid || !!acceso;
  const puedeCambiarPassword = accesoListo && !google && (tienePassword || perfil.password_local);
  const puedeCambiarCorreo = !google && tienePassword && !!perfil.email;
  const googlePendiente = !google && acceso?.google_en_firebase;
  const muestraPassword = accion === "password" || accion === "desvincular" || (accion === "vincular" && !vinculo);
  const muestraNueva = accion === "configurar" || accion === "password";
  const confirmaConGoogle = accion === "configurar" || (accion === "vincular" && vinculo);
  const textoEnvio = ocupado ? "Un momento..." : confirmaConGoogle
    ? "Confirmar con Google" : accion === "vincular" ? "Continuar" : nombres[accion];

  return (
    <section className="metodos-acceso" aria-labelledby="titulo-metodos-acceso">
      <h2 id="titulo-metodos-acceso">Métodos de acceso</h2>
      {errorConsulta && (
        <>
          <p className="metodos-acceso__error" role="alert">{errorConsulta}</p>
          <button type="button" onClick={() => ejecutar(cargarAcceso)} disabled={ocupado}>Reintentar</button>
        </>
      )}
      {!accesoListo && !errorConsulta && <p role="status">Cargando métodos de acceso...</p>}
      {accesoListo && (
        <>
          {google && <p>Google vinculado. Desvinculalo para cambiar el correo o la contraseña desde Perfil.</p>}
          {mensaje && <p className="metodos-acceso__ok" role="status">{mensaje}</p>}
          {error && <p className="metodos-acceso__error" role="alert">{error}</p>}
          {!accion && (
            <div className="metodos-acceso__acciones">
              {google && !tienePassword && <button type="button" onClick={() => abrir("configurar")}>{nombres.configurar}</button>}
              {tienePassword && (
                <div className="metodos-acceso__acciones metodos-acceso__google-fila">
                  {(google || googlePendiente) && (
                    <BotonGoogle destacado={google} onClick={() => abrir("desvincular")}>
                      {googlePendiente ? "Quitar vínculo pendiente" : nombres.desvincular}
                    </BotonGoogle>
                  )}
                  {!google && <BotonGoogle onClick={() => abrir("vincular")}>{nombres.vincular}</BotonGoogle>}
                </div>
              )}
              {puedeCambiarCorreo && <button type="button" onClick={() => abrir("correo")}>{nombres.correo}</button>}
              {puedeCambiarPassword && <button type="button" onClick={() => abrir("password")}>{nombres.password}</button>}
            </div>
          )}
          {accion === "correo" && puedeCambiarCorreo && (
            <>
              <CambiarCorreoFirebase perfil={perfil} pedir={pedir} onActualizado={onActualizado} />
              <button type="button" onClick={() => abrir("")}>Volver a métodos de acceso</button>
            </>
          )}
          {accion && accion !== "correo" && (
            <form onSubmit={enviar} className="metodos-acceso__detalle">
              <h3>{nombres[accion]}</h3>
              <fieldset disabled={ocupado}>
                {muestraPassword && (
                  <label>
                    Contraseña actual
                    <input type="password" value={password} autoComplete="current-password" required
                      onChange={(event) => setPassword(event.target.value)} />
                  </label>
                )}
                {muestraNueva && (
                  <>
                    <label>
                      Nueva contraseña
                      <input type="password" value={nueva} autoComplete="new-password" required minLength={8}
                        onChange={(event) => setNueva(event.target.value)} />
                    </label>
                    <label>
                      Confirmar contraseña
                      <input type="password" value={confirmacion} autoComplete="new-password" required
                        onChange={(event) => setConfirmacion(event.target.value)} />
                    </label>
                  </>
                )}
              </fieldset>
              {accion === "vincular" && vinculo && <p>Elegí en Google la cuenta que usa el correo {perfil.email}.</p>}
              <div className="metodos-acceso__acciones">
                {confirmaConGoogle ? (
                  <BotonGoogle type="submit" destacado disabled={ocupado}>{textoEnvio}</BotonGoogle>
                ) : (
                  <button type="submit" className="metodos-acceso__principal" disabled={ocupado}>{textoEnvio}</button>
                )}
                <button type="button" onClick={() => abrir("")} disabled={ocupado}>Cancelar</button>
              </div>
            </form>
          )}
        </>
      )}
    </section>
  );
}
