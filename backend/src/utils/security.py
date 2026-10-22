from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import HTTPException, status
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de seguridad
SECRET_KEY = os.getenv("SECRET_KEY", "eduforge_super_secret_key_change_in_production_2024")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si la contraseña en texto plano coincide con el hash

    Args:
        plain_password: Contraseña en texto plano
        hashed_password: Contraseña hasheada

    Returns:
        bool: True si coinciden, False si no
    """
    try:
        # Convertir a bytes
        password_bytes = plain_password.encode('utf-8')
        hash_bytes = hashed_password.encode('utf-8')

        # Verificar con bcrypt directamente
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception as e:
        print(f"Error verificando contraseña: {str(e)}")
        return False

def get_password_hash(password: str) -> str:
    """
    Genera el hash de una contraseña

    Args:
        password: Contraseña en texto plano

    Returns:
        str: Hash de la contraseña
    """
    try:
        # Convertir a bytes
        password_bytes = password.encode('utf-8')

        # Generar salt y hashear
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password_bytes, salt)

        # Retornar como string
        return hashed.decode('utf-8')
    except Exception as e:
        print(f"Error generando hash: {str(e)}")
        raise

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Crea un token JWT de acceso

    Args:
        data: Datos a incluir en el token
        expires_delta: Tiempo de expiración opcional

    Returns:
        str: Token JWT
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """
    Decodifica un token JWT

    Args:
        token: Token JWT a decodificar

    Returns:
        dict: Datos del token

    Raises:
        HTTPException: Si el token es inválido
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
