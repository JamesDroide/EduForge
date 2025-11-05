# src/presentation/api/routes/auth_routes.py
"""
Rutas de la API para autenticación (Clean Architecture)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Dict

from shared.utils.get_db import get_db
from application.use_cases.auth.register_use_case import RegisterUseCase
from domain.exceptions.domain_exceptions import UserAlreadyExistsException, UserNotFoundException
from presentation.schemas.user_schema import UserResponse, UserCreateRequest
from presentation.schemas.auth_schema import LoginRequest, AuthResponse
from shared.utils.security import verify_password, create_access_token
from infrastructure.persistence.sqlalchemy.repositories.user_repository import UserRepository

router = APIRouter(prefix="/auth-v2", tags=["Autenticación v2 (Clean)"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: UserCreateRequest, db: Session = Depends(get_db)):
    """Registra un nuevo usuario"""
    try:
        use_case = RegisterUseCase(db)
        user_data = use_case.execute(
            username=request.username,
            email=request.email,
            password=request.password,
            rol=request.rol or "docente",
            nombre=request.nombre,
            apellido=request.apellido
        )
        return user_data
    except UserAlreadyExistsException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)) -> Dict:
    """Inicia sesión y retorna un token de acceso"""
    try:
        repository = UserRepository(db)

        # Buscar usuario
        user = repository.find_by_username(request.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas"
            )

        # Verificar contraseña
        if not verify_password(request.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas"
            )

        # Crear token
        access_token = create_access_token(data={"sub": user.username})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login/form")
async def login_form(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login usando OAuth2PasswordRequestForm (para documentación de FastAPI)"""
    # Crear un LoginRequest desde los datos del formulario
    request = LoginRequest(username=form_data.username, password=form_data.password)
    return await login(request=request, db=db)


@router.put("/update-profile")
async def update_profile(nombre: str, apellido: str, db: Session = Depends(get_db)):
    """Actualiza el perfil del usuario (nombre y apellido)"""
    # TODO: Implementar con use case cuando se agregue autenticación completa
    raise HTTPException(
        status_code=501,
        detail="Funcionalidad en desarrollo - Usar get_current_user para obtener usuario autenticado"
    )


@router.post("/change-password")
async def change_password(old_password: str, new_password: str, db: Session = Depends(get_db)):
    """Cambia la contraseña del usuario actual"""
    # TODO: Implementar con use case cuando se agregue autenticación completa
    raise HTTPException(
        status_code=501,
        detail="Funcionalidad en desarrollo - Usar get_current_user para obtener usuario autenticado"
    )


@router.get("/me")
async def get_current_user_info(db: Session = Depends(get_db)):
    """Obtiene la información del usuario actual"""
    # TODO: Implementar con use case cuando se agregue autenticación completa
    raise HTTPException(
        status_code=501,
        detail="Funcionalidad en desarrollo - Usar get_current_user para obtener usuario autenticado"
    )


@router.post("/logout")
async def logout():
    """Cierra sesión (el frontend debe eliminar el token)"""
    return {"message": "Sesión cerrada exitosamente"}
