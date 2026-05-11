import "./HeroSection.css";
import heroVideo from "../assets/hero-trukly.mp4";

function HeroSection() {
  return (
    <section className="hero-section">
      <div className="hero-container">
        <div className="hero-content">
          <span className="hero-badge">Gestión logística</span>

          <h1>
            Controlá tus viajes, camiones y reportes desde un solo lugar.
          </h1>

          <p>
            Trukly ayuda a centralizar la operación logística, evitando registros
            manuales y mejorando el seguimiento de choferes, camiones y fallas.
          </p>

          <div className="hero-actions">
            <a href="/registro" className="hero-primary">
              Registrarse
            </a>
            <a href="#contacto" className="hero-secondary">
              Contacto
            </a>
          </div>
        </div>

        <div className="hero-media">
  <video
    src={heroVideo}
    autoPlay
    muted
    loop
    playsInline
    className="hero-video"
  />
</div>
      </div>
    </section>
  );
}

export default HeroSection;