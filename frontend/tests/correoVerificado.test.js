import test from "node:test";
import assert from "node:assert/strict";
import { enviarCambioCorreo } from "../src/utils/correoVerificado.js";

const base = { nuevo:" Nuevo@Example.invalid ", actual:"anterior@example.invalid", uid:"propio" };

test("confirma identidad y disponibilidad antes de enviar el enlace", async () => {
  const pasos = [];
  const cuenta = { uid:"propio", email:base.actual };
  const email = await enviarCambioCorreo({ ...base,
    autenticar: async () => { pasos.push("identidad"); return cuenta; },
    comprobar: async () => { pasos.push("disponibilidad"); },
    enviar: async (_, nuevo) => { pasos.push("enlace"); assert.equal(nuevo,"nuevo@example.invalid"); },
  });
  assert.deepEqual(pasos,["identidad","disponibilidad","enlace"]);
  assert.equal(cuenta.email,base.actual);
  assert.equal(email,"nuevo@example.invalid");
});
test("cuenta Google o contraseña de otro usuario no autoriza el cambio", async () => {
  await assert.rejects(enviarCambioCorreo({ ...base,
    autenticar: async () => ({uid:"ajeno"}),
    comprobar: async () => assert.fail("No debe continuar"), enviar: async () => assert.fail("No debe enviar"),
  }), /no corresponde/);
});
test("no envía verificación si el correo está ocupado en Trukly", async () => {
  await assert.rejects(enviarCambioCorreo({ ...base,
    autenticar: async () => ({uid:"propio"}),
    comprobar: async () => { throw new Error("Correo ocupado"); },
    enviar: async () => assert.fail("No debe enviar"),
  }), /Correo ocupado/);
});
test("no confirma envío si Firebase falla y se puede reintentar", async () => {
  let fallar = true;
  const opciones = { ...base, autenticar: async () => ({uid:"propio"}), comprobar: async () => {},
    enviar: async () => { if (fallar) throw new Error("Sin conexión"); } };
  await assert.rejects(enviarCambioCorreo(opciones), /Sin conexión/);
  fallar = false;
  assert.equal(await enviarCambioCorreo(opciones),"nuevo@example.invalid");
});
test("correo inválido o igual al actual se rechaza antes de autenticar", async () => {
  for (const nuevo of ["incorrecto",base.actual,"a".repeat(151)+"@example.invalid"]) {
    await assert.rejects(enviarCambioCorreo({ ...base, nuevo,
      autenticar: async () => assert.fail("No debe autenticar"),
    }), /válido y diferente/);
  }
});
