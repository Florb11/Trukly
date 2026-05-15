import { FaHardHat, FaHeadset, FaShieldAlt, FaTruck } from "react-icons/fa";
import "./BannerSection.css";

const roles = [
  {
    icon: <FaTruck />,
    name: "Choferes",
    text: "Consultan viajes y reportan novedades desde el recorrido.",
  },
  {
    icon: <FaHardHat />,
    name: "Mecánicos",
    text: "Diagnostican fallas y actualizan reparaciones pendientes.",
  },
  {
    icon: <FaHeadset />,
    name: "Operadores",
    text: "Asignan viajes, camiones y choferes con más visibilidad.",
  },
  {
    icon: <FaShieldAlt />,
    name: "Administradores",
    text: "Supervisan usuarios, permisos y datos principales.",
  },
];

function BannerSection() {
  return (
    <section id="roles" className="banner-section">
      <div className="banner-copy">
        <span>Roles del sistema</span>
        <h2>Una plataforma pensada para cada parte de la operación.</h2>
        <p>
          Cada usuario entra con una vista enfocada en su trabajo, evitando ruido
          y manteniendo la información crítica en el lugar correcto.
        </p>
      </div>

      <div className="role-list">
        {roles.map((role) => (
          <article className="role-card" key={role.name}>
            <div className="role-icon">{role.icon}</div>
            <h3>{role.name}</h3>
            <p>{role.text}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

export default BannerSection;