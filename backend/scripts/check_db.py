#!/usr/bin/env python3
"""
Script de diagnóstico para verificar la base de datos en Railway
Ejecutar: python scripts/check_db.py
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from sqlalchemy import text, inspect
from config import DATABASE_URL, engine

print("DIAGNOSTICO DE BASE DE DATOS - RAILWAY")

safe_url = DATABASE_URL.split('@')[0].split(':')[0] + ':****@' + DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL
print(f"\n1. DATABASE_URL: {safe_url}")

print("\n2. Verificando conexion...")
try:
    with engine.connect() as conn:
        db_name = conn.execute(text("SELECT current_database()")).scalar()
        user_name = conn.execute(text("SELECT current_user")).scalar()
        host = conn.execute(text("SELECT inet_server_addr()")).scalar()
        port = conn.execute(text("SELECT inet_server_port()")).scalar()

        print(f"  Conectado a: {db_name}")
        print(f"  Usuario: {user_name}")
        print(f"  Host: {host}")
        print(f"  Puerto: {port}")
except Exception as e:
    print(f"  Error: {e}")
    sys.exit(1)

print("\n3. Tablas en la base de datos:")
try:
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    if tables:
        for table in tables:
            print(f"  - {table}")
    else:
        print("  No hay tablas")
except Exception as e:
    print(f"  Error: {e}")

print("\n4. Verificando tabla 'usuarios':")
if 'usuarios' in tables:
    print("  Tabla existe")

    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM usuarios")).scalar()
        print(f"  Total de usuarios: {count}")

        if count > 0:
            result = conn.execute(text("SELECT id, username, email, rol FROM usuarios ORDER BY id"))
            print("\n  Usuarios encontrados:")
            for row in result:
                print(f"  - ID: {row[0]}, Username: {row[1]}, Email: {row[2]}, Rol: {row[3]}")
        else:
            print("  La tabla esta VACIA")
else:
    print("  La tabla NO existe")

print("\n5. Verificando otras tablas:")
important_tables = ['upload_history', 'resultados_prediccion', 'student_data']
for table in important_tables:
    if table in tables:
        with engine.connect() as conn:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"  - {table}: {count} registros")
    else:
        print(f"  - {table}: NO EXISTE")

print("\n6. Variables de entorno:")
env_vars = ['DATABASE_URL', 'SECRET_KEY', 'SUPERADMIN_USERNAME', 'ADMIN_ACCESS_CODE']
for var in env_vars:
    value = os.getenv(var)
    if value:
        if 'URL' in var or 'KEY' in var or 'PASSWORD' in var:
            print(f"  {var}: ****** (configurada)")
        else:
            print(f"  {var}: {value}")
    else:
        print(f"  {var}: NO CONFIGURADA")

print("\nFIN DEL DIAGNOSTICO")
