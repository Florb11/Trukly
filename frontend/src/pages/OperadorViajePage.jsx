import { useState, useMemo, useEffect } from "react";
import "./OperadorViajePage.css";
import { FaRoute, FaPlus, FaEye, FaSearch } from "react-icons/fa";
import DetalleViajeModal from "../components/DetalleViajeModal";
import CrearViajeModal from "../components/CrearViajeModal";
import { fetchConToken } from "../utils/fetchConToken";
import EditarViajeModal from "../components/EditarViajeModal";
import CancelarViajeModal from "../components/CancelarViajeModal";

const camposVaciosCrear = {
  origen: "",
  destino: "",
  fecha_salida: "",
  fecha_llegada: "",
  recorrido: "",
  Chofer_Usuario_idUsuario: "",
  Camion_id_camion: "",
  observaciones: "",
};

const ESTADO_OPCIONES = [
  "todos",
  "pendiente",
  "aceptado",
  "en curso",
  "finalizado",
  "cancelado",
];

function formatearFecha(fecha) {
  if (!fecha) return "-";
  const [y, m, d] = fecha.split("-");
  return `${d}/${m}/${y}`;
}

function OperadorViajesPage() {
  const [viajes, setViajes] = useState([]);
  const [busqueda, setBusqueda] = useState("");
  const [filtroEstado, setFiltroEstado] = useState("todos");
  const [viajeDetalle, setViajeDetalle] = useState(null);
  const [modalCrear, setModalCrear] = useState(false);
  const [form, setForm] = useState(camposVaciosCrear);
  const [errorForm, setErrorForm] = useState("");
  const [mensajeOk, setMensajeOk] = useState("");
  const [viajeEditar, setViajeEditar] = useState(null);
  const [viajeCancelar, setViajeCancelar] = useState(null);

  useEffect(() => {
    cargarViajes();
  }, []);

  const cargarViajes = async () => {
    try {
      const resultado = await fetchConToken(
        "http://localhost:5000/api/operador/viajes",
        { method: "GET" },
      );
      if (!resultado) return;
      const { respuesta, data } = resultado;
      if (!respuesta.ok)
        throw new Error(data.mensaje || "Error al obtener viajes");
      setViajes(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Error cargando viajes:", error);
    }
  };

  const viajesFiltrados = useMemo(() => {
    return viajes.filter((v) => {
      const texto = busqueda.toLowerCase();
      const coincideTexto =
        v.origen?.toLowerCase().includes(texto) ||
        v.destino?.toLowerCase().includes(texto) ||
        v.id_viaje?.toString().includes(texto);
      const coincideEstado =
        filtroEstado === "todos" || v.estado?.toLowerCase() === filtroEstado;
      return coincideTexto && coincideEstado;
    });
  }, [viajes, busqueda, filtroEstado]);

  const stats = useMemo(
    () => ({
      total: viajes.length,
      activos: viajes.filter(
        (v) =>
          v.estado?.toLowerCase() === "en curso" ||
          v.estado?.toLowerCase() === "aceptado",
      ).length,
      pendientes: viajes.filter((v) => v.estado?.toLowerCase() === "pendiente").length,
      cancelados: viajes.filter((v) => v.estado?.toLowerCase() === "cancelado").length,
    }),
    [viajes],
  );

  const abrirCrear = () => {
    setForm(camposVaciosCrear);
    setErrorForm("");
    setModalCrear(true);
  };

  const cerrarCrear = () => {
    setModalCrear(false);
    setErrorForm("");
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const crearViaje = async (e) => {
    e.preventDefault();

    const requeridos = [
      "origen",
      "destino",
      "fecha_salida",
      "Chofer_Usuario_idUsuario",
      "Camion_id_camion",
    ];
    for (const campo of requeridos) {
      if (!form[campo].toString().trim()) {
        setErrorForm("Completá todos los campos obligatorios.");
        return;
      }
    }

    try {
      const resultado = await fetchConToken(
        "http://localhost:5000/api/operador/viajes",
        {
          method: "POST",
          body: JSON.stringify({
            origen: form.origen,
            destino: form.destino,
            fecha_salida: form.fecha_salida,
            fecha_llegada: form.fecha_llegada || null,
            Chofer_Usuario_idUsuario: Number(form.Chofer_Usuario_idUsuario),
            Camion_id_camion: Number(form.Camion_id_camion),
            recorrido: Number(form.recorrido) || 0,
            observaciones: form.observaciones,
          }),
        },
      );
      if (!resultado) return;
      const { respuesta, data } = resultado;
      if (!respuesta.ok)
        throw new Error(data.mensaje || "Error al crear viaje");

      setMensajeOk("Viaje creado correctamente.");
      cerrarCrear();
      cargarViajes();
      setTimeout(() => setMensajeOk(""), 3500);
    } catch (error) {
      setErrorForm(error.message);
    }
  };

  return (
    <section className="op-viajes-page">
      <div className="op-viajes-header">
        <div>
          <span>Operador logístico</span>
          <h1>Viajes</h1>
          <p>
            Gestioná los viajes asignados, revisá el estado de cada operación y
            registrá nuevos recorridos.
          </p>
        </div>
        <div className="op-viajes-header__right">
          <button
            type="button"
            className="op-viajes-btn-crear"
            onClick={abrirCrear}
          >
            <FaPlus /> Nuevo viaje
          </button>
        </div>
      </div>

      <div className="op-viajes-stats">
        <article className="op-viajes-stat op-viajes-stat--info">
          <span>Total</span>
          <strong>{stats.total}</strong>
        </article>
        <article className="op-viajes-stat op-viajes-stat--active">
          <span>En curso / aceptados</span>
          <strong>{stats.activos}</strong>
        </article>
        <article className="op-viajes-stat op-viajes-stat--pending">
          <span>Pendientes</span>
          <strong>{stats.pendientes}</strong>
        </article>
        <article className="op-viajes-stat op-viajes-stat--cancelled">
          <span>Cancelados</span>
          <strong>{stats.cancelados}</strong>
        </article>
      </div>

      {mensajeOk && (
        <p className="admin-message admin-message--ok">{mensajeOk}</p>
      )}

      <article className="operator-table-card">
        <div className="operator-table-card__header">
          <h2>Listado de viajes</h2>
          <span>
            {viajesFiltrados.length} resultado
            {viajesFiltrados.length !== 1 ? "s" : ""}
          </span>
        </div>

        <div className="op-viajes-filtros">
          <div className="op-viajes-search">
            <FaSearch className="op-viajes-search__icon" />
            <input
              type="text"
              placeholder="Buscar por origen, destino o ID..."
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
            />
          </div>
          <div className="op-viajes-estado-tabs">
            {ESTADO_OPCIONES.map((estado) => (
              <button
                key={estado}
                type="button"
                className={`op-viajes-tab ${filtroEstado === estado ? "op-viajes-tab--active" : ""}`}
                onClick={() => setFiltroEstado(estado)}
              >
                {estado === "todos" ? "Todos" : estado}
              </button>
            ))}
          </div>
        </div>

        {viajesFiltrados.length === 0 ? (
          <p className="admin-message">No se encontraron viajes.</p>
        ) : (
          <div className="operator-table-wrap">
            <table className="operator-table op-viajes-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Origen</th>
                  <th>Destino</th>
                  <th>Salida</th>
                  <th>Llegada</th>
                  <th>Recorrido</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {viajesFiltrados.map((viaje) => {
                  const estadoLower = viaje.estado?.toLowerCase();
                  const puedeEditarse =
                    estadoLower !== "cancelado" && estadoLower !== "finalizado";
                  return (
                    <tr key={viaje.id_viaje}>
                      <td className="operator-table__id">#{viaje.id_viaje}</td>
                      <td>{viaje.origen}</td>
                      <td>{viaje.destino}</td>
                      <td>{formatearFecha(viaje.fecha_salida)}</td>
                      <td>{formatearFecha(viaje.fecha_llegada)}</td>
                      <td>{viaje.recorrido} km</td>
                      <td>
                        <span className={`chofer-badge chofer-badge--${estadoLower?.replace(" ", "-")}`}>
                          {viaje.estado}
                        </span>
                      </td>
                      <td style={{ display: "flex", gap: "8px", alignItems: "center" }}>
                        <button
                          type="button"
                          className="op-viajes-btn-ver"
                          onClick={() => setViajeDetalle(viaje)}
                        >
                          <FaEye /> Ver
                        </button>
                        {puedeEditarse && (
                          <>
                            <button
                              type="button"
                              className="op-viajes-btn-editar"
                              onClick={() => setViajeEditar(viaje)}
                            >
                              Editar
                            </button>
                            <button
                              type="button"
                              className="op-viajes-btn-cancelar"
                              onClick={() => setViajeCancelar(viaje)}
                            >
                              Cancelar
                            </button>
                          </>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </article>

      {modalCrear && (
        <CrearViajeModal
          form={form}
          error={errorForm}
          onChange={handleFormChange}
          onSubmit={crearViaje}
          onClose={cerrarCrear}
        />
      )}
      {viajeDetalle && (
        <DetalleViajeModal
          viaje={viajeDetalle}
          onClose={() => setViajeDetalle(null)}
        />
      )}
      {viajeEditar && (
        <EditarViajeModal
          viaje={viajeEditar}
          onClose={() => setViajeEditar(null)}
          onActualizado={() => {
            cargarViajes();
            setViajeEditar(null);
          }}
        />
      )}
      {viajeCancelar && (
        <CancelarViajeModal
          viaje={viajeCancelar}
          onClose={() => setViajeCancelar(null)}
          onActualizado={() => {
            cargarViajes();
            setViajeCancelar(null);
          }}
        />
      )}
    </section>
  );
}

export default OperadorViajesPage;