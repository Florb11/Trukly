import { lazy, Suspense } from "react";
import "./CrearViajeModal.css";
import GeoapifyPlaceField from "./GeoapifyPlaceField";

const ViajeRouteMap = lazy(() => import("./ViajeRouteMap"));

function CrearViajeModal({
  form,
  error,
  errorRecursos,
  cargandoRecursos,
  geoapifyConfigurado,
  lugares,
  ruta,
  cargandoRuta,
  cargandoLugarMapa,
  errorRuta,
  puntoMapa,
  onPuntoMapaChange,
  onLugarChange,
  onLugarSelect,
  onMapPick,
  guardando,
  onChange,
  onSubmit,
  onClose,
  choferes = [],
  camiones = [],
}) {
  return (
    <div className="viaje-modal-overlay">
      <div className="viaje-modal">
        <div className="viaje-modal__header">
          <div>
            <span>Operador logístico</span>
            <h2>Nuevo viaje</h2>
          </div>
          <button type="button" onClick={onClose} aria-label="Cerrar">
            ✕
          </button>
        </div>

        <form className="viaje-modal__form" onSubmit={onSubmit}>
          {!geoapifyConfigurado && (
            <p className="viaje-modal__error">Falta configurar VITE_GEOAPIFY_API_KEY para buscar ubicaciones.</p>
          )}
          <div className="viaje-modal__row">
            <GeoapifyPlaceField
              id="origen"
              label="Punto de partida"
              value={form.origen}
              selected={Boolean(lugares.origen)}
              onChange={(texto) => onLugarChange("origen", texto)}
              onSelect={(lugar) => onLugarSelect("origen", lugar)}
            />
            <GeoapifyPlaceField
              id="destino"
              label="Punto de destino"
              value={form.destino}
              selected={Boolean(lugares.destino)}
              onChange={(texto) => onLugarChange("destino", texto)}
              onSelect={(lugar) => onLugarSelect("destino", lugar)}
            />
          </div>

          {geoapifyConfigurado && (
            <div className="viaje-modal__route">
              <div className="viaje-modal__route-top">
                <span>Mapa de la ruta</span>
                <div className="viaje-modal__map-mode" role="group" aria-label="Punto a ajustar en el mapa">
                  <button type="button" className={puntoMapa === "origen" ? "is-active" : ""} onClick={() => onPuntoMapaChange("origen")}>Origen</button>
                  <button type="button" className={puntoMapa === "destino" ? "is-active" : ""} onClick={() => onPuntoMapaChange("destino")}>Destino</button>
                </div>
              </div>
              <Suspense fallback={<div className="viaje-modal__map" />}>
                <ViajeRouteMap origin={lugares.origen} destination={lugares.destino} route={ruta} onPick={onMapPick} />
              </Suspense>
              {cargandoLugarMapa && <p className="viaje-modal__route-status">Buscando ubicación...</p>}
              {cargandoRuta && <p className="viaje-modal__route-status">Calculando ruta...</p>}
              {errorRuta && <p className="viaje-modal__route-status viaje-modal__route-status--error">{errorRuta}</p>}
            </div>
          )}

          <div className="viaje-modal__row">
            <div className="viaje-modal__field">
              <label htmlFor="fecha_salida">Fecha de salida</label>
              <input
                type="date"
                id="fecha_salida"
                name="fecha_salida"
                value={form.fecha_salida}
                onChange={onChange}
              />
            </div>

            <div className="viaje-modal__field">
              <label htmlFor="fecha_llegada">Fecha de llegada</label>
              <input
                type="date"
                id="fecha_llegada"
                name="fecha_llegada"
                value={form.fecha_llegada}
                onChange={onChange}
              />
            </div>
          </div>

          <div className="viaje-modal__row">
            <div className="viaje-modal__field">
              <label htmlFor="Chofer_Usuario_idUsuario">Chofer</label>
              <select
                id="Chofer_Usuario_idUsuario"
                name="Chofer_Usuario_idUsuario"
                value={form.Chofer_Usuario_idUsuario}
                onChange={onChange}
              >
                <option value="">
                  {cargandoRecursos ? "Cargando choferes..." : choferes.length ? "Seleccionar chofer" : "No hay choferes disponibles"}
                </option>

                {choferes.map((chofer) => (
                  <option key={chofer.id_usuario} value={chofer.id_usuario}>
                    {chofer.nombre} {chofer.apellido} - Legajo {chofer.legajo}
                  </option>
                ))}
              </select>
            </div>

            <div className="viaje-modal__field">
              <label htmlFor="Camion_id_camion">Camión</label>
              <select
                id="Camion_id_camion"
                name="Camion_id_camion"
                value={form.Camion_id_camion}
                onChange={onChange}
              >
                <option value="">
                  {cargandoRecursos ? "Cargando camiones..." : camiones.length ? "Seleccionar camión" : "No hay camiones disponibles"}
                </option>

                {camiones.map((camion) => (
                  <option key={camion.id_camion} value={camion.id_camion}>
                    {camion.matricula} - {camion.marca} {camion.modelo}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="viaje-modal__field">
            <label htmlFor="recorrido">Distancia estimada (km)</label>
            <input
              type="number"
              id="recorrido"
              name="recorrido"
              value={form.recorrido}
              readOnly
              placeholder="Se calcula al elegir ambos puntos"
              min="0"
              step="0.1"
            />
          </div>

          <div className="viaje-modal__field">
            <label htmlFor="observaciones">Observaciones</label>
            <textarea
              id="observaciones"
              name="observaciones"
              value={form.observaciones}
              onChange={onChange}
              placeholder="Indicaciones especiales, notas del viaje..."
              rows={3}
              maxLength={200}
            />
          </div>

          {(error || errorRecursos) && <p className="viaje-modal__error">{error || errorRecursos}</p>}

          <div className="viaje-modal__actions">
            <button
              type="button"
              className="viaje-modal__btn viaje-modal__btn--cancelar"
              onClick={onClose}
            >
              Cancelar
            </button>

            <button
              type="submit"
              className="viaje-modal__btn viaje-modal__btn--guardar"
              disabled={guardando || cargandoRuta || cargandoLugarMapa || cargandoRecursos || Boolean(errorRecursos) || !geoapifyConfigurado || !ruta || !choferes.length || !camiones.length}
            >
              {guardando ? "Creando..." : "Crear viaje"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CrearViajeModal;
