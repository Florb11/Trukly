from datetime import datetime

from src.Usuario import Usuario


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

    # verifica si el reporte pertenece al mecanico
    def puede_ver_reporte(self, reporte):
        return reporte.Mecanico_Usuario_idUsuario == self.id_usuario

    # verifica si el mecanico puede marcar como resuelto el reporte
    def puede_resolver_reporte(self, reporte, nota_reparacion):
        return (
            reporte.Mecanico_Usuario_idUsuario == self.id_usuario
            and reporte.estado != "resuelto"
            and nota_reparacion is not None
            and nota_reparacion.strip() != ""
        )

    # cambia el estado del reporte a resuelto y guarda la nota de reparacion
    def resolver_reporte(self, reporte, nota_reparacion):
        if not self.puede_resolver_reporte(reporte, nota_reparacion):
            return False

        reporte.estado = "resuelto"
        reporte.nota_reparacion = nota_reparacion
        reporte.fecha_resolucion = datetime.now()

        return True

    def to_dict(self):
        datos = super().to_dict()

        datos["legajo"] = self.legajo
        datos["especialidad"] = self.especialidad

        return datos
    
    def puede_consultar_mantenimiento(self):
     return self.estado == "activo"
    
    
    def separar_reportes_mantenimiento(self, reportes):
     reportes_pendientes = []
     reparaciones_realizadas = []
     for reporte in reportes:
        if reporte.estado == "resuelto":
            reparaciones_realizadas.append(reporte)
        else:
            reportes_pendientes.append(reporte)
            return reportes_pendientes, reparaciones_realizadas