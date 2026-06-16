import { useState, useMemo, useEffect } from "react";
import { FaSearch, FaTruck } from "react-icons/fa";
import { fetchConToken } from "../utils/fetchConToken";
import "./OperadorCamionesPage.css";

const ESTADO_OPCIONES = ["todos", "disponible", "en viaje", "en mantenimiento", "inactivo"];

function OperadorCamionesPage() {
  const [camiones, setCamiones] = useState([]);
  const [busqueda, setBusqueda] = useState("");
  const [filtroEstado, setFiltroEstado] = useState("todos");

  useEffect(() => {
    cargarCamiones();
  }, []);

  const cargarCamiones = async () => {
    try {
      const resultado = await fetchConToken("http://localhost:5000/api/operador/camiones", { method: "GET" });
      if (!resultado) return;
      const { respuesta, data } = resultado;
      if (!respuesta.ok) throw new Error(data.mensaje || "Error al obtener camiones");
      setCamiones(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Error cargando camiones:", error);
    }
  };

  const camionesFiltrados = useMemo(() => {
    return camiones.filter((c) => {
      const texto = busqueda.toLowerCase();
      const coincideTexto =
        c.matricula?.toLowerCase().includes(texto) ||
        c.marca?.toLowerCase().includes(texto) ||
        c.modelo?.toLowerCase().includes(texto) ||
        c.id_camion?.toString().includes(texto);
      const coincideEstado = filtroEstado === "todos" || c.estado === filtroEstado;
      return coincideTexto && coincideEstado;
    });
  }, [camiones, busqueda, filtroEstado]);

  const getBadgeClass = (estado) => {
    if (estado === "disponible") return "camion-badge camion-badge--disponible";
    if (estado === "en viaje") return "camion-badge camion-badge--en-viaje";
    if (estado === "en mantenimiento") return "camion-badge camion-badge--mantenimiento";
    return "camion-badge camion-badge--inactivo";
  };

  return (
    <section className="op-camiones-page">
      <div className="op-camiones-header">
        <div>
          <span>Operador logístico</span>
          <h1>Camiones</h1>
          <p>Consultá el estado actual de la flota disponible.</p>
        </div>
      </div>

      <article className="operator-table-card">
        <div className="operator-table-card__header">
          <h2>Listado de camiones</h2>
          <span>{camionesFiltrados.length} resultado{camionesFiltrados.length !== 1 ? "s" : ""}</span>
        </div>

        <div className="op-camiones-filtros">
          <div className="op-camiones-search">
            <FaSearch className="op-camiones-search__icon" />
            <input
              type="text"
              placeholder="Buscar por matrícula, marca o modelo..."
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
            />
          </div>
          <div className="op-camiones-estado-tabs">
            {ESTADO_OPCIONES.map((estado) => (
              <button
                key={estado}
                type="button"
                className={`op-camiones-tab ${filtroEstado === estado ? "op-camiones-tab--active" : ""}`}
                onClick={() => setFiltroEstado(estado)}
              >
                {estado === "todos" ? "Todos" : estado}
              </button>
            ))}
          </div>
        </div>

        {camionesFiltrados.length === 0 ? (
          <p className="admin-message">No se encontraron camiones.</p>
        ) : (
          <div className="operator-table-wrap">
            <table className="operator-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Matrícula</th>
                  <th>Marca</th>
                  <th>Modelo</th>
                  <th>Capacidad</th>
                  <th>Nro. Tanque</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                {camionesFiltrados.map((camion) => (
                  <tr key={camion.id_camion}>
                    <td className="operator-table__id">{camion.id_camion}</td>
                    <td>{camion.matricula}</td>
                    <td>{camion.marca}</td>
                    <td>{camion.modelo}</td>
                    <td>{camion.capacidad_carga} t</td>
                    <td>{camion.nroTanque}</td>
                    <td>
                      <span className={getBadgeClass(camion.estado)}>
                        {camion.estado}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </article>
    </section>
  );
}

export default OperadorCamionesPage;