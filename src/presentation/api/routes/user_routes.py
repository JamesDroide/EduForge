# src/presentation/api/routes/user_routes.py
"""
Rutas de la API para gestión de usuarios (Clean Architecture)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from shared.utils.get_db import get_db
from application.use_cases.users.get_users_use_case import GetUsersUseCase, GetUserByIdUseCase
from application.use_cases.users.create_user_use_case import CreateUserUseCase
from application.use_cases.users.update_user_use_case import UpdateUserUseCase, DeleteUserUseCase
from domain.exceptions.domain_exceptions import UserNotFoundException, UserAlreadyExistsException
from presentation.schemas.user_schema import UserResponse, UserCreateRequest, UserUpdateRequest

router = APIRouter(prefix="/users-v2", tags=["Usuarios v2 (Clean)"])


@router.get("/", response_model=List[UserResponse])
async def get_all_users(db: Session = Depends(get_db)):
    """Obtiene todos los usuarios"""
    try:
        use_case = GetUsersUseCase(db)
        users = use_case.execute()
        return [user.to_dict() for user in users]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Obtiene un usuario por ID"""
    try:
        use_case = GetUserByIdUseCase(db)
        user = use_case.execute(user_id)
        return user.to_dict()
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(request: UserCreateRequest, db: Session = Depends(get_db)):
    """Crea un nuevo usuario (admin)"""
    try:
        use_case = CreateUserUseCase(db)
        user = use_case.execute(
            username=request.username,
            email=request.email,
            password=request.password,
            rol=request.rol,
            nombre=request.nombre,
            apellido=request.apellido
        )
        return user.to_dict()
    except UserAlreadyExistsException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    request: UserUpdateRequest,
    db: Session = Depends(get_db)
):
    """Actualiza un usuario"""
    try:
        use_case = UpdateUserUseCase(db)
        user = use_case.execute(
            user_id=user_id,
            username=request.username,
            email=request.email,
            password=request.password,
            rol=request.rol,
            nombre=request.nombre,
            apellido=request.apellido
        )
        return user.to_dict()
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Elimina un usuario"""
    try:
        use_case = DeleteUserUseCase(db)
        use_case.execute(user_id)
        return {"success": True, "message": "Usuario eliminado exitosamente"}
    except UserNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

