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
    
    @staticmethod
    def validar_password_registro(password):
        if not password:
            return False, "La contraseña es obligatoria"
        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres"
        
        tiene_letra = any(caracter.isalpha() for caracter in password)
        tiene_numero = any(caracter.isdigit() for caracter in password)
        
        if not tiene_letra or not tiene_numero:
            return False, "La contraseña debe contener al menos una letra y un número"
        
        return True, None
    
    