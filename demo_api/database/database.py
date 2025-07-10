import os
from sqlalchemy import create_engine, MetaData, Table

# Configuración de la conexión a la base de datos
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://yonielvegas:veronica@127.0.0.1:3308/luyeri"
)

# Crear el motor de la base de datos
engine = create_engine(DATABASE_URL, echo=True)  # Cambiar a False en producción

# Metadata y tablas
metadata = MetaData()

# Cargar las tablas
usuarios = Table('usuarios', metadata, autoload_with=engine)
usuario_intentos = Table('usuario_intentos', metadata, autoload_with=engine)
tipos_introvertido = Table('tipos_introvertido', metadata, autoload_with=engine)
usuario_tipo = Table('usuario_tipo', metadata, autoload_with=engine)
