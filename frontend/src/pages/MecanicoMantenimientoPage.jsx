import { useEffect, useState } from "react";
import {
  FaEye,
  FaSearch,
  FaTools,
  FaTruck,
} from "react-icons/fa";
import { fetchConToken } from "../utils/fetchConToken";
import MecanicoMantenimientoModal from "../components/MecanicoMantenimientoModal";
import "./MecanicoMantenimientoPage.css";

function MecanicoMantenimientoPage() {
  const [camiones, setCamiones] = useState([]);
  const [busqueda, setBusqueda] = useState("");
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState("");

  const [modalAbierto, setModalAbierto] = useState(false);
  const [detalleMantenimiento, setDetalleMantenimiento] = useState(null);
  const [cargandoDetalle, setCargandoDetalle] = useState(false);
  const [errorDetalle, setErrorDetalle] = useState("");

  const cargarCamiones = async () => {
    try {
      setCargando(true);
      setError("");

      const resultado = await fetchConToken(
        "http://localhost:5000/api/mecanico/camiones-mantenimiento",
        {
          method: "GET",
        }
      );

      if (!resultado) return;

      const { respuesta, data } = resultado;

      if (!respuesta.ok) {
        throw new Error(
          data.mensaje ||
            data.msg ||
            "Error al cargar los camiones"
        );
      }

      setCamiones(data.camiones || []);
    } catch (error) {
      setError(error.message);
    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarCamiones();
  }, []);

  const normalizarTexto = (texto) => {
    return texto?.toString().trim().toLowerCase() || "";
  };

  const camionesFiltrados = camiones.filter((item) => {
    const textoBusqueda = normalizarTexto(busqueda);
    const camion = item.camion;

    return (
      normalizarTexto(camion?.matricula).includes(textoBusqueda) ||
      normalizarTexto(camion?.marca).includes(textoBusqueda) ||
      normalizarTexto(camion?.modelo).includes(textoBusqueda) ||
      normalizarTexto(camion?.estado).includes(textoBusqueda)
    );
  });

  const verMantenimiento = async (idCamion) => {
    try {
      setModalAbierto(true);
      setCargandoDetalle(true);
      setErrorDetalle("");
      setDetalleMantenimiento(null);

      const resultado = await fetchConToken(
        `http://localhost:5000/api/mecanico/camiones/${idCamion}/mantenimiento`,
        {
          method: "GET",
        }
      );

      if (!resultado) return;

      const { respuesta, data } = resultado;

      if (!respuesta.ok) {
        throw new Error(
          data.mensaje ||
            data.msg ||
            "Error al cargar el mantenimiento del camión"
        );
      }

      setDetalleMantenimiento(data);
    } catch (error) {
      setErrorDetalle(error.message);
    } finally {
      setCargandoDetalle(false);
    }
  };

  const cerrarModal = () => {
    setModalAbierto(false);
    setDetalleMantenimiento(null);
    setErrorDetalle("");
  };

  if (cargando) {
    return (
      <section className="mecanico-mantenimiento-page">
        <p className="mecanico-mantenimiento-message">
          Cargando camiones...
        </p>
      </section>
    );
  }

  return (
    <section className="mecanico-mantenimiento-page">
      <div className="mecanico-mantenimiento-header">
        <div>
          <span>Control de unidades</span>

          <h1>Mantenimiento</h1>

          <p>
            Consultá los reportes pendientes y el historial de reparaciones de
            cada camión.
          </p>
        </div>

        <div className="mecanico-mantenimiento-header__icon">
          <FaTools />
        </div>
      </div>

      {error && (
        <p className="mecanico-mantenimiento-message mecanico-mantenimiento-message--error">
          {error}
        </p>
      )}

      <div className="mecanico-mantenimiento-toolbar">
        <div className="mecanico-mantenimiento-search">
          <FaSearch />

          <input
            type="text"
            placeholder="Buscar por matrícula, marca, modelo o estado..."
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
          />
        </div>
      </div>

      <div className="mecanico-mantenimiento-table-wrap">
        <table className="mecanico-mantenimiento-table">
          <thead>
            <tr>
              <th>Camión</th>
              <th>Marca</th>
              <th>Modelo</th>
              <th>Estado</th>
              <th>Pendientes</th>
              <th>Reparaciones realizadas</th>
              <th>Acción</th>
            </tr>
          </thead>

          <tbody>
            {camionesFiltrados.length === 0 ? (
              <tr>
                <td colSpan="7">
                  <div className="mecanico-mantenimiento-empty">
                    <FaTruck />
                    <p>No se encontraron camiones.</p>
                  </div>
                </td>
              </tr>
            ) : (
              camionesFiltrados.map((item) => {
                const camion = item.camion;

                const estadoClase = normalizarTexto(camion.estado)
                  .normalize("NFD")
                  .replace(/[\u0300-\u036f]/g, "")
                  .replaceAll(" ", "-");

                return (
                  <tr key={camion.id_camion}>
                    <td data-label="Camión">
                      <div className="mecanico-mantenimiento-camion">
                        <div className="mecanico-mantenimiento-camion__icon">
                          <FaTruck />
                        </div>

                        <div>
                          <strong>{camion.matricula || "Sin matrícula"}</strong>
                          <span>Unidad #{camion.id_camion}</span>
                        </div>
                      </div>
                    </td>

                    <td data-label="Marca">
                      {camion.marca || "-"}
                    </td>

                    <td data-label="Modelo">
                      {camion.modelo || "-"}
                    </td>

                    <td data-label="Estado">
                      <span
                        className={`mecanico-mantenimiento-status mecanico-mantenimiento-status--${estadoClase}`}
                      >
                        {camion.estado || "Sin estado"}
                      </span>
                    </td>

                    <td data-label="Pendientes">
                      <span className="mecanico-mantenimiento-count mecanico-mantenimiento-count--pending">
                        {item.cantidad_reportes_pendientes || 0}
                      </span>
                    </td>

                    <td data-label="Reparaciones realizadas">
                      <span className="mecanico-mantenimiento-count mecanico-mantenimiento-count--resolved">
                        {item.cantidad_reparaciones_realizadas || 0}
                      </span>
                    </td>

                    <td data-label="Acción">
                      <button
                        type="button"
                        className="mecanico-mantenimiento-action"
                        onClick={() =>
                          verMantenimiento(camion.id_camion)
                        }
                      >
                        <FaEye />
                        Ver mantenimiento
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      <MecanicoMantenimientoModal
        abierto={modalAbierto}
        onCerrar={cerrarModal}
        detalle={detalleMantenimiento}
        cargando={cargandoDetalle}
        error={errorDetalle}
      />
    </section>
  );
}

export default MecanicoMantenimientoPage;
