import { useState, useMemo } from "react";
import "./OperadorViajePage.css";
import {
  FaRoute,
  FaPlus,
  FaEye,
  FaSearch,
  FaTruck,
  FaUser,
  FaMapMarkerAlt,
  FaCalendarAlt,
  FaTachometerAlt,
} from "react-icons/fa";
import DetalleViajeModal from "../components/DetalleViajeModal";

const viajesHardcoded = [
  {
    id_viaje: 1,
    origen: "Buenos Aires",
    destino: "Rosario",
    fecha_salida: "2026-06-01",
    fecha_llegada: "2026-06-02",
    recorrido: 300,
    estado: "finalizado",
    chofer: "Carlos Méndez",
    camion: "ABC 123",
    observaciones: "Entrega sin inconvenientes.",
  },
  {
    id_viaje: 2,
    origen: "Córdoba",
    destino: "Mendoza",
    fecha_salida: "2026-06-05",
    fecha_llegada: "2026-06-06",
    recorrido: 720,
    estado: "en-curso",
    chofer: "Laura Gómez",
    camion: "DEF 456",
    observaciones: "",
  },
  {
    id_viaje: 3,
    origen: "Rosario",
    destino: "Santa Fe",
    fecha_salida: "2026-06-08",
    fecha_llegada: "2026-06-08",
    recorrido: 170,
    estado: "pendiente",
    chofer: "Martín Torres",
    camion: "GHI 789",
    observaciones: "Esperando confirmación del chofer.",
  },
  {
    id_viaje: 4,
    origen: "Buenos Aires",
    destino: "La Plata",
    fecha_salida: "2026-06-10",
    fecha_llegada: "2026-06-10",
    recorrido: 60,
    estado: "aceptado",
    chofer: "Sofía Ruiz",
    camion: "JKL 012",
    observaciones: "",
  },
  {
    id_viaje: 5,
    origen: "Tucumán",
    destino: "Salta",
    fecha_salida: "2026-06-03",
    fecha_llegada: "2026-06-04",
    recorrido: 310,
    estado: "cancelado",
    chofer: "Diego Herrera",
    camion: "MNO 345",
    observaciones: "Falla mecánica en ruta.",
  },
  {
    id_viaje: 6,
    origen: "Mar del Plata",
    destino: "Buenos Aires",
    fecha_salida: "2026-06-11",
    fecha_llegada: "2026-06-11",
    recorrido: 400,
    estado: "pendiente",
    chofer: "Pablo Acosta",
    camion: "PQR 678",
    observaciones: "",
  },
];

const ESTADO_OPCIONES = [
  "todos",
  "pendiente",
  "aceptado",
  "en-curso",
  "finalizado",
  "cancelado",
];

const estadoLabel = (estado) => estado.replace("-", " ");

function formatearFecha(fecha) {
  if (!fecha) return "-";
  const [y, m, d] = fecha.split("-");
  return `${d}/${m}/${y}`;
}

const camposVaciosCrear = {
  origen: "",
  destino: "",
  fecha_salida: "",
  fecha_llegada: "",
  recorrido: "",
  chofer: "",
  camion: "",
  observaciones: "",
};

function OperadorViajesPage() {
  const [viajes, setViajes] = useState(viajesHardcoded);
  const [busqueda, setBusqueda] = useState("");
  const [filtroEstado, setFiltroEstado] = useState("todos");

  const [viajeDetalle, setViajeDetalle] = useState(null);
  const [modalCrear, setModalCrear] = useState(false);
  const [form, setForm] = useState(camposVaciosCrear);
  const [errorForm, setErrorForm] = useState("");
  const [mensajeOk, setMensajeOk] = useState("");

  const viajesFiltrados = useMemo(() => {
    return viajes.filter((v) => {
      const textoMatch =
        busqueda === "" ||
        v.origen.toLowerCase().includes(busqueda.toLowerCase()) ||
        v.destino.toLowerCase().includes(busqueda.toLowerCase()) ||
        v.chofer.toLowerCase().includes(busqueda.toLowerCase()) ||
        v.camion.toLowerCase().includes(busqueda.toLowerCase());

      const estadoMatch = filtroEstado === "todos" || v.estado === filtroEstado;

      return textoMatch && estadoMatch;
    });
  }, [viajes, busqueda, filtroEstado]);

  const stats = useMemo(
    () => ({
      total: viajes.length,
      activos: viajes.filter(
        (v) => v.estado === "en-curso" || v.estado === "aceptado",
      ).length,
      pendientes: viajes.filter((v) => v.estado === "pendiente").length,
      cancelados: viajes.filter((v) => v.estado === "cancelado").length,
    }),
    [viajes],
  );

  const abrirDetalle = (viaje) => {
    setViajeDetalle(viaje);
  };

  const cerrarDetalle = () => setViajeDetalle(null);

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

  const crearViaje = () => {
    const requeridos = [
      "origen",
      "destino",
      "fecha_salida",
      "fecha_llegada",
      "chofer",
      "camion",
    ];
    for (const campo of requeridos) {
      if (!form[campo].trim()) {
        setErrorForm("Completá todos los campos obligatorios.");
        return;
      }
    }

    const nuevoViaje = {
      ...form,
      id_viaje:
        viajes.length > 0 ? Math.max(...viajes.map((v) => v.id_viaje)) + 1 : 1,
      estado: "pendiente",
      recorrido: form.recorrido || 0,
    };

    setViajes((prev) => [nuevoViaje, ...prev]);
    setMensajeOk("Viaje creado correctamente.");
    cerrarCrear();

    setTimeout(() => setMensajeOk(""), 3500);
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
          <div className="op-viajes-header__icon">
            <FaRoute />
          </div>
          <button
            type="button"
            className="op-viajes-btn-crear"
            onClick={abrirCrear}
          >
            <FaPlus />
            Nuevo viaje
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
              placeholder="Buscar por origen, destino, chofer o camión..."
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
                {estado === "todos" ? "Todos" : estadoLabel(estado)}
              </button>
            ))}
          </div>
        </div>

        {viajesFiltrados.length === 0 ? (
          <p className="admin-message">
            No se encontraron viajes con ese criterio.
          </p>
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
                  <th>Chofer</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {viajesFiltrados.map((viaje) => (
                  <tr key={viaje.id_viaje}>
                    <td className="operator-table__id">#{viaje.id_viaje}</td>
                    <td>{viaje.origen}</td>
                    <td>{viaje.destino}</td>
                    <td>{formatearFecha(viaje.fecha_salida)}</td>
                    <td>{formatearFecha(viaje.fecha_llegada)}</td>
                    <td>{viaje.recorrido} km</td>
                    <td>{viaje.chofer}</td>
                    <td>
                      <span
                        className={`chofer-badge chofer-badge--${viaje.estado}`}
                      >
                        {estadoLabel(viaje.estado)}
                      </span>
                    </td>
                    <td>
                      <button
                        type="button"
                        className="op-viajes-btn-ver"
                        onClick={() => abrirDetalle(viaje)}
                      >
                        <FaEye />
                        Ver
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </article>
    {viajeDetalle && (
        <DetalleViajeModal 
          viaje={viajeDetalle} /* <--- ACÁ ESTÁ EL CAMBIO */
          onClose={cerrarDetalle} 
        />
      )}

    </section>
  
  );
}

export default OperadorViajesPage;
