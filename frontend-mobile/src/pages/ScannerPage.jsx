import { useEffect, useRef, useState } from "react";
import { FaCamera, FaCheckCircle, FaKeyboard, FaQrcode, FaStop } from "react-icons/fa";
import { apiFetch } from "../utils/api";

function extraerIdViaje(valor) {
  const texto = String(valor || "").trim();
  const formato = texto.match(/^TRUKLY:VIAJE:(\d+)$/i);
  if (formato) return Number(formato[1]);
  try {
    const id = new URL(texto).searchParams.get("viaje");
    if (id && /^\d+$/.test(id)) return Number(id);
  } catch { /* También se acepta el ID solo. */ }
  return /^\d+$/.test(texto) ? Number(texto) : null;
}

export default function ScannerPage() {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const frameRef = useRef(null);
  const detectorRef = useRef(null);
  const viajesRef = useRef([]);
  const [viajes, setViajes] = useState([]);
  const [codigo, setCodigo] = useState("");
  const [escaneando, setEscaneando] = useState(false);
  const [seleccionado, setSeleccionado] = useState(null);
  const [observacion, setObservacion] = useState("");
  const [procesando, setProcesando] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [empresaValidada, setEmpresaValidada] = useState(false);

  const disponibles = viajes.filter((viaje) => ["pendiente", "en curso"].includes(viaje.estado?.toLowerCase()));

  const detenerCamara = () => {
    if (frameRef.current) cancelAnimationFrame(frameRef.current);
    streamRef.current?.getTracks().forEach((track) => track.stop());
    frameRef.current = null;
    streamRef.current = null;
    if (videoRef.current) videoRef.current.srcObject = null;
    setEscaneando(false);
  };

  const cargarViajes = async () => {
    const result = await apiFetch("/api/choferes/mis-viajes", { signal: AbortSignal.timeout(20000) });
    if (result?.response.ok) {
      const siguientesViajes = Array.isArray(result.data) ? result.data : [];
      viajesRef.current = siguientesViajes.filter((viaje) => ["pendiente", "en curso"].includes(viaje.estado?.toLowerCase()));
      setViajes(siguientesViajes);
    }
  };

  useEffect(() => {
    const id = requestAnimationFrame(() => cargarViajes().catch(() => {
      setFeedback({ type: "error", text: "No se pudieron cargar los viajes. Revisá tu conexión y volvé a abrir esta sección." });
    }));
    return () => {
      cancelAnimationFrame(id);
      if (frameRef.current) cancelAnimationFrame(frameRef.current);
      streamRef.current?.getTracks().forEach((track) => track.stop());
    };
  }, []);

  const validarCodigo = (valor) => {
    if (String(valor || "").trim() === "TRUKLY:EMPRESA:PRINCIPAL") {
      detenerCamara();
      setEmpresaValidada(true);
      const activos = viajesRef.current.filter((viaje) => viaje.estado?.toLowerCase() === "en curso");
      const candidatos = activos.length ? activos : viajesRef.current;
      if (candidatos.length === 1) setSeleccionado(candidatos[0]);
      setFeedback({ type: candidatos.length ? "ok" : "error", text: candidatos.length ? "Empresa reconocida. Confirmá el viaje a registrar." : "No tenés viajes habilitados para registrar." });
      return true;
    }
    const id = extraerIdViaje(valor);
    const viaje = viajesRef.current.find((item) => item.id_viaje === id);
    if (!id || !viaje) {
      setFeedback({ type: "error", text: "El código no corresponde a un viaje habilitado." });
      return false;
    }
    detenerCamara();
    setFeedback(null);
    setSeleccionado(viaje);
    return true;
  };

  const abrirCamara = async () => {
    setFeedback(null);
    if (!("BarcodeDetector" in window)) {
      setFeedback({ type: "error", text: "Este navegador no admite lectura QR. Usá el ingreso manual." });
      return;
    }
    try {
      detectorRef.current = new window.BarcodeDetector({ formats: ["qr_code"] });
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: { ideal: "environment" } }, audio: false });
      streamRef.current = stream;
      setEscaneando(true);
      requestAnimationFrame(() => {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
        const detectar = async () => {
          if (videoRef.current?.readyState >= 2) {
            try {
              const encontrados = await detectorRef.current.detect(videoRef.current);
              if (encontrados[0]?.rawValue && validarCodigo(encontrados[0].rawValue)) return;
            } catch { /* Se reintenta en el próximo cuadro. */ }
          }
          frameRef.current = requestAnimationFrame(detectar);
        };
        frameRef.current = requestAnimationFrame(detectar);
      });
    } catch (err) {
      detenerCamara();
      setFeedback({ type: "error", text: err.name === "NotAllowedError" ? "Necesitamos permiso para usar la cámara." : "No se pudo abrir la cámara." });
    }
  };

  const confirmar = async () => {
    if (procesando || !seleccionado) return;
    const tipo = seleccionado.estado?.toLowerCase() === "pendiente" ? "ingreso" : "salida";
    setProcesando(true);
    setFeedback(null);
    try {
      const result = await apiFetch(`/api/choferes/viajes/${seleccionado.id_viaje}/registro`, {
      method: "POST",
      signal: AbortSignal.timeout(20000),
      body: JSON.stringify({ tipo_registro: tipo, observacion: observacion.trim() }),
    });
    if (result?.response.ok) {
      setFeedback({ type: "ok", text: tipo === "ingreso" ? "Salida de la empresa registrada. Viaje en curso." : "Regreso a la empresa registrado. Viaje finalizado." });
      setEmpresaValidada(false);
      setSeleccionado(null);
      setCodigo("");
      setObservacion("");
      try {
        await cargarViajes();
      } catch {
        setFeedback({ type: "ok", text: "Movimiento guardado. No se pudieron actualizar los viajes; volvé a abrir la sección Viajes." });
      }
    } else setFeedback({ type: "error", text: result?.data.mensaje || "No se pudo guardar el registro." });
    } catch (err) {
      setFeedback({ type: "error", text: err.name === "TimeoutError" || err.name === "AbortError"
        ? "El servidor no respondió a tiempo. Revisá el estado en Viajes antes de volver a confirmar."
        : "No se pudo confirmar el movimiento por un problema de conexión. Revisá el estado en Viajes antes de reintentar." });
    } finally {
      setProcesando(false);
    }
  };

  const tipo = seleccionado?.estado?.toLowerCase() === "pendiente" ? "Salida de la empresa" : "Regreso a la empresa";
  return (
    <section className="page-stack">
      <header className="page-heading"><span>CONTROL DE VIAJE</span><h1>Escanear QR</h1><p>Registrá el inicio o final de un viaje.</p></header>
      {feedback && <p className={`feedback ${feedback.type}`}>{feedback.type === "ok" && <FaCheckCircle />} {feedback.text}</p>}
      <article className="scanner-card">
        <div className={`camera ${escaneando ? "active" : ""}`}><video ref={videoRef} muted playsInline />{!escaneando && <div><FaQrcode /><strong>Cámara apagada</strong><span>Activala frente al código QR.</span></div>}<i /></div>
        <button className="button primary wide" onClick={escaneando ? detenerCamara : abrirCamara}>{escaneando ? <><FaStop /> Detener cámara</> : <><FaCamera /> Abrir cámara</>}</button>
        <div className="manual-code"><label htmlFor="codigo"><FaKeyboard /> Ingreso manual</label><div><input id="codigo" inputMode="numeric" value={codigo} onChange={(event) => setCodigo(event.target.value)} placeholder="ID del viaje" /><button onClick={() => validarCodigo(codigo)}>Validar</button></div></div>
      </article>
      {empresaValidada && <article className="available-card"><div className="section-title"><div><FaQrcode /><span>EMPRESA PRINCIPAL</span></div><b>{disponibles.length}</b></div>{disponibles.length === 0 ? <p className="empty compact">No tenés viajes para registrar.</p> : disponibles.filter((viaje) => !disponibles.some((item) => item.estado?.toLowerCase() === "en curso") || viaje.estado?.toLowerCase() === "en curso").map((viaje) => <button key={viaje.id_viaje} onClick={() => setSeleccionado(viaje)}><span>Viaje #{viaje.id_viaje}</span><strong>{viaje.origen} → {viaje.destino}</strong><small>{viaje.estado?.toLowerCase() === "pendiente" ? "Registrar salida" : "Registrar regreso"}</small></button>)}</article>}
      {seleccionado && <div className="modal-backdrop" onMouseDown={() => !procesando && setSeleccionado(null)}><div className="modal-sheet" role="dialog" aria-modal="true" onMouseDown={(event) => event.stopPropagation()}><span>{tipo}</span><h2>Confirmar {tipo.toLowerCase()}</h2><p>Viaje #{seleccionado.id_viaje}<br /><strong>{seleccionado.origen} → {seleccionado.destino}</strong></p>{feedback?.type === "error" && <p role="alert" className="feedback error">{feedback.text}</p>}<label>Observación opcional<textarea maxLength="100" value={observacion} onChange={(event) => setObservacion(event.target.value)} /></label><div><button className="button secondary" disabled={procesando} onClick={() => setSeleccionado(null)}>Cancelar</button><button className="button primary" onClick={confirmar} disabled={procesando}>{procesando ? "Guardando..." : "Confirmar"}</button></div></div></div>}
    </section>
  );
}
