from pydantic import BaseModel
from typing import Optional
from datetime import date

# ========================
# Tabla: usuarios
# ========================
class UsuarioBaseSchema(BaseModel):
    id_usuario: int
    nombre_completo: str
    correo: str
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
# Tabla: tipos_introvertido
# ========================
class TiposIntrovertidoSchema(BaseModel):
    id_tipointro: int
    tipo: str
    video: str

    class Config:
        orm_mode = True


# ========================
# Tabla: usuario_tipo
# ========================
class UsuarioTipoSchema(BaseModel):
    id: int
    id_usuario: int
    id_tipointro: int

    class Config:
        orm_mode = True
