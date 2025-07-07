from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, update, insert
from sqlalchemy.engine import Result
from database.database import engine, usuarios, usuario_intentos, registro_de_puntos
from datetime import datetime


login_router = APIRouter()

class LoginRequest(BaseModel):
    user_or_username: str
    password: str

class UpdatePuntosRequest(BaseModel):
    user_id: int
    puntos: int


@login_router.post("/api/login")
def login(request: LoginRequest):
    user_or_username = request.user_or_username
    password = request.password

    try:
        with engine.connect() as connection:
            trans = connection.begin()
            try:
                # Buscar usuario
                query = select(usuarios).where(
                    usuarios.c.username == user_or_username
                )
                result: Result = connection.execute(query)
                user = result.fetchone()

                if not user:
                    raise HTTPException(status_code=404, detail="Usuario o Contraseña Incorrecto")

                user_dict = dict(user._mapping)

                # Verificar si tiene registro de intentos
                intentos_query = select(usuario_intentos).where(
                    usuario_intentos.c.usuario_id == user_dict['id']
                )
                intentos_result = connection.execute(intentos_query).fetchone()

                # Si no tiene registro, lo creamos
                if not intentos_result:
                    connection.execute(
                        insert(usuario_intentos).values(
                            usuario_id=user_dict['id'],
                            intentos=0,
                            estado=1
                        )
                    )
                    intentos_result = connection.execute(intentos_query).fetchone()

                intentos_data = intentos_result._mapping
                intentos_actuales = intentos_data['intentos']
                estado_usuario = intentos_data['estado']

                # Verificar si está bloqueado
                if estado_usuario == 0:
                    raise HTTPException(status_code=403, detail="Usuario bloqueado por múltiples intentos fallidos")

                # Validar contraseña (compara texto plano)
                if password.strip() != user_dict['contraseña'].strip():
                    nuevos_intentos = min(3, intentos_actuales + 1)
                    nuevo_estado = 0 if nuevos_intentos >= 3 else 1

                    stmt = update(usuario_intentos).where(
                        usuario_intentos.c.usuario_id == user_dict['id']
                    ).values(intentos=nuevos_intentos, estado=nuevo_estado)

                    connection.execute(stmt)
                    trans.commit()

                    print(f"[LOGIN FALLIDO] Usuario ID {user_dict['id']} | Intentos: {nuevos_intentos} | Estado: {nuevo_estado}")
                    raise HTTPException(status_code=401, detail="Usuario o Contraseña Incorrecto")

                # Si login exitoso, reiniciar intentos
                connection.execute(
                    update(usuario_intentos).where(
                        usuario_intentos.c.usuario_id == user_dict['id']
                    ).values(intentos=0, estado=1)
                )

                # Obtener puntos
                puntos_query = select(registro_de_puntos.c.cantidad_puntos).where(
                    registro_de_puntos.c.usuario_id == user_dict['id']
                )
                puntos_result = connection.execute(puntos_query).fetchone()
                puntos = puntos_result[0] if puntos_result else 0

                trans.commit()

                return {
                    "message": "Inicio de sesión exitoso",
                    "user_id": user_dict['id'],
                    "nombre_completo": user_dict['nombre_completo'],
                    "puntos": puntos
                }

            except:
                trans.rollback()
                raise

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"[ERROR] {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@login_router.put("/api/puntos")
def actualizar_puntos(request: UpdatePuntosRequest):
    try:
        now = datetime.now()
        with engine.begin() as connection:
            # Verificar si ya existe un registro de puntos para el usuario
            query = select(registro_de_puntos).where(
                registro_de_puntos.c.usuario_id == request.user_id
            )
            result = connection.execute(query).fetchone()

            if result:
                # Actualizar puntos y fecha
                stmt = update(registro_de_puntos).where(
                    registro_de_puntos.c.usuario_id == request.user_id
                ).values(
                    cantidad_puntos=request.puntos,
                    fecha_registro=now
                )
                print(f"Actualizando puntos para usuario {request.user_id}")
            else:
                # Insertar nuevo registro
                stmt = insert(registro_de_puntos).values(
                    usuario_id=request.user_id,
                    cantidad_puntos=request.puntos,
                    fecha_registro=now
                )
                print(f"Insertando puntos para usuario {request.user_id}")

            connection.execute(stmt)
            return {"message": "Puntos actualizados correctamente"}
    except Exception as e:
        print(f"Error actualizando puntos: {e}")
        raise HTTPException(status_code=500, detail="Error al actualizar puntos")
