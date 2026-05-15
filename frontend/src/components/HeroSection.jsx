import "./HeroSection.css";
import heroVideo from "../assets/hero-trukly.mp4";

function HeroSection() {
  return (
    <section className="hero-section">
      <div className="hero-container">
        <div className="hero-content">
          <span className="hero-badge">Gestión logística para flotas</span>

          <h1>Operá tus viajes, camiones y reportes sin perder el control.</h1>

          <p>
            Trukly centraliza la operación diaria: asignaciones, estados de
            viaje, choferes, unidades y fallas mecánicas en una experiencia
            simple para equipos en movimiento.
          </p>

          <div className="hero-actions">
            <a href="/registro" className="hero-primary">
              Crear cuenta
            </a>
            <a href="#contacto" className="hero-secondary">
              Hablar con el equipo
            </a>
          </div>

          <div className="hero-stats" aria-label="Resumen de funcionalidades">
            <div>
              <strong>24/7</strong>
              <span>Seguimiento operativo</span>
            </div>
            <div>
              <strong>4 roles</strong>
              <span>Accesos organizados</span>
            </div>
            <div>
              <strong>1 panel</strong>
              <span>Viajes y fallas</span>
            </div>
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

          <div className="hero-media-card">
            <span>Estado de flota</span>
            <strong>Viajes activos</strong>
            <p>Choferes, camiones y reportes en una sola vista.</p>
          </div>
        </div>
      </div>
    </section>
  );
}

export default HeroSection;