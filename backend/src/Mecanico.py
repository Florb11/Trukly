from src.Usuario import Usuario
from src.ReporteFalla import ReporteFalla


class Mecanico(Usuario):
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
        especialidad,
        foto_perfil=None,
        reportes_asignados=None,
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
        self.especialidad = especialidad
        self.reportes_asignados = reportes_asignados or []

    # verifica si el reporte pertenece al mecanico
    def puede_ver_reporte(self, reporte):
        if reporte is None:
            return False

        return reporte.pertenece_a_mecanico(self)

    def asignar_reporte(self, reporte):
        if reporte is None:
            return False

        if not reporte.asignar_mecanico(self):
            return False

        self.reportes_asignados.append(reporte)
        return True

    # verifica si el mecanico puede marcar como resuelto el reporte
    def puede_resolver_reporte(self, reporte, nota_reparacion):
        if reporte is None:
            return False

        return reporte.puede_ser_resuelto_por(
            self,
            nota_reparacion
        )

    # cambia el estado del reporte a resuelto y guarda la nota de reparacion
    def resolver_reporte(self, reporte, nota_reparacion):
        if reporte is None:
            return False

        return reporte.resolver_por_mecanico(
            self,
            nota_reparacion
        )

    def puede_liberar_camion(self, camion, reportes_activos):
        if camion is None:
            return False

        return camion.puede_liberarse_de_mantenimiento(reportes_activos)

    def liberar_camion_si_corresponde(self, camion, reportes_activos):
        if not self.puede_liberar_camion(camion, reportes_activos):
            return False

        return camion.liberar_si_no_tiene_reportes_activos(reportes_activos)

    def to_dict(self):
        datos = super().to_dict()

        datos["legajo"] = self.legajo
        datos["especialidad"] = self.especialidad

        return datos
    
    def puede_consultar_mantenimiento(self):
        return self.estado == Usuario.ESTADO_ACTIVO
    
    
    def separar_reportes_mantenimiento(self, reportes):
        reportes_pendientes = []
        reparaciones_realizadas = []

        for reporte in reportes:
            if reporte.estado == ReporteFalla.ESTADO_RESUELTO:
                reparaciones_realizadas.append(reporte)
            else:
                reportes_pendientes.append(reporte)

        return reportes_pendientes, reparaciones_realizadas