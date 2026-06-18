from src.Usuario import Usuario
from src.ReporteFalla import ReporteFalla
from src.Camion import Camion
from src.Chofer import Chofer
from src.Mecanico import Mecanico
from src.OperadorLogistico import OperadorLogistico


class Administrador(Usuario):
    ROLES_VALIDOS = Usuario.ROLES_VALIDOS
    ESTADOS_VALIDOS = Usuario.ESTADOS_VALIDOS

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
        legajo,
        foto_perfil=None,
        usuarios_gestionados=None,
        reportes_falla=None,
        camiones_gestionados=None,
    ):
        super().__init__(
            id_usuario,
            username,
            email,
            password,
            nombre,
            apellido,
            estado,
            rol,
            foto_perfil,
        )

        self.legajo = legajo
        self.usuarios_gestionados = usuarios_gestionados or []
        self.reportes_falla = reportes_falla or []
        self.camiones_gestionados = camiones_gestionados or []

    @classmethod
    def crear_desde_datos(cls, datos):
        # crea un administrador desde un diccionario
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
            legajo=datos.get("legajo"),
            foto_perfil=datos.get("foto_perfil"),
        )

    def agregar_usuario_gestionado(self, usuario):
        # guarda el usuario en la lista del admin
        if usuario is None:
            return False

        self.usuarios_gestionados.append(usuario)
        return True

    def agregar_camion_gestionado(self, camion):
        # guarda el camion en la lista del admin
        if camion is None:
            return False

        self.camiones_gestionados.append(camion)
        return True

    def agregar_reporte_falla(self, reporte):
        # guarda el reporte en la lista del admin
        if reporte is None:
            return False

        self.reportes_falla.append(reporte)
        return True

    @staticmethod
    def rol_valido(rol):
        # valida que el rol exista
        return rol in Administrador.ROLES_VALIDOS

    @staticmethod
    def estado_valido(estado):
        # valida que el estado exista
        return estado in Administrador.ESTADOS_VALIDOS

    def _construir_usuario_por_rol(self, datos, password):
        if datos is None:
            return None

        rol = datos.get("rol")
        estado = datos.get("estado")

        if not self.rol_valido(rol):
            return None

        if not self.estado_valido(estado):
            return None

        if not self.texto_valido(datos.get("username")):
            return None

        if not self.texto_valido(datos.get("email")):
            return None

        if not self.texto_valido(datos.get("nombre")):
            return None

        if not self.texto_valido(datos.get("apellido")):
            return None

        if not self.texto_valido(datos.get("legajo")):
            return None

        if rol == Usuario.ROL_ADMIN:
            datos_admin = dict(datos)
            datos_admin["id_usuario"] = datos.get("id_usuario")
            datos_admin["password"] = password

            return Administrador.crear_desde_datos(datos_admin)

        if rol == Usuario.ROL_CHOFER:
            vencimiento = Chofer.convertir_vencimiento_licencia(
                datos.get("vencimientoLicencia")
            )

            if vencimiento is None:
                return None

            datos_chofer = dict(datos)
            datos_chofer["id_usuario"] = datos.get("id_usuario")
            datos_chofer["password"] = password
            datos_chofer["vencimientoLicencia"] = vencimiento

            return Chofer.crear_desde_datos(datos_chofer)

        if rol == Usuario.ROL_MECANICO:
            if not self.texto_valido(datos.get("especialidad")):
                return None

            datos_mecanico = dict(datos)
            datos_mecanico["id_usuario"] = datos.get("id_usuario")
            datos_mecanico["password"] = password

            return Mecanico.crear_desde_datos(datos_mecanico)

        if rol == Usuario.ROL_OPERADOR:
            if not self.texto_valido(datos.get("sector")):
                return None

            datos_operador = dict(datos)
            datos_operador["id_usuario"] = datos.get("id_usuario")
            datos_operador["password"] = password

            return OperadorLogistico.crear_desde_datos(datos_operador)

        return None

    def crear_usuario(self, datos, password):
        # crea y registra un usuario nuevo
        usuario = self._construir_usuario_por_rol(
            datos,
            password
        )

        if usuario is None:
            return None

        self.agregar_usuario_gestionado(usuario)
        return usuario

    def reconstruir_usuario(self, datos, password):
        # reconstruye un usuario existente sin registrarlo como nuevo
        return self._construir_usuario_por_rol(
            datos,
            password
        )

    def activar_usuario(self, usuario):
        # activa un usuario pendiente o inactivo
        if usuario is None:
            return False

        if usuario.estado not in [
            Usuario.ESTADO_PENDIENTE,
            Usuario.ESTADO_INACTIVO,
        ]:
            return False

        usuario.estado = Usuario.ESTADO_ACTIVO
        self.agregar_usuario_gestionado(usuario)
        return True

    def desactivar_usuario(self, usuario):
        # desactiva un usuario sin eliminarlo
        if usuario is None:
            return False

        if usuario.id_usuario == self.id_usuario:
            return False

        if usuario.estado != Usuario.ESTADO_ACTIVO:
            return False

        usuario.estado = Usuario.ESTADO_INACTIVO
        self.agregar_usuario_gestionado(usuario)
        return True

    def modificar_usuario(
        self,
        usuario,
        username,
        email,
        nombre,
        apellido,
        estado
    ):
        # modifica datos generales de un usuario
        if usuario is None:
            return False

        if not self.texto_valido(username):
            return False

        if not self.texto_valido(email):
            return False

        if not self.texto_valido(nombre):
            return False

        if not self.texto_valido(apellido):
            return False

        if not self.estado_valido(estado):
            return False

        usuario.username = username
        usuario.email = email
        usuario.nombre = nombre
        usuario.apellido = apellido
        usuario.estado = estado

        self.agregar_usuario_gestionado(usuario)
        return True

    def validar_datos_camion(self, datos_camion):
        return Camion.validar_datos_camion(datos_camion)

    def crear_camion(self, datos, id_camion=None):
        # crea un camion desde el administrador
        if datos is None:
            return None

        camion = Camion.crear_desde_datos(
            datos,
            id_camion=id_camion,
        )

        if not self.registrar_camion(camion):
            return None

        return camion

    def registrar_camion(self, camion):
        # registra un camion si sus datos son validos
        if camion is None:
            return False

        if not camion.validar_datos():
            return False

        if not camion.validar_estado():
            return False

        self.agregar_camion_gestionado(camion)
        return True

    def preparar_modificacion_camion(self, datos_camion, id_camion):
        # prepara un camion existente con datos nuevos
        if datos_camion is None:
            return None

        if id_camion is None:
            return None

        camion = Camion.crear_desde_datos(
            datos_camion,
            id_camion=id_camion,
        )

        if camion is None:
            return None

        if not self.modificar_camion(camion):
            return None

        return camion

    def modificar_camion(self, camion):
        if camion is None:
            return False

        if not camion.validar_datos():
            return False

        if not camion.validar_estado():
            return False

        self.agregar_camion_gestionado(camion)
        return True

    def cambiar_estado_camion(self, camion, nuevo_estado):
        # cambia el estado de un camion
        if camion is None:
            return False

        estado_cambiado = camion.cambiar_estado(nuevo_estado)

        if estado_cambiado:
            self.agregar_camion_gestionado(camion)

        return estado_cambiado

    def cambiar_estado_reporte(self, reporte, nuevo_estado):
        # cambia el estado de un reporte
        if reporte is None:
            return False

        if not isinstance(reporte, ReporteFalla):
            return False

        estado_cambiado = reporte.cambiar_estado(nuevo_estado)

        if estado_cambiado:
            self.agregar_reporte_falla(reporte)

        return estado_cambiado

    def to_dict(self):
        datos_usuario = super().to_dict()

        datos_usuario.update(
            {
                "legajo": self.legajo,
            }
        )

        return datos_usuario