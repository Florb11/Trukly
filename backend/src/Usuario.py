class Usuario:
    def __init__(self, id_usuario, username, password, nombre, apellido, estado, rol):
        self.id_usuario = id_usuario
        self.username = username
        self.password = password
        self.nombre = nombre
        self.apellido = apellido
        self.estado = estado
        self.rol = rol

    # verifica si la contrasena ingresada coincide con la contrasena guardada
    def verificar_password(self, password_ingresada, bcrypt):
        return bcrypt.check_password_hash(self.password, password_ingresada)

   
    def esta_activo(self):
        return self.estado == "activo"

    
    def to_dict(self):
        return {
            "id_usuario": self.id_usuario,
            "username": self.username,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "estado": self.estado,
            "rol": self.rol,
        }

    def cerrar_sesion(self):
        return True
