import { hoyOperativo } from "./fechaOperativa.js";

export function validarEdicionViaje(form, viaje, hoy = hoyOperativo()) {
  if (!form.origen.trim() || !form.destino.trim()) return "Origen y destino son obligatorios.";
  const fechaValida = (valor) => /^\d{4}-\d{2}-\d{2}$/.test(valor)
    && Number.isFinite(Date.parse(`${valor}T00:00:00Z`))
    && new Date(`${valor}T00:00:00Z`).toISOString().slice(0, 10) === valor;
  if (!fechaValida(form.fecha_salida) || (form.fecha_llegada && !fechaValida(form.fecha_llegada))) {
    return "Ingresá fechas válidas.";
  }
  const cambiaSalida = form.fecha_salida !== viaje.fecha_salida;
  const cambiaLlegada = (form.fecha_llegada || "") !== (viaje.fecha_llegada || "");
  if (cambiaSalida && viaje.estado === "en curso") return "No se puede cambiar la salida de un viaje en curso.";
  if (cambiaSalida && form.fecha_salida < hoy) return "La nueva fecha de salida debe ser hoy o una fecha futura.";
  if ((cambiaSalida || cambiaLlegada) && form.fecha_llegada && form.fecha_llegada < form.fecha_salida) {
    return "La fecha de llegada no puede ser anterior a la salida.";
  }
  if (form.recorrido === "" || !Number.isFinite(Number(form.recorrido)) || Number(form.recorrido) < 0) {
    return "El recorrido debe ser un número mayor o igual a cero.";
  }
  return "";
}
