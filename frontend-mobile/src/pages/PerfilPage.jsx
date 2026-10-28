import { useEffect, useState } from "react";
import { FaCamera, FaSave, FaSignOutAlt, FaUser } from "react-icons/fa";
import { useAuth } from "../context/AuthContext";
import { API_URL, apiFetch } from "../utils/api";

export default function PerfilPage() {
  const { usuario, logout, actualizarUsuario } = useAuth();
  const [perfil, setPerfil] = useState(null);
  const [form, setForm] = useState({});
  const [cargando, setCargando] = useState(true);
  const [ocupado, setOcupado] = useState(false);
  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [fotoFallida, setFotoFallida] = useState(false);
  useEffect(() => {
    const controller = new AbortController();
    const id = setTimeout(async () => {
      try {
        const resultado = await apiFetch("/api/perfil", { signal: AbortSignal.any([controller.signal, AbortSignal.timeout(20000)]) });
        if (!resultado) return;
        if (!resultado.response.ok) throw new Error(resultado.data.mensaje || "No se pudo cargar el perfil.");
        const datos = resultado.data.perfil;
        setPerfil(datos);
        setForm(Object.fromEntries(["nombre", "apellido", "email", "licencia", "vencimientoLicencia", "legajo"].map((campo) => [campo, datos[campo] || ""])));
      } catch (err) { if (!controller.signal.aborted) setError(["TypeError", "TimeoutError"].includes(err.name) ? "No se pudo cargar el perfil. Revisá tu conexión y volvé a abrir esta sección." : err.message); }
      finally { if (!controller.signal.aborted) setCargando(false); }
    }, 0);
    return () => { clearTimeout(id); controller.abort(); };
  }, []);
  const guardar = async (event) => {
    event.preventDefault();
    if (ocupado) return;
    setOcupado(true); setError(""); setMensaje("");
    try {
      const datos = { nombre: form.nombre, apellido: form.apellido, email: form.email };
      if (perfil.rol === "chofer") Object.assign(datos, { licencia: form.licencia, vencimientoLicencia: form.vencimientoLicencia, legajo: form.legajo });
      const resultado = await apiFetch("/api/perfil", { method: "PUT", body: JSON.stringify(datos), signal: AbortSignal.timeout(20000) });
      if (!resultado) return;
      if (!resultado.response.ok) throw new Error(resultado.data.mensaje || "No se pudo guardar el perfil.");
      setPerfil(resultado.data.perfil); actualizarUsuario(resultado.data.perfil);
      setMensaje("Perfil actualizado.");
    } catch (err) { setError(["TypeError", "TimeoutError"].includes(err.name) ? "No se pudo confirmar el cambio. Revisá tu conexión y recargá el perfil." : err.message); }
    finally { setOcupado(false); }
  };
  const subirFoto = async (event) => {
    const archivo = event.target.files?.[0];
    event.target.value = "";
    if (!archivo || ocupado) return;
    setError(""); setMensaje("");
    if (!/\.(jpe?g|png|webp)$/i.test(archivo.name) || archivo.size > 3 * 1024 * 1024) {
      setError("Elegí una imagen JPG, PNG o WEBP de hasta 3 MB."); return;
    }
    setOcupado(true);
    try {
      const datos = new FormData(); datos.append("foto", archivo);
      const resultado = await apiFetch("/api/perfil/foto", { method: "POST", body: datos, signal: AbortSignal.timeout(30000) });
      if (!resultado) return;
      if (!resultado.response.ok) throw new Error(resultado.data.mensaje || "No se pudo guardar la foto.");
      const cambio = { foto_perfil: resultado.data.foto_perfil };
      setPerfil((actual) => ({ ...actual, ...cambio })); actualizarUsuario(cambio); setFotoFallida(false);
      setMensaje("Foto actualizada.");
    } catch (err) { setError(["TypeError", "TimeoutError"].includes(err.name) ? "No se pudo confirmar la foto. Revisá tu conexión y recargá el perfil." : err.message); }
    finally { setOcupado(false); }
  };
  const datos = perfil || usuario;
  const foto = datos?.foto_perfil ? new URL(datos.foto_perfil, API_URL).href : null;
  return <section className="page-stack">
    <header className="page-heading"><span>MI CUENTA</span><h1>Perfil</h1></header>
    {error && <p className="feedback error" role="alert">{error}</p>}{mensaje && <p className="feedback ok" role="status">{mensaje}</p>}
    {cargando ? <p className="empty">Cargando perfil...</p> : <>
      <div className="profile-card"><div className="profile-avatar">{foto && !fotoFallida ? <img src={foto} alt="Foto de perfil" onError={() => setFotoFallida(true)} /> : <FaUser />}</div>
        <h2>{datos?.nombre} {datos?.apellido}</h2><span>{datos?.rol === "chofer" ? "Chofer" : datos?.rol === "mecanico" ? "Mecánico" : "Operador logístico"}</span>
        <label className="button secondary photo-upload"><FaCamera /> {ocupado ? "Procesando..." : "Cambiar foto"}<input type="file" accept="image/jpeg,image/png,image/webp" disabled={ocupado || !perfil} onChange={subirFoto} /></label>
      </div>
      {perfil?.rol === "chofer" && <article className="profile-card">
        <h2>Horas en viaje · {perfil.horas_viaje?.mes || "Este mes"}</h2>
        <strong>{perfil.horas_viaje?.duracion || "Información no disponible"}</strong>
        <p>{perfil.horas_viaje?.viajes_confirmados ?? "—"} viajes confirmados · {perfil.horas_viaje?.viajes_en_curso ?? "—"} en curso</p>
        <p>Tiempo entre salida y regreso, incluidas paradas y descansos. Solo suman viajes con ambos controles válidos.</p>
      </article>}
      {perfil && <form className="profile-form" onSubmit={guardar}><fieldset disabled={ocupado}>
        <legend>Datos personales</legend>
        {[["nombre", "Nombre", "text"], ["apellido", "Apellido", "text"], ["email", "Email", "email"]].map(([campo, texto, tipo]) => <label key={campo}>{texto}<input type={tipo} required value={form[campo]} onChange={(event) => setForm({ ...form, [campo]: event.target.value })} /></label>)}
        <label>Usuario<input readOnly value={perfil.username || ""} /></label>
        {perfil.rol === "chofer" ? [["licencia", "Licencia", "text"], ["vencimientoLicencia", "Vencimiento de licencia", "date"], ["legajo", "Legajo", "text"]].map(([campo, texto, tipo]) => <label key={campo}>{texto}<input type={tipo} required value={form[campo]} onChange={(event) => setForm({ ...form, [campo]: event.target.value })} /></label>) : <>
          <label>Legajo<input readOnly value={perfil.legajo || ""} /></label>
          <label>{perfil.rol === "mecanico" ? "Especialidad" : "Sector"}<input readOnly value={perfil.especialidad || perfil.sector || ""} /></label>
        </>}
        <button className="button primary wide"><FaSave />{ocupado ? "Guardando..." : "Guardar cambios"}</button>
      </fieldset></form>}
    </>}
    <button className="logout-button" onClick={async () => {
      setOcupado(true);
      try { await logout(); } catch { setError("No se pudieron desactivar los avisos de este dispositivo. Revisá tu conexión antes de cerrar sesión."); }
      finally { setOcupado(false); }
    }} disabled={ocupado}><FaSignOutAlt /> Cerrar sesión</button>
  </section>;
}
