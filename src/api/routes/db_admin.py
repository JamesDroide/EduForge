"""
Router para administración de base de datos desde la web
Permite ejecutar consultas SQL de solo lectura de forma segura
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import text, inspect
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import sys
import os

# Agregar el directorio src al path para las importaciones
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from config import engine, SessionLocal
from utils.dependencies import get_current_user
from models.user import Usuario

router = APIRouter(prefix="/db-admin", tags=["Administración de Base de Datos"])


class QueryRequest(BaseModel):
    query: str
    limit: Optional[int] = 100


class QueryResponse(BaseModel):
    columns: List[str]
    rows: List[Dict[str, Any]]
    row_count: int


@router.get("/tables", response_model=List[str])
async def list_tables(current_user: Usuario = Depends(get_current_user)):
    """
    Lista todas las tablas disponibles en la base de datos
    Requiere autenticación
    """
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        return sorted(tables)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar tablas: {str(e)}")


@router.get("/table/{table_name}/schema")
async def get_table_schema(table_name: str, current_user: Usuario = Depends(get_current_user)):
    """
    Obtiene el esquema de una tabla específica (columnas y tipos de datos)
    """
    try:
        inspector = inspect(engine)

        # Verificar que la tabla existe
        tables = inspector.get_table_names()
        if table_name not in tables:
            raise HTTPException(status_code=404, detail=f"Tabla '{table_name}' no encontrada")

        columns = inspector.get_columns(table_name)
        return {
            "table_name": table_name,
            "columns": [
                {
                    "name": col["name"],
                    "type": str(col["type"]),
                    "nullable": col["nullable"],
                    "default": str(col["default"]) if col["default"] else None
                }
                for col in columns
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener esquema: {str(e)}")


@router.get("/table/{table_name}/data")
async def get_table_data(
    table_name: str,
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0, ge=0),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene los datos de una tabla con paginación
    """
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        if table_name not in tables:
            raise HTTPException(status_code=404, detail=f"Tabla '{table_name}' no encontrada")

        with engine.connect() as connection:
            # Contar total de registros
            count_query = text(f"SELECT COUNT(*) FROM {table_name}")
            total_count = connection.execute(count_query).scalar()

            # Obtener datos con paginación
            query = text(f"SELECT * FROM {table_name} LIMIT :limit OFFSET :offset")
            result = connection.execute(query, {"limit": limit, "offset": offset})

            columns = list(result.keys())
            rows = [dict(zip(columns, row)) for row in result]

            return {
                "table_name": table_name,
                "columns": columns,
                "rows": rows,
                "total_count": total_count,
                "returned_count": len(rows),
                "limit": limit,
                "offset": offset
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener datos: {str(e)}")


@router.post("/query", response_model=QueryResponse)
async def execute_query(
    query_request: QueryRequest,
    current_user: Usuario = Depends(get_current_user)
):
    """
    Ejecuta una consulta SQL de solo lectura (SELECT)
    IMPORTANTE: Solo permite consultas SELECT por seguridad
    """
    query = query_request.query.strip().upper()

    # Validar que solo sea una consulta SELECT
    if not query.startswith("SELECT"):
        raise HTTPException(
            status_code=400,
            detail="Solo se permiten consultas SELECT por seguridad"
        )

    # Validar que no contenga comandos peligrosos
    dangerous_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "TRUNCATE", "GRANT", "REVOKE"]
    if any(keyword in query for keyword in dangerous_keywords):
        raise HTTPException(
            status_code=400,
            detail="La consulta contiene comandos no permitidos"
        )

    try:
        with engine.connect() as connection:
            # Agregar LIMIT si no existe
            original_query = query_request.query.strip()
            if "LIMIT" not in query:
                original_query = f"{original_query} LIMIT {query_request.limit}"

            result = connection.execute(text(original_query))

            columns = list(result.keys())
            rows = [dict(zip(columns, row)) for row in result]

            return QueryResponse(
                columns=columns,
                rows=rows,
                row_count=len(rows)
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al ejecutar consulta: {str(e)}")


@router.get("/stats")
async def get_database_stats(current_user: Usuario = Depends(get_current_user)):
    """
    Obtiene estadísticas generales de la base de datos
    """
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        stats = {}
        with engine.connect() as connection:
            for table in tables:
                try:
                    count_query = text(f"SELECT COUNT(*) FROM {table}")
                    count = connection.execute(count_query).scalar()
                    stats[table] = count
                except:
                    stats[table] = "Error al contar"

        return {
            "total_tables": len(tables),
            "tables": tables,
            "row_counts": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener estadísticas: {str(e)}")


@router.get("/connection-info")
async def get_connection_info(current_user: Usuario = Depends(get_current_user)):
    """
    Obtiene información sobre la conexión a la base de datos
    """
    try:
        with engine.connect() as connection:
            # Obtener versión de PostgreSQL
            version_query = text("SELECT version()")
            version = connection.execute(version_query).scalar()

            # Obtener nombre de la base de datos actual
            db_query = text("SELECT current_database()")
            db_name = connection.execute(db_query).scalar()

            # Obtener usuario actual
            user_query = text("SELECT current_user")
            db_user = connection.execute(user_query).scalar()

            return {
                "database": db_name,
                "user": db_user,
                "version": version,
                "status": "connected"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener información: {str(e)}")
