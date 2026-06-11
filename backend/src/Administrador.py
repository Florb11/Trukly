from src.Usuario import Usuario
from src.ReporteFalla import ReporteFalla


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

    def agregar_usuario_gestionado(self, usuario):
        if usuario is None:
            return False

        self.usuarios_gestionados.append(usuario)
        return True

    def agregar_camion_gestionado(self, camion):
        if camion is None:
            return False

        self.camiones_gestionados.append(camion)
        return True

    def agregar_reporte_falla(self, reporte):
        if reporte is None:
            return False

        self.reportes_falla.append(reporte)
        return True

    @staticmethod
    def texto_valido(valor):
        return valor is not None and str(valor).strip() != ""

    @staticmethod
    def rol_valido(rol):
        return rol in Administrador.ROLES_VALIDOS

    @staticmethod
    def estado_valido(estado):
        return estado in Administrador.ESTADOS_VALIDOS

    @staticmethod
    def calcular_porcentaje(parte, total):
        if total <= 0:
            return 0

        return round((parte / total) * 100)

    # activa un usuario si esta pendiente o inactivo
    def activar_usuario(self, usuario):
        if usuario.estado not in [
            Usuario.ESTADO_PENDIENTE,
            Usuario.ESTADO_INACTIVO,
        ]:
            return False

        usuario.estado = Usuario.ESTADO_ACTIVO
        self.agregar_usuario_gestionado(usuario)
        return True

    # desactiva un usuario pasandolo a inactivo
    # no eliminamos usuarios, los desactivamos
    def desactivar_usuario(self, usuario):
        if usuario.id_usuario == self.id_usuario:
            return False

        if usuario.estado != Usuario.ESTADO_ACTIVO:
            return False

        usuario.estado = Usuario.ESTADO_INACTIVO
        self.agregar_usuario_gestionado(usuario)
        return True

    # modifica los datos generales de un usuario
    # no modificamos el rol desde aca
    def modificar_usuario(self, usuario, username, email, nombre, apellido, estado):
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

    # registra un usuario desde el administrador
    def registrar_usuario(self, usuario):
        if usuario is None:
            return False

        if not self.rol_valido(usuario.rol):
            return False

        if not self.estado_valido(usuario.estado):
            return False

        if not self.texto_valido(usuario.username):
            return False

        if not self.texto_valido(usuario.email):
            return False

        if not self.texto_valido(usuario.nombre):
            return False

        if not self.texto_valido(usuario.apellido):
            return False

        self.agregar_usuario_gestionado(usuario)
        return True

    # uso el diccionario del padre y agrego el legajo del admin
    def to_dict(self):
        datos_usuario = super().to_dict()

        datos_usuario.update(
            {
                "legajo": self.legajo,
            }
        )

        return datos_usuario

    # registra un camion desde el administrador
    def registrar_camion(self, camion):
        if camion is None:
            return False

        if not camion.validar_datos():
            return False

        if not camion.validar_estado():
            return False

        self.agregar_camion_gestionado(camion)
        return True

    # modifica los datos de un camion
    def modificar_camion(self, camion):
        if camion is None:
            return False

        if not camion.validar_datos():
            return False

        if not camion.validar_estado():
            return False

        self.agregar_camion_gestionado(camion)
        return True

    # cambia el estado de un camion
    def cambiar_estado_camion(self, camion, nuevo_estado):
        if camion is None:
            return False

        estado_cambiado = camion.cambiar_estado(nuevo_estado)

        if estado_cambiado:
            self.agregar_camion_gestionado(camion)

        return estado_cambiado

    def cambiar_estado_reporte(self, reporte, nuevo_estado):
        if reporte is None:
            return False

        if not isinstance(reporte, ReporteFalla):
            return False

        estado_cambiado = reporte.cambiar_estado(nuevo_estado)

        if estado_cambiado:
            self.agregar_reporte_falla(reporte)

        return estado_cambiado

    def preparar_chofer_pendiente(self, usuario, chofer):
        datos_usuario = usuario.to_dict()

        if chofer:
            datos_usuario["licencia"] = chofer.licencia
            datos_usuario["legajo"] = chofer.legajo
            datos_usuario["vencimientoLicencia"] = str(
                chofer.vencimientoLicencia
            )
        else:
            datos_usuario["licencia"] = "-"

        return datos_usuario

    def armar_resumen_dashboard(
        self,
        usuarios_activos,
        camiones_registrados,
        camiones_disponibles,
        reportes_abiertos,
        reportes_resueltos,
        total_reportes,
        viajes_del_dia,
        viajes_en_curso,
        viajes_finalizados,
        total_viajes,
        actividad_operativa,
        usuarios_pendientes,
    ):
        return {
            "usuarios_activos": usuarios_activos,
            "camiones_registrados": camiones_registrados,
            "camiones_disponibles": camiones_disponibles,
            "reportes_abiertos": reportes_abiertos,
            "reportes_prioridad_alta": 0,
            "viajes_del_dia": viajes_del_dia,
            "viajes_en_curso": viajes_en_curso,
            "estado_general": {
                "flota_disponible": self.calcular_porcentaje(
                    camiones_disponibles,
                    camiones_registrados
                ),
                "reportes_resueltos": self.calcular_porcentaje(
                    reportes_resueltos,
                    total_reportes
                ),
                "viajes_finalizados": self.calcular_porcentaje(
                    viajes_finalizados,
                    total_viajes
                ),
            },
            "actividad_operativa": actividad_operativa,
            "usuarios_pendientes": usuarios_pendientes,
        }

    def armar_resumen_estadisticas(
        self,
        total_viajes,
        viajes_finalizados,
        viajes_cancelados,
        viajes_en_curso,
        total_reportes,
        reportes_activos,
        reportes_resueltos,
    ):
        return {
            "total_viajes": total_viajes,
            "viajes_finalizados": viajes_finalizados,
            "viajes_cancelados": viajes_cancelados,
            "viajes_en_curso": viajes_en_curso,
            "total_reportes": total_reportes,
            "reportes_activos": reportes_activos,
            "reportes_resueltos": reportes_resueltos,
        }

    @staticmethod
    def armar_ranking_viajes(filas):
        return [
            {
                "id_usuario": fila.id_usuario,
                "nombre": fila.nombre,
                "apellido": fila.apellido,
                "total_viajes": fila.total_viajes,
                "viajes_finalizados": int(
                    fila.viajes_finalizados or 0
                ),
                "viajes_cancelados": int(
                    fila.viajes_cancelados or 0
                ),
            }
            for fila in filas
        ]

    @staticmethod
    def armar_ranking_reportes_chofer(filas):
        return [
            {
                "id_usuario": fila.id_usuario,
                "nombre": fila.nombre,
                "apellido": fila.apellido,
                "total_reportes": fila.total_reportes,
                "reportes_resueltos": int(
                    fila.reportes_resueltos or 0
                ),
            }
            for fila in filas
        ]

    @staticmethod
    def armar_ranking_reparaciones_mecanico(filas):
        return [
            {
                "id_usuario": fila.id_usuario,
                "nombre": fila.nombre,
                "apellido": fila.apellido,
                "total_asignados": fila.total_asignados,
                "total_resueltos": int(
                    fila.total_resueltos or 0
                ),
                "en_revision": int(
                    fila.en_revision or 0
                ),
            }
            for fila in filas
        ]

    @staticmethod
    def armar_ranking_reportes_camion(filas):
        return [
            {
                "id_camion": fila.id_camion,
                "matricula": fila.matricula,
                "marca": fila.marca,
                "modelo": fila.modelo,
                "total_reportes": fila.total_reportes,
            }
            for fila in filas
        ]

    @staticmethod
    def convertir_modelos_a_diccionario(modelos):
        return [
            modelo.to_dict()
            for modelo in modelos
        ]

    def armar_estadisticas(
        self,
        resumen,
        choferes_mas_viajes,
        operadores_mas_viajes,
        choferes_mas_reportes,
        mecanicos_mas_reparaciones,
        camiones_mas_reportes,
        ultimos_viajes,
        ultimos_reportes,
    ):
        return {
            "resumen": resumen,
            "choferes_mas_viajes": choferes_mas_viajes,
            "operadores_mas_viajes": operadores_mas_viajes,
            "choferes_mas_reportes": choferes_mas_reportes,
            "mecanicos_mas_reparaciones": mecanicos_mas_reparaciones,
            "camiones_mas_reportes": camiones_mas_reportes,
            "ultimos_viajes": self.convertir_modelos_a_diccionario(
                ultimos_viajes
            ),
            "ultimos_reportes": self.convertir_modelos_a_diccionario(
                ultimos_reportes
            ),
        }