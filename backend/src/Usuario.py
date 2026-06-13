import os
import uuid

from utils.domain_helpers import texto_valido


class Usuario:
    ROL_ADMIN = "admin"
    ROL_CHOFER = "chofer"
    ROL_MECANICO = "mecanico"
    ROL_OPERADOR = "operador"

    ESTADO_PENDIENTE = "pendiente"
    ESTADO_ACTIVO = "activo"
    ESTADO_INACTIVO = "inactivo"

    ROLES_VALIDOS = [
        ROL_ADMIN,
        ROL_CHOFER,
        ROL_MECANICO,
        ROL_OPERADOR,
    ]

    ESTADOS_VALIDOS = [
        ESTADO_PENDIENTE,
        ESTADO_ACTIVO,
        ESTADO_INACTIVO,
    ]

    EXTENSIONES_FOTO_PERMITIDAS = {
        "png",
        "jpg",
        "jpeg",
        "webp",
    }

    TAMANIO_MAXIMO_FOTO_BYTES = 3 * 1024 * 1024

    def __init__(
        self,
        id_usuario,
        username,
        email,
        password,
        nombre,
        apellido,
        estado,
        rol,
        foto_perfil=None
    ):
        self.id_usuario = id_usuario
        self.username = username
        self.password = password
        self.email = email
        self.nombre = nombre
        self.apellido = apellido
        self.estado = estado
        self.rol = rol
        self.foto_perfil = foto_perfil

    @classmethod
    def crear_desde_datos(cls, datos):
        # crea un usuario desde un diccionario
        if datos is None:
            return None

        return cls(
            id_usuario=datos.get("id_usuario"),
            username=datos.get("username"),
            email=datos.get("email"),
            password=datos.get("password"),
            nombre=datos.get("nombre"),
            apellido=datos.get("apellido"),
            estado=datos.get("estado"),
            rol=datos.get("rol"),
            foto_perfil=datos.get("foto_perfil"),
        )

    def verificar_password(self, password_ingresada, bcrypt):
        # verifica si la contrasena ingresada coincide
        if not self.password:
            return False

        if not password_ingresada:
            return False

        return bcrypt.check_password_hash(
            self.password,
            password_ingresada
        )

    def esta_activo(self):
        # indica si el usuario puede iniciar sesion
        return self.estado == self.ESTADO_ACTIVO

    def modificar_datos_personales(self, nombre, apellido, email):
        # modifica datos personales del usuario
        if not self.texto_valido(nombre):
            return False, "El nombre es obligatorio"

        if not self.texto_valido(apellido):
            return False, "El apellido es obligatorio"

        if not self.texto_valido(email):
            return False, "El email es obligatorio"

        self.nombre = nombre.strip()
        self.apellido = apellido.strip()
        self.email = email.strip()

        return True, None

    def puede_cambiar_password(
        self,
        password_actual,
        password_nueva,
        confirmar_password,
        bcrypt
    ):
        # valida si puede cambiar la contrasena
        if not password_actual:
            return False, "La contrasena actual es obligatoria"

        if not self.verificar_password(password_actual, bcrypt):
            return False, "La contrasena actual es incorrecta"

        if not password_nueva:
            return False, "La contrasena nueva es obligatoria"

        if password_nueva != confirmar_password:
            return False, "Las contrasenas nuevas no coinciden"

        password_valida, mensaje_error = (
            Usuario.validar_password_registro(password_nueva)
        )

        if not password_valida:
            return False, mensaje_error

        if self.verificar_password(password_nueva, bcrypt):
            return False, "La contrasena nueva debe ser diferente a la actual"

        return True, None

    def cerrar_sesion(self):
        # representa el cierre de sesion a nivel dominio
        return True

    def to_dict(self):
        # convierte el usuario a diccionario
        return {
            "id_usuario": self.id_usuario,
            "username": self.username,
            "email": self.email,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "estado": self.estado,
            "rol": self.rol,
            "foto_perfil": self.foto_perfil,
        }

    @staticmethod
    def texto_valido(valor):
        # valida texto no vacio
        return texto_valido(valor)

    @staticmethod
    def rol_valido(rol):
        # valida que el rol exista
        return rol in Usuario.ROLES_VALIDOS

    @staticmethod
    def estado_valido(estado):
        # valida que el estado exista
        return estado in Usuario.ESTADOS_VALIDOS

    @staticmethod
    def obtener_extension_foto(nombre_archivo):
        # obtiene la extension de una imagen
        if not nombre_archivo:
            return None

        if "." not in nombre_archivo:
            return None

        return nombre_archivo.rsplit(".", 1)[1].lower()

    @staticmethod
    def validar_foto_perfil(nombre_archivo, tamanio):
        # valida formato y tamanio de foto
        if not nombre_archivo:
            return False, "No se selecciono ninguna imagen"

        extension = Usuario.obtener_extension_foto(nombre_archivo)

        if extension not in Usuario.EXTENSIONES_FOTO_PERMITIDAS:
            return False, "Formato de imagen no permitido"

        if tamanio > Usuario.TAMANIO_MAXIMO_FOTO_BYTES:
            return False, "La imagen no puede superar los 3 MB"

        return True, None

    @staticmethod
    def generar_nombre_foto_perfil(nombre_archivo):
        # genera un nombre unico para la foto
        extension = Usuario.obtener_extension_foto(nombre_archivo)

        if extension is None:
            return None

        return f"{uuid.uuid4().hex}.{extension}"

    @staticmethod
    def obtener_nombre_archivo_foto(ruta_foto):
        # obtiene el nombre del archivo desde una ruta
        if not ruta_foto:
            return None

        return os.path.basename(ruta_foto)

    @staticmethod
    def validar_password_registro(password):
        # valida la contrasena al registrar usuario
        if not password:
            return False, "La contrasena es obligatoria"

        if len(password) < 8:
            return False, "La contrasena debe tener al menos 8 caracteres"

        tiene_letra = any(
            caracter.isalpha()
            for caracter in password
        )

        tiene_numero = any(
            caracter.isdigit()
            for caracter in password
        )

        if not tiene_letra or not tiene_numero:
            return False, (
                "La contrasena debe contener al menos una letra y un numero"
            )

        return True, None
    