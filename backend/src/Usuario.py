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
        "webp"
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

    # verifica si la contrasena ingresada coincide con la contrasena guardada
    def verificar_password(self, password_ingresada, bcrypt):
        return bcrypt.check_password_hash(
            self.password,
            password_ingresada
        )

    # verifica si la cuenta del usuario esta activa
    def esta_activo(self):
        return self.estado == self.ESTADO_ACTIVO

    # modifica los datos personales del usuario
    def modificar_datos_personales(self, nombre, apellido, email):
        if not nombre or nombre.strip() == "":
            return False, "El nombre es obligatorio"

        if not apellido or apellido.strip() == "":
            return False, "El apellido es obligatorio"

        if not email or email.strip() == "":
            return False, "El email es obligatorio"

        self.nombre = nombre.strip()
        self.apellido = apellido.strip()
        self.email = email.strip()

        return True, None

    # valida los datos necesarios para cambiar la contrasena
    def puede_cambiar_password(
        self,
        password_actual,
        password_nueva,
        confirmar_password,
        bcrypt
    ):
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

    # devuelve los datos publicos del usuario
    def to_dict(self):
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

    def cerrar_sesion(self):
        return True

    @staticmethod
    def texto_valido(valor):
        return texto_valido(valor)

    @staticmethod
    def obtener_extension_foto(nombre_archivo):
        if not nombre_archivo or "." not in nombre_archivo:
            return None

        return nombre_archivo.rsplit(".", 1)[1].lower()

    @staticmethod
    def validar_foto_perfil(nombre_archivo, tamanio):
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
        extension = Usuario.obtener_extension_foto(nombre_archivo)

        return f"{uuid.uuid4().hex}.{extension}"

    @staticmethod
    def obtener_nombre_archivo_foto(ruta_foto):
        if not ruta_foto:
            return None

        return os.path.basename(ruta_foto)

    # Usamos staticmethod porque la validacion pertenece a la clase
    # pero no necesita que exista un objeto de la clase creado
    # Antes de crear el objeto, validamos si los datos sirven para construirlo
    @staticmethod
    def validar_password_registro(password):
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
    