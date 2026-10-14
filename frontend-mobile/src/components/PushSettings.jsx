import { useState } from "react";
import { FaBell, FaBellSlash } from "react-icons/fa";
import { activarPush, desactivarPush } from "../utils/push";

export default function PushSettings() {
  const [activo, setActivo] = useState(() => Boolean(localStorage.getItem("trukly_push_token")));
  const [ocupado, setOcupado] = useState(false);
  const [error, setError] = useState("");
  const cambiar = async () => {
    setOcupado(true); setError("");
    try {
      if (activo) await desactivarPush(); else await activarPush();
      setActivo(!activo);
    } catch (err) { setError(err.message || "No se pudo cambiar la configuración."); }
    finally { setOcupado(false); }
  };
  return <div><button className="button secondary wide" disabled={ocupado} onClick={cambiar}>
    {activo ? <FaBellSlash /> : <FaBell />}{ocupado ? "Configurando..." : activo ? "Desactivar avisos push" : "Activar notificaciones"}
  </button>{error && <p className="feedback error" role="alert">{error}</p>}</div>;
}
