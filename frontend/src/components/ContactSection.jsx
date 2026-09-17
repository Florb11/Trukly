import { useState } from "react";
import "./ContactSection.css";

function ContactSection() {
  const [formulario, setFormulario] = useState({
    nombre: "",
    apellido: "",
    email: "",
    empresa: "",
    mensaje: "",
  });
  const [enviando, setEnviando] = useState(false);
  const [respuesta, setRespuesta] = useState({ tipo: "", texto: "" });

  const handleChange = (e) => {
    setFormulario({
      ...formulario,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setRespuesta({ tipo: "", texto: "" });
    setEnviando(true);

    try {
      const resultado = await fetch("https://trukly-production.up.railway.app/api/contacto", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formulario),
      });

      const data = await resultado.json();

      if (!resultado.ok) {
        throw new Error(data.mensaje || "No se pudo enviar la consulta.");
      }

      setRespuesta({ tipo: "exito", texto: data.mensaje });
      setFormulario({
        nombre: "",
        apellido: "",
        email: "",
        empresa: "",
        mensaje: "",
      });
    } catch (error) {
      setRespuesta({
        tipo: "error",
        texto: error.message || "No se pudo conectar con el backend.",
      });
    } finally {
      setEnviando(false);
    }
  };

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

      <form className="contact-form" onSubmit={handleSubmit}>
        <div className="contact-row">
          <label>
            <span>Nombre</span>
            <input
              type="text"
              name="nombre"
              value={formulario.nombre}
              onChange={handleChange}
              placeholder="Florencia"
              maxLength={60}
              required
            />
          </label>
          <label>
            <span>Apellido</span>
            <input
              type="text"
              name="apellido"
              value={formulario.apellido}
              onChange={handleChange}
              placeholder="Bergman"
              maxLength={60}
              required
            />
          </label>
        </div>

        <label>
          <span>Correo electrónico</span>
          <input
            type="email"
            name="email"
            value={formulario.email}
            onChange={handleChange}
            placeholder="nombre@empresa.com"
            maxLength={120}
            required
          />
        </label>
        <label>
          <span>Empresa</span>
          <input
            type="text"
            name="empresa"
            value={formulario.empresa}
            onChange={handleChange}
            placeholder="Nombre de la empresa"
            maxLength={100}
          />
        </label>
        <label>
          <span>Mensaje</span>
          <textarea
            name="mensaje"
            value={formulario.mensaje}
            onChange={handleChange}
            placeholder="Contanos qué querés mejorar"
            rows="4"
            maxLength={800}
            required
          ></textarea>
        </label>

        <button type="submit" disabled={enviando}>
          {enviando ? "Enviando..." : "Enviar consulta"}
        </button>
        {respuesta.texto && (
          <p className={`contact-message ${respuesta.tipo}`}>
            {respuesta.texto}
          </p>
        )}
      </form>
    </section>
  );
}

export default ContactSection;
