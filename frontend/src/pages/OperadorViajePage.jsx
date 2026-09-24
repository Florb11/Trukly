import { useState, useMemo, useEffect } from "react";
import "./OperadorViajePage.css";
import {
  FaCheckCircle,
  FaClock,
  FaEye,
  FaPlus,
  FaRoute,
  FaSearch,
  FaTimesCircle,
} from "react-icons/fa";
import DetalleViajeModal from "../components/DetalleViajeModal";
import CrearViajeModal from "../components/CrearViajeModal";
import { fetchConToken } from "../utils/fetchConToken";
import EditarViajeModal from "../components/EditarViajeModal";
import CancelarViajeModal from "../components/CancelarViajeModal";
import { getTruckRoute, hasGeoapifyKey, reversePlace } from "../utils/geoapify";

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

  const [choferes, setChoferes] = useState([]);
  const [camiones, setCamiones] = useState([]);
  const [cargandoRecursos, setCargandoRecursos] = useState(false);
  const [errorRecursos, setErrorRecursos] = useState("");
  const [lugares, setLugares] = useState({ origen: null, destino: null });
  const [ruta, setRuta] = useState(null);
  const [cargandoRuta, setCargandoRuta] = useState(false);
  const [errorRuta, setErrorRuta] = useState("");
  const [puntoMapa, setPuntoMapa] = useState("origen");
  const [cargandoLugarMapa, setCargandoLugarMapa] = useState(false);
  const [guardando, setGuardando] = useState(false);

  useEffect(() => {
    cargarViajes();
  }, []);

  useEffect(() => {
    if (!lugares.origen || !lugares.destino) return undefined;

    const controller = new AbortController();
    const calcular = async () => {
      try {
        setCargandoRuta(true);
        setErrorRuta("");
        const resultado = await getTruckRoute(lugares.origen, lugares.destino, controller.signal);
        if (controller.signal.aborted) return;
        setRuta(resultado.feature);
        setForm((prev) => ({ ...prev, recorrido: String(resultado.kilometers) }));
      } catch (error) {
        if (error.name !== "AbortError") setErrorRuta(error.message);
      } finally {
        if (!controller.signal.aborted) setCargandoRuta(false);
      }
    };
    calcular();
    return () => controller.abort();
  }, [lugares.origen, lugares.destino]);

  async function cargarViajes() {
    try {
      const resultado = await fetchConToken(
        `${import.meta.env.VITE_API_URL || "http://localhost:5000"}/api/operador/viajes`,
        { method: "GET" },
      );

      if (!resultado) return;

      const { respuesta, data } = resultado;

      if (!respuesta.ok) {
        throw new Error(data.mensaje || "Error al obtener viajes");
      }

      setViajes(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("Error cargando viajes:", error);
    }
  };

  const cargarChoferes = async () => {
    try {
      const resultado = await fetchConToken(
        `${import.meta.env.VITE_API_URL || "http://localhost:5000"}/api/operador/choferes?disponibles=1`,
        { method: "GET" },
      );

      if (!resultado) return;

      const { respuesta, data } = resultado;

      if (!respuesta.ok) {
        throw new Error(data.mensaje || "Error al obtener choferes");
      }

      setChoferes(Array.isArray(data) ? data : []);
    } catch (error) {
      setChoferes([]);
      throw error;
    }
  };

  const cargarCamiones = async () => {
    try {
      const resultado = await fetchConToken(
        `${import.meta.env.VITE_API_URL || "http://localhost:5000"}/api/operador/camiones?disponibles=1`,
        { method: "GET" },
      );

      if (!resultado) return;

      const { respuesta, data } = resultado;

      if (!respuesta.ok) {
        throw new Error(data.mensaje || "Error al obtener camiones");
      }

      setCamiones(Array.isArray(data) ? data : []);
    } catch (error) {
      setCamiones([]);
      throw error;
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
      pendientes: viajes.filter((v) => v.estado?.toLowerCase() === "pendiente")
        .length,
      cancelados: viajes.filter((v) => v.estado?.toLowerCase() === "cancelado")
        .length,
    }),
    [viajes],
  );

  const abrirCrear = () => {
    setForm(camposVaciosCrear);
    setErrorForm("");
    setLugares({ origen: null, destino: null });
    setRuta(null);
    setErrorRuta("");
    setPuntoMapa("origen");
    setErrorRecursos("");
    setChoferes([]);
    setCamiones([]);
    setCargandoRecursos(true);
    setModalCrear(true);
    Promise.allSettled([cargarChoferes(), cargarCamiones()]).then((resultados) => {
      if (resultados.some((resultado) => resultado.status === "rejected")) {
        setErrorRecursos("No se pudieron cargar los recursos disponibles.");
      }
      setCargandoRecursos(false);
    });
  };

  const cerrarCrear = () => {
    setModalCrear(false);
    setErrorForm("");
  };

  const handleFormChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  const cambiarLugar = (campo, texto) => {
    setForm((prev) => ({ ...prev, [campo]: texto, recorrido: "" }));
    setLugares((prev) => ({ ...prev, [campo]: null }));
    setRuta(null);
    setErrorRuta("");
  };

  const seleccionarLugar = (campo, lugar) => {
    setForm((prev) => ({ ...prev, [campo]: lugar.label, recorrido: "" }));
    setLugares((prev) => ({ ...prev, [campo]: lugar }));
    setRuta(null);
    setErrorRuta("");
  };

  const elegirEnMapa = async ({ lat, lng }) => {
    if (!hasGeoapifyKey || cargandoLugarMapa) return;
    try {
      setCargandoLugarMapa(true);
      setErrorRuta("");
      const label = await reversePlace(lat, lng);
      seleccionarLugar(puntoMapa, { label, lat, lon: lng });
    } catch (error) {
      setErrorRuta(error.message);
    } finally {
      setCargandoLugarMapa(false);
    }
  };

  const crearViaje = async (e) => {
    e.preventDefault();

    if (!lugares.origen || !lugares.destino || !ruta || cargandoRuta || cargandoLugarMapa) {
      setErrorForm("Elegí dos ubicaciones y esperá a que se calcule la ruta.");
      return;
    }

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
      setGuardando(true);
      const resultado = await fetchConToken(
        `${import.meta.env.VITE_API_URL || "http://localhost:5000"}/api/operador/viajes`,
        {
          method: "POST",
          body: JSON.stringify({
            origen: form.origen,
            destino: form.destino,
            origen_lat: lugares.origen.lat,
            origen_lon: lugares.origen.lon,
            destino_lat: lugares.destino.lat,
            destino_lon: lugares.destino.lon,
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

      if (!respuesta.ok) {
        throw new Error(data.mensaje || "Error al crear viaje");
      }

      setMensajeOk("Viaje creado correctamente.");
      cerrarCrear();
      cargarViajes();
      setTimeout(() => setMensajeOk(""), 3500);
    } catch (error) {
      setErrorForm(error.message);
    } finally {
      setGuardando(false);
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
          <div className="dashboard-heading-icon" aria-hidden="true"><FaRoute /></div>
        </div>
      </div>

      <div className="op-viajes-stats">
        <article className="op-viajes-stat op-viajes-stat--info">
          <span>Total</span>
          <strong>{stats.total}</strong>
          <div className="op-viajes-stat__icon" aria-hidden="true"><FaRoute /></div>
        </article>

        <article className="op-viajes-stat op-viajes-stat--active">
          <span>En curso / aceptados</span>
          <strong>{stats.activos}</strong>
          <div className="op-viajes-stat__icon" aria-hidden="true"><FaCheckCircle /></div>
        </article>

        <article className="op-viajes-stat op-viajes-stat--pending">
          <span>Pendientes</span>
          <strong>{stats.pendientes}</strong>
          <div className="op-viajes-stat__icon" aria-hidden="true"><FaClock /></div>
        </article>

        <article className="op-viajes-stat op-viajes-stat--cancelled">
          <span>Cancelados</span>
          <strong>{stats.cancelados}</strong>
          <div className="op-viajes-stat__icon" aria-hidden="true"><FaTimesCircle /></div>
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
                className={`op-viajes-tab ${
                  filtroEstado === estado ? "op-viajes-tab--active" : ""
                }`}
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
                      <td data-label="#" className="operator-table__id">{viaje.id_viaje}</td>
                      <td data-label="Origen">{viaje.origen}</td>
                      <td data-label="Destino">{viaje.destino}</td>
                      <td data-label="Salida">{formatearFecha(viaje.fecha_salida)}</td>
                      <td data-label="Llegada">{formatearFecha(viaje.fecha_llegada)}</td>
                      <td data-label="Recorrido">{viaje.recorrido} km</td>
                      <td data-label="Estado">
                        <span
                          className={`chofer-badge chofer-badge--${estadoLower?.replace(
                            " ",
                            "-",
                          )}`}
                        >
                          {viaje.estado}
                        </span>
                      </td>
                      <td data-label="Acciones" className="op-viajes-table__acciones">
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
          errorRecursos={errorRecursos}
          cargandoRecursos={cargandoRecursos}
          geoapifyConfigurado={hasGeoapifyKey}
          lugares={lugares}
          ruta={ruta}
          cargandoRuta={cargandoRuta}
          cargandoLugarMapa={cargandoLugarMapa}
          errorRuta={errorRuta}
          puntoMapa={puntoMapa}
          onPuntoMapaChange={setPuntoMapa}
          onLugarChange={cambiarLugar}
          onLugarSelect={seleccionarLugar}
          onMapPick={elegirEnMapa}
          guardando={guardando}
          onChange={handleFormChange}
          onSubmit={crearViaje}
          onClose={cerrarCrear}
          choferes={choferes}
          camiones={camiones}
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
