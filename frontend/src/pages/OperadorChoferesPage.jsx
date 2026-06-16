import { useState, useMemo, useEffect } from "react";
import { FaSearch } from "react-icons/fa";
import { fetchConToken } from "../utils/fetchConToken";
import "./OperadorChoferesPage.css";

const ESTADO_OPCIONES = ["todos", "activo", "inactivo", "pendiente"];

function OperadorChoferesPage() {
  const [choferes, setChoferes] = useState([]);
  const [busqueda, setBusqueda] = useState("");
  const [filtroEstado, setFiltroEstado] = useState("todos");

  useEffect(() => {
    cargarChoferes();
  }, []);

  const cargarChoferes = async () => {
    try {
      const resultado = await fetchConToken("http://localhost:5000/api/operador/choferes", { method: "GET" });
      if (!resultado) return;
      const { respuesta, data } = resultado;
      if (!respuesta.ok) throw new Error(data.mensaje || "Error al obtener choferes");
      setChoferes(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Error cargando choferes:", error);
    }
  };

  const choferesFiltrados = useMemo(() => {
    return choferes.filter((c) => {
      const texto = busqueda.toLowerCase();
      const coincideTexto =
        c.nombre?.toLowerCase().includes(texto) ||
        c.apellido?.toLowerCase().includes(texto) ||
        c.legajo?.toLowerCase().includes(texto) ||
        c.licencia?.toLowerCase().includes(texto) ||
        c.id_usuario?.toString().includes(texto);
      const coincideEstado = filtroEstado === "todos" || c.estado === filtroEstado;
      return coincideTexto && coincideEstado;
    });
  }, [choferes, busqueda, filtroEstado]);

  const getBadgeClass = (estado) => {
    if (estado === "activo") return "chofer-estado-badge chofer-estado-badge--activo";
    if (estado === "inactivo") return "chofer-estado-badge chofer-estado-badge--inactivo";
    return "chofer-estado-badge chofer-estado-badge--pendiente";
  };

  return (
    <section className="op-choferes-page">
      <div className="op-choferes-header">
        <div>
          <span>Operador logístico</span>
          <h1>Choferes</h1>
          <p>Consultá el listado de choferes disponibles para asignar a viajes.</p>
        </div>
      </div>

      <article className="operator-table-card">
        <div className="operator-table-card__header">
          <h2>Listado de choferes</h2>
          <span>{choferesFiltrados.length} resultado{choferesFiltrados.length !== 1 ? "s" : ""}</span>
        </div>

        <div className="op-choferes-filtros">
          <div className="op-choferes-search">
            <FaSearch className="op-choferes-search__icon" />
            <input
              type="text"
              placeholder="Buscar por nombre, apellido, legajo o licencia..."
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
            />
          </div>
          <div className="op-choferes-estado-tabs">
            {ESTADO_OPCIONES.map((estado) => (
              <button
                key={estado}
                type="button"
                className={`op-choferes-tab ${filtroEstado === estado ? "op-choferes-tab--active" : ""}`}
                onClick={() => setFiltroEstado(estado)}
              >
                {estado === "todos" ? "Todos" : estado}
              </button>
            ))}
          </div>
        </div>

        {choferesFiltrados.length === 0 ? (
          <p className="admin-message">No se encontraron choferes.</p>
        ) : (
          <div className="operator-table-wrap">
            <table className="operator-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Nombre</th>
                  <th>Apellido</th>
                  <th>Legajo</th>
                  <th>Licencia</th>
                  <th>Venc. Licencia</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                {choferesFiltrados.map((chofer) => (
                  <tr key={chofer.id_usuario}>
                    <td className="operator-table__id">{chofer.id_usuario}</td>
                    <td>{chofer.nombre}</td>
                    <td>{chofer.apellido}</td>
                    <td>{chofer.legajo}</td>
                    <td>{chofer.licencia}</td>
                    <td>{chofer.vencimientoLicencia}</td>
                    <td>
                      <span className={getBadgeClass(chofer.estado)}>
                        {chofer.estado}
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

export default OperadorChoferesPage;