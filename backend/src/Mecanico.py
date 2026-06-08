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
    def puede_resolver_reporte(self, reporte):
        return (
            reporte.Mecanico_Usuario_idUsuario == self.id_usuario
            and reporte.estado != "resuelto"
        )

    # cambia el estado del reporte a resuelto si corresponde
    def resolver_reporte(self, reporte):
        if not self.puede_resolver_reporte(reporte):
            return False

        reporte.estado = "resuelto"
        return True

    def to_dict(self):
        datos = super().to_dict()

        datos["legajo"] = self.legajo
        datos["especialidad"] = self.especialidad

        return datos