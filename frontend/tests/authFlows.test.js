import test from "node:test";
import assert from "node:assert/strict";
import { completarRegistro, iniciarSesionConRespaldo } from "../src/utils/authFlows.js";

const cuenta = { getIdToken: async (renovar) => { assert.equal(renovar, true); return "token"; } };
const ok = { respuesta: { ok: true }, data: { mensaje: "Solicitud guardada" } };
const errorConCodigo = (code) => Object.assign(new Error(code), { code });

test("registro confirma éxito solo después de Firebase y Trukly", async () => {
  const pasos = [];
  const resultado = await completarRegistro({
    crearCuenta: async () => { pasos.push("firebase"); return cuenta; },
    enviarRegistro: async (token) => { assert.equal(token, "token"); pasos.push("trukly"); return ok; },
  });
  assert.equal(resultado, ok.data);
  assert.deepEqual(pasos, ["firebase", "trukly"]);
});

test("fallo de red después de crear Firebase permite reintentar autenticando la misma cuenta", async () => {
  let creada = false, solicitudes = 0, autenticaciones = 0;
  const opciones = {
    crearCuenta: async () => {
      if (creada) throw errorConCodigo("auth/email-already-in-use");
      creada = true; return cuenta;
    },
    iniciarSesion: async () => { autenticaciones++; return cuenta; },
    enviarRegistro: async () => {
      if (++solicitudes === 1) throw new TypeError("Sin conexión");
      return ok;
    },
  };
  await assert.rejects(completarRegistro(opciones), /Sin conexión/);
  assert.equal(creada, true);
  assert.equal(await completarRegistro(opciones), ok.data);
  assert.equal(autenticaciones, 1);
});

test("respuesta perdida tras guardar Trukly se recupera sin crear otra cuenta", async () => {
  let guardada = false, inserciones = 0;
  const opciones = {
    crearCuenta: async () => { throw errorConCodigo("auth/email-already-in-use"); },
    iniciarSesion: async () => cuenta,
    enviarRegistro: async () => {
      if (!guardada) { guardada = true; inserciones++; throw new TypeError("Respuesta perdida"); }
      return { respuesta: { ok: true }, data: { registro_existente: true } };
    },
  };
  await assert.rejects(completarRegistro(opciones));
  assert.equal((await completarRegistro(opciones)).registro_existente, true);
  assert.equal(inserciones, 1);
});

test("correo existente no permite registrar sin conocer su contraseña", async () => {
  let envios = 0;
  await assert.rejects(completarRegistro({
    crearCuenta: async () => { throw errorConCodigo("auth/email-already-in-use"); },
    iniciarSesion: async () => { throw errorConCodigo("auth/invalid-credential"); },
    enviarRegistro: async () => { envios++; },
  }), /auth\/invalid-credential/);
  assert.equal(envios, 0);
});

test("Google renueva el token antes de registrar y conserva el error del backend", async () => {
  await assert.rejects(completarRegistro({
    obtenerCuentaGoogle: async () => cuenta,
    enviarRegistro: async () => ({ respuesta: { ok: false }, data: { mensaje: "Nombre de usuario ocupado" } }),
  }), /Nombre de usuario ocupado/);
});

for (const [status, mensaje] of [[403, "Pendiente de aprobación"], [404, "Completá tu registro"], [503, "Servicio no disponible"]]) {
  test(`login conserva el rechazo ${status} y no llama al acceso local`, async () => {
    let respaldo = 0;
    await assert.rejects(iniciarSesionConRespaldo({
      autenticarFirebase: async () => "token",
      loginFirebase: async () => { throw Object.assign(new Error(mensaje), { status }); },
      loginLocal: async () => { respaldo++; },
    }), new RegExp(mensaje));
    assert.equal(respaldo, 0);
  });
}

test("login conserva error de red después de autenticar Firebase", async () => {
  await assert.rejects(iniciarSesionConRespaldo({
    autenticarFirebase: async () => "token",
    loginFirebase: async () => { throw new TypeError("Sin conexión"); },
    loginLocal: async () => assert.fail("No debe ocultar el fallo de red"),
  }), /Sin conexión/);
});

test("login permite el respaldo para migrar con token y credencial local", async () => {
  assert.equal(await iniciarSesionConRespaldo({
    autenticarFirebase: async () => "token",
    loginFirebase: async () => { throw { status: 409, codigo: "migracion_pendiente" }; },
    loginLocal: async (token) => { assert.equal(token, "token"); return "migrado"; },
  }), "migrado");
});

test("cuenta local todavía puede migrar cuando Firebase no la conoce", async () => {
  assert.equal(await iniciarSesionConRespaldo({
    autenticarFirebase: async () => { throw errorConCodigo("auth/invalid-credential"); },
    loginFirebase: async () => assert.fail("No hay token"),
    loginLocal: async (token) => { assert.equal(token, null); return "migrado"; },
  }), "migrado");
});
