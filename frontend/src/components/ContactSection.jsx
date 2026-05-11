import "./ContactSection.css";

function ContactSection() {
  return (
    <section id="contacto" className="contact-section">
      <div className="contact-info">
        <span>Contacto</span>
        <h2>¿Querés conocer más sobre Trukly?</h2>
        <p>
          Dejanos tus datos y nos comunicamos para contarte cómo la plataforma
          puede ayudar a organizar la gestión logística.
        </p>

        <ul>
          <li>Centralización de viajes y camiones</li>
          <li>Seguimiento de reportes de falla</li>
          <li>Gestión de roles y usuarios</li>
        </ul>
      </div>

      <form className="contact-form">
        <div className="contact-row">
          <input type="text" placeholder="Nombre" />
          <input type="text" placeholder="Apellido" />
        </div>

        <input type="email" placeholder="Correo electrónico" />
        <input type="text" placeholder="Empresa" />
        <textarea placeholder="Mensaje" rows="4"></textarea>

        <button type="submit">Enviar consulta</button>
      </form>
    </section>
  );
}

export default ContactSection;