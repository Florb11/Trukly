import test from "node:test";
import assert from "node:assert/strict";
import { validarEdicionViaje } from "../src/utils/validarEdicionViaje.js";

const viaje = { origen:"A", destino:"B", fecha_salida:"2026-11-04", fecha_llegada:"", recorrido:10, estado:"aceptado" };
const validar = (cambios, original=viaje) => validarEdicionViaje({ ...original, ...cambios }, original, "2026-11-04");

test("rechaza salida pasada, fecha inexistente y llegada anterior", () => {
  for (const datos of [{fecha_salida:"2026-11-03"}, {fecha_salida:"2026-02-30"}, {fecha_llegada:"2026-11-03"}]) {
    assert.notEqual(validar(datos), "");
  }
});
test("rechaza distancia negativa, no numérica o infinita", () => {
  for (const recorrido of [-1, "abc", "Infinity", "NaN", ""]) assert.notEqual(validar({recorrido}), "");
});
test("acepta fechas coherentes y distancia cero", () => {
  assert.equal(validar({fecha_salida:"2026-11-05", fecha_llegada:"2026-11-06", recorrido:0}), "");
});
test("permite observaciones conservando fechas históricas", () => {
  assert.equal(validar({observaciones:"Nueva nota"}, {...viaje, fecha_salida:"2000-01-01"}), "");
});
test("impide cambiar salida cuando ya está en curso", () => {
  assert.notEqual(validar({fecha_salida:"2026-11-05"}, {...viaje, estado:"en curso"}), "");
});

test("bloquea reasignaciones en curso y permite conservarlas o editar notas", () => {
  const original = {...viaje, estado:"en curso", Chofer_Usuario_idUsuario:91, Camion_id_camion:90};
  assert.notEqual(validar({Chofer_Usuario_idUsuario:92}, original), "");
  assert.notEqual(validar({Camion_id_camion:91}, original), "");
  assert.equal(validar({Chofer_Usuario_idUsuario:"91", Camion_id_camion:"90", observaciones:"Nota"}, original), "");
});
test("permite solicitar reasignacion antes de iniciar", () => {
  const original = {...viaje, Chofer_Usuario_idUsuario:91, Camion_id_camion:90};
  assert.equal(validar({Chofer_Usuario_idUsuario:92}, original), "");
});
