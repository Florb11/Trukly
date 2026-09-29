import { FaIdCard, FaSignOutAlt, FaUser } from "react-icons/fa";
import { useAuth } from "../context/AuthContext";

export default function PerfilPage() {
  const { usuario, logout } = useAuth();
  return (
    <section className="page-stack">
      <header className="page-heading"><span>MI CUENTA</span><h1>Perfil</h1><p>Datos de tu sesión mobile.</p></header>
      <article className="profile-card"><div className="profile-avatar"><FaUser /></div><h2>{usuario?.nombre} {usuario?.apellido}</h2><span>Chofer</span><dl><div><dt><FaIdCard /> Usuario</dt><dd>{usuario?.username || "-"}</dd></div><div><dt>Email</dt><dd>{usuario?.email || "-"}</dd></div></dl></article>
      <button className="logout-button" onClick={logout}><FaSignOutAlt /> Cerrar sesión</button>
    </section>
  );
}
