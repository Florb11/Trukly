import {
  FaCheckCircle,
  FaClock,
  FaTimes,
  FaTools,
  FaTruck,
  FaWrench,
} from "react-icons/fa";
import "./MecanicoMantenimientoModal.css";

function MecanicoMantenimientoModal({
  abierto,
  onCerrar,
  detalle,
  cargando,
  error,
}) {
  if (!abierto) return null;

  const formatearFecha = (fecha) => {
    if (!fecha) return "-";

    const fechaConvertida = new Date(fecha);

    if (Number.isNaN(fechaConvertida.getTime())) {
      return fecha;
    }

    return fechaConvertida.toLocaleString("es-UY", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const cerrarDesdeFondo = (e) => {
    if (e.target === e.currentTarget) {
      onCerrar();
    }
  };

  const camion = detalle?.camion;
  const reportesPendientes = detalle?.reportes_pendientes || [];
  const reparacionesRealizadas = detalle?.reparaciones_realizadas || [];

  return (
    <div
      className="mecanico-mantenimiento-modal-overlay"
      onMouseDown={cerrarDesdeFondo}
    >
      <div className="mecanico-mantenimiento-modal">
        <div className="mecanico-mantenimiento-modal__header">
          <div>
            <span>Historial de la unidad</span>
            <h2>Mantenimiento del camión</h2>
          </div>

          <button
            type="button"
            className="mecanico-mantenimiento-modal__close"
            onClick={onCerrar}
            aria-label="Cerrar modal"
          >
            <FaTimes />
          </button>
        </div>

        {cargando ? (
          <p className="mecanico-mantenimiento-modal__message">
            Cargando información...
          </p>
        ) : error ? (
          <p className="mecanico-mantenimiento-modal__message mecanico-mantenimiento-modal__message--error">
            {error}
          </p>
        ) : (
          <>
            <section className="mecanico-mantenimiento-modal__truck">
              <div className="mecanico-mantenimiento-modal__truck-icon">
                <FaTruck />
              </div>

              <div>
                <span>Unidad #{camion?.id_camion}</span>
                <h3>{camion?.matricula || "Sin matrícula"}</h3>
                <p>
                  {camion?.marca || "-"} {camion?.modelo || ""}
                </p>
              </div>

              <strong className="mecanico-mantenimiento-modal__status">
                {camion?.estado || "Sin estado"}
              </strong>
            </section>

            <div className="mecanico-mantenimiento-modal__summary">
              <article>
                <FaClock />
                <div>
                  <strong>{reportesPendientes.length}</strong>
                  <span>Reportes pendientes</span>
                </div>
              </article>

              <article>
                <FaCheckCircle />
                <div>
                  <strong>{reparacionesRealizadas.length}</strong>
                  <span>Reparaciones realizadas</span>
                </div>
              </article>
            </div>

            <div className="mecanico-mantenimiento-modal__sections">
              <section className="mecanico-mantenimiento-modal__section">
                <div className="mecanico-mantenimiento-modal__section-title">
                  <div>
                    <FaTools />
                    <h3>Reparaciones pendientes</h3>
                  </div>

                  <span>{reportesPendientes.length}</span>
                </div>

                <div className="mecanico-mantenimiento-modal__list">
                  {reportesPendientes.length === 0 ? (
                    <p className="mecanico-mantenimiento-modal__empty">
                      Este camión no tiene reparaciones pendientes.
                    </p>
                  ) : (
                    reportesPendientes.map((reporte) => (
                      <article
                        className="mecanico-mantenimiento-modal__report"
                        key={reporte.id_reporte}
                      >
                        <div className="mecanico-mantenimiento-modal__report-top">
                          <strong>Reporte #{reporte.id_reporte}</strong>

                          <span className="mecanico-mantenimiento-modal__badge mecanico-mantenimiento-modal__badge--pending">
                            {reporte.estado}
                          </span>
                        </div>

                        <p>{reporte.descripcion}</p>

                        <div className="mecanico-mantenimiento-modal__date">
                          <FaClock />
                          <span>
                            Reportado: {formatearFecha(reporte.fecha_hora)}
                          </span>
                        </div>
                      </article>
                    ))
                  )}
                </div>
              </section>

              <section className="mecanico-mantenimiento-modal__section">
                <div className="mecanico-mantenimiento-modal__section-title">
                  <div>
                    <FaWrench />
                    <h3>Historial de reparaciones</h3>
                  </div>

                  <span>{reparacionesRealizadas.length}</span>
                </div>

                <div className="mecanico-mantenimiento-modal__list">
                  {reparacionesRealizadas.length === 0 ? (
                    <p className="mecanico-mantenimiento-modal__empty">
                      Todavía no hay reparaciones registradas.
                    </p>
                  ) : (
                    reparacionesRealizadas.map((reporte) => (
                      <article
                        className="mecanico-mantenimiento-modal__report mecanico-mantenimiento-modal__report--resolved"
                        key={reporte.id_reporte}
                      >
                        <div className="mecanico-mantenimiento-modal__report-top">
                          <strong>Reporte #{reporte.id_reporte}</strong>

                          <span className="mecanico-mantenimiento-modal__badge mecanico-mantenimiento-modal__badge--resolved">
                            Resuelto
                          </span>
                        </div>

                        <p>{reporte.descripcion}</p>

                        <div className="mecanico-mantenimiento-modal__repair">
                          <strong>Reparación realizada</strong>
                          <p>
                            {reporte.nota_reparacion ||
                              "Sin nota de reparación"}
                          </p>
                        </div>

                        <div className="mecanico-mantenimiento-modal__date">
                          <FaCheckCircle />
                          <span>
                            Resuelto:{" "}
                            {formatearFecha(reporte.fecha_resolucion)}
                          </span>
                        </div>
                      </article>
                    ))
                  )}
                </div>
              </section>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default MecanicoMantenimientoModal;