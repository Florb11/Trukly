import { useEffect, useState } from "react";
import { fetchConToken } from "../utils/fetchConToken";
import "./CargasViajeDetalle.css";

const kg = (valor) => `${Number(valor).toLocaleString("es-AR", { maximumFractionDigits: 3 })} kg`;

export default function CargasViajeDetalle({ idViaje }) {
  const [resultado, setResultado] = useState(null);
  const [intento, setIntento] = useState(0);
  useEffect(() => {
    if (!idViaje) return;
    const controlador = new AbortController();
    fetchConToken(`${import.meta.env.VITE_API_URL || "http://localhost:5000"}/api/viaje/${idViaje}/cargas`, {
      method: "GET", signal: controlador.signal,
    }).then((respuesta) => {
      if (!respuesta || controlador.signal.aborted) return;
      if (!respuesta.respuesta.ok) throw new Error(respuesta.data.mensaje || "No se pudieron consultar las cargas de este viaje.");
      setResultado({ id: idViaje, intento, datos: respuesta.data });
    }).catch((error) => {
      if (!controlador.signal.aborted) setResultado({ id: idViaje, intento, error: error.message });
    });
    return () => controlador.abort();
  }, [idViaje, intento]);
  const actual = resultado?.id === idViaje && resultado?.intento === intento ? resultado : null;
  const datos = actual?.datos;
  return <section className="cargas-detalle" aria-label="Cargas del viaje">
    <h3>Cargas del viaje</h3>
    {!actual && <p role="status">Cargando cargas...</p>}
    {actual?.error && <div className="cargas-detalle__error"><p role="alert">{actual.error}</p><button type="button" onClick={() => setIntento((valor) => valor + 1)}>Reintentar</button></div>}
    {datos && <>
      <dl className="cargas-detalle__resumen"><div><dt>Peso total</dt><dd>{kg(datos.peso_total_kg)}</dd></div><div><dt>Capacidad del camión</dt><dd>{kg(datos.capacidad_kg)}</dd></div><div><dt>Disponible</dt><dd>{kg(datos.disponible_kg)}</dd></div></dl>
      {datos.cargas.length === 0 ? <p className="cargas-detalle__vacio">Este viaje no tiene cargas registradas.</p> : <div className="cargas-detalle__lista">{datos.cargas.map((carga) => <article key={carga.id_carga}>
        <div className="cargas-detalle__cabecera"><strong>{carga.descripcion}</strong><span>{kg(carga.peso)}</span></div>
        <dl className="cargas-detalle__datos"><div><dt>Tipo</dt><dd>{carga.tipo}</dd></div>{carga.bultos != null && <div><dt>Bultos</dt><dd>{carga.bultos}</dd></div>}{carga.remito && <div><dt>Remito</dt><dd>{carga.remito}</dd></div>}</dl>
      </article>)}</div>}
    </>}
  </section>;
}
