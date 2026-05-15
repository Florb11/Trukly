import {
  FaClipboardCheck,
  FaRoute,
  FaTruckMoving,
  FaWrench,
} from "react-icons/fa";
import "./FeatureSection.css";
import viajesImg from "../assets/viajes-trukly.png";
import fallasImg from "../assets/fallas-trukly.png";

const highlights = [
  {
    icon: <FaRoute />,
    title: "Planificación clara",
    text: "Asigná recorridos, choferes y camiones con información visible para cada rol.",
  },
  {
    icon: <FaTruckMoving />,
    title: "Flota ordenada",
    text: "Consultá unidades disponibles y mantené el estado operativo siempre a mano.",
  },
  {
    icon: <FaClipboardCheck />,
    title: "Registro consistente",
    text: "Reducí planillas sueltas y centralizá salidas, llegadas y novedades.",
  },
  {
    icon: <FaWrench />,
    title: "Fallas trazables",
    text: "Seguimiento desde el reporte del chofer hasta el diagnóstico mecánico.",
  },
];

function FeatureSection() {
  return (
    <section id="funcionalidades" className="feature-section">
      <div className="feature-intro">
        <span>Funcionalidades</span>
        <h2>Todo lo importante de la operación, ordenado por flujo de trabajo.</h2>
        <p>
          Trukly conecta la planificación logística con el estado real de la
          flota, para que cada equipo vea lo que necesita sin duplicar tareas.
        </p>
      </div>

      <div className="feature-grid">
        {highlights.map((item) => (
          <article className="feature-card" key={item.title}>
            <div className="feature-card-icon">{item.icon}</div>
            <h3>{item.title}</h3>
            <p>{item.text}</p>
          </article>
        ))}
      </div>

      <div className="feature-block">
        <div className="feature-text">
          <span>Viajes</span>
          <h2>Gestioná viajes asignados con una vista más clara.</h2>
          <p>
            Los operadores organizan recorridos, asignan choferes y camiones,
            mientras que los choferes consultan sus trayectos y registran
            salidas o llegadas desde el sistema.
          </p>
        </div>

        <div className="feature-image">
          <img src={viajesImg} alt="Gestión de viajes en Trukly" />
        </div>
      </div>

      <div className="feature-block reverse">
        <div className="feature-text">
          <span>Reportes de falla</span>
          <h2>Registrá fallas y seguí su estado hasta la reparación.</h2>
          <p>
            Los choferes reportan problemas del camión y los mecánicos pueden
            consultar, diagnosticar y cerrar reparaciones desde una misma
            plataforma.
          </p>
        </div>

        <div className="feature-image">
          <img src={fallasImg} alt="Reportes de falla en Trukly" />
        </div>
      </div>
    </section>
  );
}

export default FeatureSection;