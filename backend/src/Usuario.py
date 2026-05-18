class Usuario:
    def __init__(self, id_usuario, username, password, nombre, apellido, estado):
        self.id_usuario = id_usuario
        self.username = username
        self.password = password
        self.nombre = nombre
        self.apellido = apellido
        self.estado = estado
        
    def iniciar_sesion(self, password_ingresada, bcrypt):
        return bcrypt.check_password_hash(self.password, password_ingresada)

    def esta_activo(self):
        return self.estado == "activo"

    def cerrar_sesion(self):
        return True
        
