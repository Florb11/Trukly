from flask_sqlalchemy import SQLAlchemy

#Lo hicimos siguiendo la idea del ejemplo de clase: 
# usamos una metaclase que guarda las instancias 
# y evita que se creen varias instancias de la base de datos 
# Despues toda la app usa esa misma instancia de SQLAlchemy
class DatabaseManager(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class Database(metaclass=DatabaseManager):
    def __init__(self):
        if not hasattr(self, "db"):
            self.db = SQLAlchemy()

    def init_app(self, app):
        self.db.init_app(app)


database = Database()
db = database.db