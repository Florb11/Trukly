import "./ContactSection.css";

function ContactSection() {
  return (
    <section id="contacto" className="contact-section">
      <div className="contact-info">
        <span>Contacto</span>
        <h2>¿Querés conocer más sobre Trukly?</h2>
        <p>
          Dejanos tus datos y nos comunicamos para contarte cómo la plataforma
          puede ayudar a organizar la gestión logística de tu equipo.
        </p>

        <ul>
          <li>Centralización de viajes, choferes y camiones</li>
          <li>Seguimiento de reportes de falla</li>
          <li>Gestión de roles y usuarios</li>
        </ul>
      </div>

      <form className="contact-form">
        <div className="contact-row">
          <label>
            <span>Nombre</span>
            <input type="text" placeholder="Florencia" />
          </label>
          <label>
            <span>Apellido</span>
            <input type="text" placeholder="Bergman" />
          </label>
        </div>

        <label>
          <span>Correo electrónico</span>
          <input type="email" placeholder="nombre@empresa.com" />
        </label>
        <label>
          <span>Empresa</span>
          <input type="text" placeholder="Nombre de la empresa" />
        </label>
        <label>
          <span>Mensaje</span>
          <textarea placeholder="Contanos qué querés mejorar" rows="4"></textarea>
        </label>

        <button type="submit">Enviar consulta</button>
      </form>
    </section>
  );
}

export default ContactSection;