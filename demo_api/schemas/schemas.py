from pydantic import BaseModel
from typing import Optional
from datetime import date

# ========================
# Tabla: usuarios
# ========================
class UsuarioBaseSchema(BaseModel):
    id: int
    nombre_completo: str
    username: str
    contraseña: str
    fecha_registro: date
    # puntos no está en esta tabla, se maneja por separado

    class Config:
        orm_mode = True


# ========================
# Tabla: usuario_intentos
# ========================
class UsuarioIntentoSchema(BaseModel):
    id: int
    usuario_id: int
    intentos: int
    estado: bool  # True = libre, False = bloqueado

    class Config:
        orm_mode = True


# ========================
# Tabla: registro_de_puntos
# ========================
class RegistroPuntosSchema(BaseModel):
    id: int
    cantidad_puntos: int
    usuario_id: int
    fecha_registro: date

    class Config:
        orm_mode = True
