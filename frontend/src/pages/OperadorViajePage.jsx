import { useState } from "react";
import {
  FaMapMarkerAlt,
  FaTruck,
  FaUser,
  FaCalendarAlt,
  FaBoxOpen,
  FaCheckCircle,
} from "react-icons/fa";
import "./OperadorViajePage.css";
import { fetchConToken } from "../utils/fetchConToken";

const estadosIniciales = {
  origen: "",
  destino: "",
  id_chofer: "",
  id_camion: "",
  fecha_salida: "",
  fecha_estimada_llegada: "",
  carga: "",
  peso_kg: "",
  observaciones: "",
};

function OperadorViajePage({ title = "Crear nuevo viaje" }) {
  const [form, setForm] = useState(estadosIniciales);
  const [enviando, setEnviando] = useState(false);
  const [exito, setExito] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setExito(false);

    if (
      !form.origen ||
      !form.destino ||
      !form.id_chofer ||
      !form.id_camion ||
      !form.fecha_salida
    ) {
      setError("Completá todos los campos obligatorios.");
      return;
    }

    try {
      setEnviando(true);

      const resultado = await fetchConToken(
        "http://localhost:5000/api/operador/viajes",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(form),
        },
      );

      if (!resultado) return;

      const { respuesta, data } = resultado;

      if (!respuesta.ok) {
        throw new Error(data.mensaje || data.msg || "Error al crear el viaje");
      }

      setExito(true);
      setForm(estadosIniciales);
    } catch (err) {
      setError(err.message);
    } finally {
      setEnviando(false);
    }
  };

  return (
    <section className="crear-viaje-page">
      <div className="crear-viaje-page__header">
        <div>
          <span>Operador logístico</span>
          <h1>{title}</h1>
          <p>Completá los datos para registrar un nuevo viaje en el sistema.</p>
        </div>
      </div>

      <div className="crear-viaje__layout">
        <form className="crear-viaje__form" onSubmit={handleSubmit} noValidate>
          <fieldset className="crear-viaje__fieldset">
            <legend>
              <FaMapMarkerAlt /> Ruta
            </legend>

            <div className="crear-viaje__row">
              <div className="crear-viaje__field">
                <label htmlFor="origen">Origen *</label>
                <input
                  id="origen"
                  name="origen"
                  type="text"
                  placeholder="Ciudad de origen"
                  value={form.origen}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="crear-viaje__field">
                <label htmlFor="destino">Destino *</label>
                <input
                  id="destino"
                  name="destino"
                  type="text"
                  placeholder="Ciudad de destino"
                  value={form.destino}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>
          </fieldset>

          <fieldset className="crear-viaje__fieldset">
            <legend>
              <FaUser /> Asignación
            </legend>

            <div className="crear-viaje__row">
              <div className="crear-viaje__field">
                <label htmlFor="id_chofer">ID Chofer *</label>
                <input
                  id="id_chofer"
                  name="id_chofer"
                  type="text"
                  placeholder="ej: 42"
                  value={form.id_chofer}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="crear-viaje__field">
                <label htmlFor="id_camion">
                  <FaTruck style={{ marginRight: 6 }} />
                  ID Camión *
                </label>
                <input
                  id="id_camion"
                  name="id_camion"
                  type="text"
                  placeholder="ej: 7"
                  value={form.id_camion}
                  onChange={handleChange}
                  required
                />
              </div>
            </div>
          </fieldset>

          <fieldset className="crear-viaje__fieldset">
            <legend>
              <FaCalendarAlt /> Fechas
            </legend>

            <div className="crear-viaje__row">
              <div className="crear-viaje__field">
                <label htmlFor="fecha_salida">Fecha de salida *</label>
                <input
                  id="fecha_salida"
                  name="fecha_salida"
                  type="datetime-local"
                  value={form.fecha_salida}
                  onChange={handleChange}
                  required
                />
              </div>

              <div className="crear-viaje__field">
                <label htmlFor="fecha_estimada_llegada">Llegada estimada</label>
                <input
                  id="fecha_estimada_llegada"
                  name="fecha_estimada_llegada"
                  type="datetime-local"
                  value={form.fecha_estimada_llegada}
                  onChange={handleChange}
                />
              </div>
            </div>
          </fieldset>

          <fieldset className="crear-viaje__fieldset">
            <legend>
              <FaBoxOpen /> Carga
            </legend>

            <div className="crear-viaje__row">
              <div className="crear-viaje__field">
                <label htmlFor="carga">Descripción de carga</label>
                <input
                  id="carga"
                  name="carga"
                  type="text"
                  placeholder="ej: Electrodomésticos"
                  value={form.carga}
                  onChange={handleChange}
                />
              </div>

              <div className="crear-viaje__field crear-viaje__field--sm">
                <label htmlFor="peso_kg">Peso (kg)</label>
                <input
                  id="peso_kg"
                  name="peso_kg"
                  type="number"
                  min="0"
                  placeholder="ej: 8500"
                  value={form.peso_kg}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="crear-viaje__field">
              <label htmlFor="observaciones">Observaciones</label>
              <textarea
                id="observaciones"
                name="observaciones"
                rows={3}
                placeholder="Instrucciones especiales, temperatura requerida, etc."
                value={form.observaciones}
                onChange={handleChange}
              />
            </div>
          </fieldset>

          {error && (
            <p className="admin-message admin-message--error">{error}</p>
          )}

          {exito && (
            <p className="crear-viaje__exito">
              <FaCheckCircle /> Viaje creado correctamente.
            </p>
          )}

          <div className="crear-viaje__actions">
            <button
              type="button"
              className="crear-viaje__btn crear-viaje__btn--secondary"
              onClick={() => {
                setForm(estadosIniciales);
                setError("");
                setExito(false);
              }}
            >
              Limpiar
            </button>

            <button
              type="submit"
              className="crear-viaje__btn crear-viaje__btn--primary"
              disabled={enviando}
            >
              {enviando ? "Creando viaje..." : "Crear viaje"}
            </button>
          </div>
        </form>

        <aside className="crear-viaje__sidebar">
          <div className="crear-viaje__info-card">
            <h3>Checklist previo</h3>
            <ul>
              <li>
                <span className="crear-viaje__bullet crear-viaje__bullet--ok" />
                Chofer habilitado y con licencia vigente
              </li>
              <li>
                <span className="crear-viaje__bullet crear-viaje__bullet--ok" />
                Camión con VTV al día
              </li>
              <li>
                <span className="crear-viaje__bullet crear-viaje__bullet--warn" />
                Carga correctamente declarada
              </li>
              <li>
                <span className="crear-viaje__bullet crear-viaje__bullet--ok" />
                Ruta sin alertas activas
              </li>
            </ul>
          </div>

          <div className="crear-viaje__info-card">
            <h3>Estados del viaje</h3>
            <div className="crear-viaje__estados">
              {[
                { key: "pendiente", label: "Pendiente" },
                { key: "aceptado", label: "Aceptado" },
                { key: "en-curso", label: "En curso" },
                { key: "finalizado", label: "Finalizado" },
                { key: "cancelado", label: "Cancelado" },
              ].map((e) => (
                <span
                  key={e.key}
                  className={`chofer-badge chofer-badge--${e.key}`}
                >
                  {e.label}
                </span>
              ))}
            </div>
          </div>
        </aside>
      </div>
    </section>
  );
}

export default OperadorViajePage;
