import { useEffect, useRef, useState } from "react";
import "./ConfirmarAccionModal.css";

export default function ConfirmarAccionModal({ titulo, descripcion, identidad, detalle, textoConfirmar, icono, peligro = true, onConfirm, onClose }) {
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState("");
  const ocupado = useRef(false);
  const cancelar = useRef(null);
  const dialogo = useRef(null);
  useEffect(() => {
    const anterior = document.activeElement;
    const overflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    cancelar.current?.focus();
    const teclado = (event) => {
      if (event.key === "Escape" && !ocupado.current) onClose();
      if (event.key === "Tab") {
        const botones = [...(dialogo.current?.querySelectorAll('button:not([disabled])') || [])];
        if (!botones.length) { event.preventDefault(); return; }
        const primero = botones[0], ultimo = botones.at(-1);
        if (event.shiftKey && document.activeElement === primero) { event.preventDefault(); ultimo?.focus(); }
        else if (!event.shiftKey && document.activeElement === ultimo) { event.preventDefault(); primero?.focus(); }
      }
    };
    document.addEventListener("keydown", teclado);
    return () => { document.removeEventListener("keydown", teclado); document.body.style.overflow = overflow; anterior?.focus(); };
  }, [onClose]);
  const confirmar = async () => {
    if (ocupado.current) return;
    ocupado.current = true; setGuardando(true); setError("");
    try { await onConfirm(); onClose(); }
    catch (err) { setError(["AbortError", "TimeoutError", "TypeError"].includes(err.name) ? "No se pudo confirmar la operación. Cerrá este aviso y recargá la página para comprobar el estado antes de reintentar." : err.message || "No se pudo completar la operación."); }
    finally { ocupado.current = false; setGuardando(false); }
  };
  return <div className="confirmar-accion-backdrop"><section className={`confirmar-accion ${peligro ? "confirmar-accion--desactivar" : "confirmar-accion--activar"}`} ref={dialogo} role="alertdialog" aria-modal="true" aria-labelledby="confirmar-accion-titulo" aria-describedby="confirmar-accion-mensaje" aria-busy={guardando}>
    <div className="confirmar-accion__icono">{icono}</div>
    <h2 id="confirmar-accion-titulo">{titulo}</h2>
    <p id="confirmar-accion-mensaje">{descripcion}</p>
    <div className="confirmar-accion__identidad">{identidad}</div>
    <p className="confirmar-accion__efecto">{detalle}</p>
    {error && <p className="confirmar-accion__error" role="alert">{error}</p>}
    <footer><button type="button" ref={cancelar} disabled={guardando} onClick={onClose}>Cancelar</button><button type="button" className="confirmar-accion__confirmar" disabled={guardando} onClick={confirmar}>{guardando ? "Guardando..." : textoConfirmar}</button></footer>
  </section></div>;
}
