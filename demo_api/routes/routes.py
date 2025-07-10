from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, update, insert, or_
from sqlalchemy.engine import Result
from database.database import engine, usuarios, usuario_intentos, usuario_tipo, tipos_introvertido
from datetime import datetime



login_router = APIRouter()

class LoginRequest(BaseModel):
    user_or_email: str
    password: str

class UpdatePuntosRequest(BaseModel):
    user_id: int
    puntos: int


@login_router.post("/api/login")
def login(request: LoginRequest):
    user_or_username = request.user_or_email
    password = request.password

    try:
        with engine.connect() as connection:
            trans = connection.begin()
            try:
                # Buscar usuario
                query = select(usuarios).where(
                    or_(
                        usuarios.c.username == user_or_username,
                        usuarios.c.correo == user_or_username
                    )
                )
                result: Result = connection.execute(query)
                user = result.fetchone()

                if not user:
                    raise HTTPException(status_code=404, detail="Usuario o Contraseña Incorrecto")

                user_dict = dict(user._mapping)

                # Verificar si tiene registro de intentos
                intentos_query = select(usuario_intentos).where(
                    usuario_intentos.c.id_usuario == user_dict['id_usuario']
                )
                intentos_result = connection.execute(intentos_query).fetchone()

                # Si no tiene registro, lo creamos
                if not intentos_result:
                    connection.execute(
                        insert(usuario_intentos).values(
                            id_usuario=user_dict['id_usuario'],
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
                        usuario_intentos.c.id_usuario == user_dict['id_usuario']
                    ).values(intentos=nuevos_intentos, estado=nuevo_estado)

                    connection.execute(stmt)
                    trans.commit()
                    raise HTTPException(status_code=401, detail="Usuario o Contraseña Incorrecto")

                # Si login exitoso, reiniciar intentos
                connection.execute(
                    update(usuario_intentos).where(
                        usuario_intentos.c.id_usuario == user_dict['id_usuario']
                    ).values(intentos=0, estado=1)
                )

                #Obtener Informacion del usuario Introvertido
                query =(select(usuario_tipo.c.id_tipointro, tipos_introvertido.c.tipo, tipos_introvertido.c.video)
                .join(tipos_introvertido, usuario_tipo.c.id_tipointro == tipos_introvertido.c.id_tipointro)
                .where(usuario_tipo.c.id_usuario == user_dict['id_usuario'])) 

                result: Result = connection.execute(query)
                intro_list = [dict(row._mapping) for row in result.fetchall()]

                if intro_list:
                    user_dict['id_tipointro'] = ",".join(str(i['id_tipointro']) for i in intro_list)
                    user_dict['tipo_introvertido'] = ",".join(i['tipo'] for i in intro_list)
                    user_dict['video_introvertido'] = ",".join(i['video'] for i in intro_list)
                else:
                    user_dict['id_tipointro'] = None
                    user_dict['tipo_introvertido'] = None
                    user_dict['video_introvertido'] = None



                trans.commit()

                return {
                    "message": "Inicio de sesión exitoso",
                    "user_id": user_dict['id_usuario'],
                    "nombre_completo": user_dict['nombre_completo'],
                    "id_tipo_introvertido": user_dict['id_tipointro'],
                    "tipos_de_introvertido": user_dict['tipo_introvertido'],
                    "video": user_dict['video_introvertido']
                }

            except:
                trans.rollback()
                raise

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"[ERROR] {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")
