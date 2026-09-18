import { useEffect, useState } from "react";
import { searchPlaces } from "../utils/geoapify";

function GeoapifyPlaceField({ id, label, value, selected, onChange, onSelect }) {
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (selected || value.trim().length < 3) return undefined;

    const controller = new AbortController();
    const timer = window.setTimeout(async () => {
      try {
        setLoading(true);
        setError("");
        setSuggestions(await searchPlaces(value.trim(), controller.signal));
      } catch (requestError) {
        if (requestError.name !== "AbortError") {
          setError(requestError.message);
          setSuggestions([]);
        }
      } finally {
        if (!controller.signal.aborted) setLoading(false);
      }
    }, 350);

    return () => {
      window.clearTimeout(timer);
      controller.abort();
    };
  }, [value, selected]);

  const choose = (place) => {
    setSuggestions([]);
    setLoading(false);
    onSelect({ label: place.formatted, lat: place.lat, lon: place.lon });
  };

  return (
    <div className="viaje-modal__field viaje-modal__place-field">
      <label htmlFor={id}>{label}</label>
      <input
        id={id}
        name={id}
        type="text"
        value={value}
        onChange={(event) => {
          setSuggestions([]);
          setLoading(false);
          onChange(event.target.value);
        }}
        placeholder="Buscar dirección o establecimiento"
        autoComplete="off"
        role="combobox"
        aria-expanded={suggestions.length > 0}
        aria-controls={`${id}-opciones`}
        maxLength={255}
        required
      />
      {loading && <span className="viaje-modal__place-status">Buscando...</span>}
      {error && <span className="viaje-modal__place-status viaje-modal__place-status--error">{error}</span>}
      {suggestions.length > 0 && (
        <ul className="viaje-modal__suggestions" id={`${id}-opciones`} role="listbox">
          {suggestions.map((place) => (
            <li key={place.place_id || `${place.lat}-${place.lon}`} role="option" aria-selected="false">
              <button type="button" onClick={() => choose(place)}>{place.formatted}</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default GeoapifyPlaceField;
