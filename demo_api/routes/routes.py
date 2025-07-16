from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, constr, Field
from sqlalchemy import select, update, insert, or_
from sqlalchemy.engine import Result
from database.database import engine, usuarios, usuario_intentos, usuario_tipo, tipos_introvertido
from datetime import datetime, timedelta
from typing import List
from jose import jwt
from google.oauth2 import id_token
from google.auth.transport import requests 

import bcrypt

def hashear_contraseña(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verificar_contraseña(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

SECRET_KEY = "brochazo"
ALGORITHM = "HS256"

def crear_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=7))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


router = APIRouter()


class LoginRequest(BaseModel):
    user_or_email: constr(strip_whitespace=True, min_length=3)
    password: constr(min_length=6)

class RegisterRequest(BaseModel):
    nombre_completo: constr(strip_whitespace=True, min_length=1)
    correo: EmailStr
    user: constr(strip_whitespace=True, min_length=3, max_length=30)
    password: constr(min_length=6)
    tipo_introvert: List[int]

class GoogleToken(BaseModel):
    id_token: str


class GoogleRegister(BaseModel):
    nombre_completo: str
    correo: str
    user: str
    password: str
    tipo_introvert: List[int]



@router.post("/api/login")
def login(request: LoginRequest):
    user_or_username = request.user_or_email
    print(f"[LOGIN] Recibido: {request.user_or_email}")
    password = request.password
    

    try:
        with engine.connect() as connection:
            trans = connection.begin()
            try:
                # Buscar usuario
                query = select(usuarios).where(
                        (usuarios.c.username == user_or_username) | (usuarios.c.correo == user_or_username)
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
                if not verificar_contraseña(password.strip(), user_dict['contraseña'].strip()):
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

                token = crear_token({"sub": str(user_dict['id_usuario'])})

                trans.commit()

                return {
                    "message": "Inicio de sesión exitoso",
                    "token": token,
                    "tipo_token": "bearer",
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

#Registro

@router.post("/api/registrar")
def registrar(request: RegisterRequest):
    nombre = request.nombre_completo
    email = request.correo
    user = request.user
    password = request.password
    tipintro = request.tipo_introvert

    try:
        with engine.connect() as connection:
            # Transacción segura
            with connection.begin():

                # Verificar si ya existe el usuario o correo
                check_query = select(usuarios).where(
                    (usuarios.c.username == user) | (usuarios.c.correo == email)
                )
                result: Result = connection.execute(check_query)
                existing_user = result.fetchone()

                if existing_user:
                    raise HTTPException(
                        status_code=409, detail="Usuario o correo ya registrado"
                    )

                # Insertar usuario y obtener el ID insertado
                insert_query = (
                    insert(usuarios)
                    .values(
                        nombre_completo=nombre,
                        correo=email,
                        username=user,
                        contraseña=hashear_contraseña(password)
                    )
                    .returning(usuarios)
                )
                result: Result = connection.execute(insert_query)
                user = result.fetchone()

                user_dict = dict(user._mapping)

                # Insertar los tipos de introvertido asociados
                for tipo_id in tipintro:
                    connection.execute(
                        insert(usuario_tipo).values(
                            id_usuario=user_dict['id_usuario'],
                            id_tipointro=tipo_id
                        )
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

                token = crear_token({"sub": str(user_dict['id_usuario'])})

                return {
                    "message": "Usuario registrado exitosamente",
                    "token": token,
                    "tipo_token": "bearer",
                    "user_id": user_dict['id_usuario'],
                    "nombre_completo": user_dict['nombre_completo'],
                    "id_tipo_introvertido": user_dict['id_tipointro'],
                    "tipos_de_introvertido": user_dict['tipo_introvertido'],
                    "video": user_dict['video_introvertido']
                }

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"[ERROR] {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


# --- INICIO DE SESIÓN CON GOOGLE ---
@router.post("/api/login_google")
def login_google(request: GoogleToken):
    try:
        
        user = request.id_token

        with engine.connect() as connection:
            # Buscar usuario
            result = connection.execute(
                select(usuarios).where(usuarios.c.username == user)
            ).fetchone()

            if not result:
                raise HTTPException(status_code=404, detail="Usuario no registrado")

            user_dict = dict(result._mapping)

            # Obtener tipos de introversión
            query = (select(usuario_tipo.c.id_tipointro, tipos_introvertido.c.tipo, tipos_introvertido.c.video)
                     .join(tipos_introvertido, usuario_tipo.c.id_tipointro == tipos_introvertido.c.id_tipointro)
                     .where(usuario_tipo.c.id_usuario == user_dict['id_usuario']))

            intro_list = [dict(row._mapping) for row in connection.execute(query).fetchall()]

            if intro_list:
                user_dict['id_tipointro'] = ",".join(str(i['id_tipointro']) for i in intro_list)
                user_dict['tipo_introvertido'] = ",".join(i['tipo'] for i in intro_list)
                user_dict['video_introvertido'] = ",".join(i['video'] for i in intro_list)
            else:
                user_dict['id_tipointro'] = None
                user_dict['tipo_introvertido'] = None
                user_dict['video_introvertido'] = None

            token = crear_token({"sub": str(user_dict['id_usuario'])})

            return {
                "message": "Inicio de sesión con Google exitoso",
                "token": token,
                "tipo_token": "bearer",
                "user_id": user_dict['id_usuario'],
                "nombre_completo": user_dict['nombre_completo'],
                "id_tipo_introvertido": user_dict['id_tipointro'],
                "tipos_de_introvertido": user_dict['tipo_introvertido'],
                "video": user_dict['video_introvertido']
            }

    except ValueError:
        raise HTTPException(status_code=401, detail="Token de Google inválido")


# --- REGISTRO CON GOOGLE ---
from fastapi import HTTPException

@router.post("/api/registrar_google")
def registrar_google(request: GoogleRegister):
    try:
        with engine.connect() as connection:
            with connection.begin():
                # Validar si el usuario o correo ya están registrados
                existing = connection.execute(
                    select(usuarios).where(
                        (usuarios.c.username == request.user) | (usuarios.c.correo == request.correo)
                    )
                ).fetchone()

                if existing:
                    raise HTTPException(status_code=409, detail="Usuario ya registrado")

                # Hashear contraseña si viene (puede ser null)
                password_hash = hashear_contraseña(request.password) if request.password else hashear_contraseña("google_default")

                insert_query = (
                    insert(usuarios)
                    .values(
                        nombre_completo=request.nombre_completo,
                        correo=request.correo,
                        username=request.user,
                        contraseña=password_hash
                    )
                    .returning(usuarios)
                )
                new_user = connection.execute(insert_query).fetchone()
                user_dict = dict(new_user._mapping)

                for tipo_id in request.tipo_introvert:
                    connection.execute(
                        insert(usuario_tipo).values(
                            id_usuario=user_dict['id_usuario'],
                            id_tipointro=tipo_id
                        )
                    )

                query = (
                    select(usuario_tipo.c.id_tipointro, tipos_introvertido.c.tipo, tipos_introvertido.c.video)
                    .join(tipos_introvertido, usuario_tipo.c.id_tipointro == tipos_introvertido.c.id_tipointro)
                    .where(usuario_tipo.c.id_usuario == user_dict['id_usuario'])
                )

                intro_list = [dict(row._mapping) for row in connection.execute(query).fetchall()]

                if intro_list:
                    user_dict['id_tipointro'] = ",".join(str(i['id_tipointro']) for i in intro_list)
                    user_dict['tipo_introvertido'] = ",".join(i['tipo'] for i in intro_list)
                    user_dict['video_introvertido'] = ",".join(i['video'] for i in intro_list)
                else:
                    user_dict['id_tipointro'] = None
                    user_dict['tipo_introvertido'] = None
                    user_dict['video_introvertido'] = None

                token = crear_token({"sub": str(user_dict['id_usuario'])})

                return {
                    "message": "Registro con Google exitoso",
                    "token": token,
                    "tipo_token": "bearer",
                    "user_id": user_dict['id_usuario'],
                    "nombre_completo": user_dict['nombre_completo'],
                    "id_tipo_introvertido": user_dict['id_tipointro'],
                    "tipos_de_introvertido": user_dict['tipo_introvertido'],
                    "video": user_dict['video_introvertido']
                }

    except HTTPException as he:
        # Relanzar para que FastAPI devuelva el status code correcto
        raise he
    except Exception as e:
        print("ERROR:", e)
        raise HTTPException(status_code=500, detail="Error interno en el servidor")
