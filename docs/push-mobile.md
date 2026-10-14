# Notificaciones push mobile

## Despliegue

1. Ejecutar `backend/database/migrations/2026_10_14_push_dispositivo.sql` sobre la base de datos antes de habilitar push.
2. Desplegar el backend en Railway. Reutiliza las credenciales Firebase Admin del login; deben corresponder al mismo proyecto que la mobile y permitir Firebase Cloud Messaging.
3. En Firebase: Configuracion del proyecto > Cloud Messaging > Web Push certificates, generar o copiar la clave publica VAPID.
4. Agregar `VITE_FIREBASE_VAPID_KEY` en Vercel y volver a desplegar la mobile. No agregar una clave privada ni credenciales Firebase Admin al frontend.
5. Entrar desde el APK > Notificaciones > Activar notificaciones y aceptar el permiso. Si Android bloquea avisos, revisar permisos de Trukly y Chrome.

## Prueba

- Chofer: crear una falla; el operador suscrito recibe el aviso.
- Operador: asignar una falla; el mecanico suscrito recibe el aviso.
- Mecanico: resolver una falla; el chofer suscrito recibe el aviso.
- Abrir el aviso debe llevar a Notificaciones. La bandeja conserva los avisos aunque falle el push.
- Desactivar avisos o cerrar sesion elimina la suscripcion Firebase del dispositivo.

El envio se realiza despues de confirmar la transaccion. Es un envio de mejor esfuerzo: no hay cola persistente de reintentos. Una falla de Firebase no revierte una reparacion o asignacion guardada. Los tokens invalidos se eliminan al enviar.

No se garantiza entrega si Android fuerza la detencion de Chrome o de la app. La clave publica y la migracion son necesarias para probar la entrega real.
