from flask import g, jsonify, request

from db_instance import db
from models.usuario_model import UsuarioModel
from services.firebase_service import FirebaseAuthService, FirebaseConfigError
from src.Usuario import Usuario
from utils.app_logger import get_app_logger
from utils.auth_decorators import usuario_required


logger = get_app_logger()


class ErrorAcceso(ValueError):
    def __init__(self, mensaje, codigo=409):
        super().__init__(mensaje)
        self.codigo = codigo


def usuario_bloqueado():
    usuario = (UsuarioModel.query.filter_by(id_usuario=g.usuario_actual.id_usuario)
               .populate_existing().with_for_update().one_or_none())
    if not usuario or usuario.estado != Usuario.ESTADO_ACTIVO:
        raise ErrorAcceso("La sesión no corresponde a un usuario activo.", 401)
    return usuario


def cuenta_firebase(usuario):
    if not usuario.firebase_uid:
        raise ErrorAcceso("Volvé a iniciar sesión para configurar tus métodos de acceso.")
    cuenta = FirebaseAuthService.obtener_usuario_por_uid(usuario.firebase_uid)
    if cuenta.disabled:
        raise ErrorAcceso("El acceso de esta cuenta está desactivado.", 403)
    return cuenta


def proveedores(cuenta):
    return {proveedor.provider_id: proveedor for proveedor in cuenta.provider_data}


def metodos_acceso(usuario, cuenta):
    disponibles = proveedores(cuenta)
    return {
        "google_vinculado": bool(usuario.google_autorizado),
        "google_en_firebase": "google.com" in disponibles,
        "tiene_password": "password" in disponibles,
    }


def confirmar(usuario, token, proveedor):
    if not usuario.firebase_uid or not isinstance(token, str) or not token:
        raise ErrorAcceso("Confirmá tu identidad antes de continuar.", 403)
    try:
        FirebaseAuthService.confirmar_identidad(usuario.firebase_uid, token, proveedor)
    except FirebaseConfigError:
        raise
    except Exception as error:
        raise ErrorAcceso("La confirmación de identidad no corresponde a esta cuenta o venció.", 403) from error


def comprobar_correo_acceso(usuario, cuenta):
    if not usuario.email or (cuenta.email or "").casefold() != usuario.email.casefold():
        raise ErrorAcceso("El correo de acceso requiere revisión. Contactá al administrador.")


def configurar_password(usuario, datos):
    if not usuario.google_autorizado:
        raise ErrorAcceso("Esta opción está disponible para cuentas con Google vinculado.", 403)

    nueva = datos.get("password_nueva")
    if not isinstance(nueva, str) or nueva != datos.get("confirmar_password"):
        raise ErrorAcceso("Las contraseñas nuevas no coinciden.", 400)
    valida, mensaje = Usuario.validar_password_registro(nueva)
    if not valida:
        raise ErrorAcceso(mensaje, 400)

    confirmar(usuario, datos.get("firebaseToken"), "google.com")
    cuenta = cuenta_firebase(usuario)
    comprobar_correo_acceso(usuario, cuenta)
    disponibles = proveedores(cuenta)
    if "google.com" not in disponibles or not cuenta.email_verified:
        raise ErrorAcceso("Confirmá tu cuenta de Google y el correo de acceso.", 403)
    if "password" in disponibles:
        raise ErrorAcceso("Ya tenés una contraseña configurada. Confirmala para desvincular Google.")

    FirebaseAuthService.cambiar_password(usuario.firebase_uid, nueva)
    return "Contraseña configurada. Ya podés confirmarla para desvincular Google."


def vincular_google(usuario, datos):
    confirmar(usuario, datos.get("firebaseTokenPassword"), "password")
    confirmar(usuario, datos.get("firebaseTokenGoogle"), "google.com")
    cuenta = cuenta_firebase(usuario)
    comprobar_correo_acceso(usuario, cuenta)
    disponibles = proveedores(cuenta)
    google = disponibles.get("google.com")
    if ("password" not in disponibles or not google or not cuenta.email_verified
            or (google.email or "").casefold() != usuario.email.casefold()):
        raise ErrorAcceso("Elegí la cuenta de Google que usa el mismo correo que tu perfil.", 403)

    usuario.google_autorizado = True
    db.session.commit()
    return "Google vinculado a tu cuenta."


def desvincular_google(usuario, datos):
    confirmar(usuario, datos.get("firebaseToken"), "password")
    cuenta = cuenta_firebase(usuario)
    comprobar_correo_acceso(usuario, cuenta)
    if "password" not in proveedores(cuenta):
        raise ErrorAcceso("Configurá y confirmá una contraseña antes de desvincular Google.")

    uid = usuario.firebase_uid
    if usuario.google_autorizado is not False:
        # Guardar el permiso primero evita habilitar el ingreso por Google si falla la desvinculación.
        usuario.google_autorizado = False
        db.session.commit()
        usuario = usuario_bloqueado()
        if usuario.firebase_uid != uid or usuario.google_autorizado:
            raise ErrorAcceso("Los métodos de acceso cambiaron. Volvé a abrir Perfil.")

    if "google.com" in proveedores(cuenta):
        try:
            FirebaseAuthService.desvincular_google(uid)
        except Exception as error:
            logger.exception("No se pudo completar la desvinculación de Google")
            raise ErrorAcceso("El acceso con Google quedó deshabilitado en Trukly. Volvé a intentar la desvinculación.", 503) from error

    return "Google desvinculado. Podés ingresar con tu correo y contraseña."


class AccesoPerfilController:
    @staticmethod
    @usuario_required
    def obtener():
        try:
            usuario = g.usuario_actual
            return jsonify({"acceso": metodos_acceso(usuario, cuenta_firebase(usuario))}), 200
        except ErrorAcceso as error:
            return jsonify({"mensaje": str(error)}), error.codigo
        except Exception:
            logger.exception("No se pudieron consultar los métodos de acceso")
            return jsonify({"mensaje": "No se pudieron consultar los métodos de acceso. Intentá nuevamente."}), 503

    @staticmethod
    @usuario_required
    def crear_password():
        return AccesoPerfilController._actualizar(configurar_password)

    @staticmethod
    @usuario_required
    def google():
        operacion = vincular_google if request.method == "POST" else desvincular_google
        return AccesoPerfilController._actualizar(operacion)

    @staticmethod
    def _actualizar(operacion):
        datos = request.get_json(silent=True)
        if not isinstance(datos, dict):
            return jsonify({"mensaje": "Los datos de acceso no son válidos."}), 400
        try:
            usuario = usuario_bloqueado()
            mensaje = operacion(usuario, datos)
            # El cliente vuelve a consultar los métodos para mostrar el estado confirmado.
            return jsonify({"mensaje": mensaje}), 200
        except ErrorAcceso as error:
            db.session.rollback()
            return jsonify({"mensaje": str(error)}), error.codigo
        except Exception:
            db.session.rollback()
            logger.exception("No se pudo actualizar el método de acceso")
            return jsonify({"mensaje": "No se pudo actualizar el acceso. Intentá nuevamente."}), 503
