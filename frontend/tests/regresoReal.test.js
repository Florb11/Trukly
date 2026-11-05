import test from "node:test";
import assert from "node:assert/strict";
import { regresoReal } from "../src/utils/regresoReal.js";
import { regresoReal as regresoMobile } from "../../frontend-mobile/src/utils/regresoReal.js";

for (const [nombre, formato] of [["web", regresoReal], ["móvil", regresoMobile]]) {
  test(`${nombre}: separa estimación y control real sin desplazar el reloj`, () => {
    assert.equal(formato({fecha_llegada:"2026-11-12"}), "Sin registro");
    assert.equal(formato({fecha_regreso_real:"2026-11-05T00:02:13.123456"}), "05/11/2026 00:02:13");
    assert.equal(formato({tiempo_viaje:{estado:"confirmado", regreso:"2026-11-04T23:59:00"}}), "04/11/2026 23:59:00");
    assert.equal(formato({tiempo_viaje:{estado:"inconsistente", regreso:"2026-11-04T23:59:00"}}), "Sin registro");
  });
}
