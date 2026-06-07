class Usuario:
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

    # verifica si la contrasena ingresada coincide con la contrasena guardada
    def verificar_password(self, password_ingresada, bcrypt):
        return bcrypt.check_password_hash(
            self.password,
            password_ingresada
        )

    # verifica si la cuenta del usuario esta activa
    def esta_activo(self):
        return self.estado == "activo"

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
            return False, "La contraseña actual es obligatoria"

        if not self.verificar_password(password_actual, bcrypt):
            return False, "La contraseña actual es incorrecta"

        if not password_nueva:
            return False, "La contraseña nueva es obligatoria"

        if password_nueva != confirmar_password:
            return False, "Las contraseñas nuevas no coinciden"

        password_valida, mensaje_error = (
            Usuario.validar_password_registro(password_nueva)
        )

        if not password_valida:
            return False, mensaje_error

        if self.verificar_password(password_nueva, bcrypt):
            return False, "La contraseña nueva debe ser diferente a la actual"

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

    # Usamos staticmethod porque la validacion pertenece a la clase
    # pero no necesita que exista un objeto de la clase creado
    # Antes de crear el objeto, validamos si los datos sirven para construirlo
    @staticmethod
    def validar_password_registro(password):
        if not password:
            return False, "La contraseña es obligatoria"

        if len(password) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres"

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
                "La contraseña debe contener al menos una letra y un número"
            )

        return True, None
    