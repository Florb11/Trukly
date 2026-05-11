import "./FeatureSection.css";
import viajesImg from "../assets/viajes-trukly.png";
import fallasImg from "../assets/fallas-trukly.png";

function FeatureSection() {
  return (
    <section id="funcionalidades" className="feature-section">
      <div className="feature-block">
        <div className="feature-text">
          <span>Viajes</span>
          <h2>Gestioná los viajes asignados de forma más clara.</h2>
          <p>
            Los operadores pueden organizar viajes, asignar choferes y camiones,
            mientras que los choferes pueden consultar sus recorridos y registrar
            salidas o llegadas.
          </p>
        </div>

        <div className="feature-image">
          <img src={viajesImg} alt="Gestión de viajes en Trukly" />
        </div>
      </div>

      <div className="feature-block reverse">
        <div className="feature-text">
          <span>Reportes de falla</span>
          <h2>Registrá fallas y seguí su estado en el sistema.</h2>
          <p>
            Los choferes pueden reportar problemas del camión y los mecánicos
            pueden consultar, diagnosticar y cerrar reparaciones desde una misma
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