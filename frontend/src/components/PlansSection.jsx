import { FaArrowRight, FaCrown } from "react-icons/fa";
import "./PlansSection.css";

const plans = [
  {
    name: "Básico",
    description: "Lo esencial para ordenar viajes, choferes y camiones en un solo lugar.",
    audience: "Para equipos que están empezando",
    className: "basic",
  },
  {
    name: "Pro",
    description: "Más seguimiento para quienes coordinan rutas y reportes todos los días.",
    audience: "Para operaciones en crecimiento",
    className: "pro",
  },
  {
    name: "Premium",
    description: "Una mirada más completa para trabajar con varios equipos y una flota mayor.",
    audience: "Para operaciones de mayor escala",
    className: "premium",
  },
];

function PlansSection() {
  return (
    <section id="planes" className="plans-section" aria-labelledby="plans-title">
      <div className="plans-section__inner">
        <div className="plans-section__intro">
          <span>Planes</span>
          <h2 id="plans-title">Una opción para cada etapa de tu operación.</h2>
          <p>Planes orientativos para mostrar cómo Trukly puede acompañar a distintos equipos.</p>
        </div>

        <div className="plans-section__grid">
          {plans.map((plan) => (
            <article className={`plans-card plans-card--${plan.className}`} key={plan.name}>
              <div className="plans-card__top">
                <span className="plans-card__audience">{plan.audience}</span>
                {plan.className === "premium" && <FaCrown className="plans-card__crown" aria-label="Premium" />}
              </div>
              <h3>{plan.name}</h3>
              <p>{plan.description}</p>
              <a href="#contacto" className="plans-card__link">
                Consultar plan <FaArrowRight aria-hidden="true" />
              </a>
            </article>
          ))}
        </div>

        <div className="plans-custom">
          <div>
            <span>¿Necesitás algo distinto?</span>
            <h3>Planes personalizados</h3>
            <p>Contanos cómo trabaja tu equipo y conversemos sobre una propuesta a medida.</p>
          </div>
          <a href="#contacto">
            Contactanos <FaArrowRight aria-hidden="true" />
          </a>
        </div>
      </div>
    </section>
  );
}

export default PlansSection;
