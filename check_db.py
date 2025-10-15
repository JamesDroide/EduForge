#!/usr/bin/env python3
"""
Script de diagnóstico para verificar la base de datos en Railway
Ejecutar: python check_db.py
"""
import os
import sys

# Agregar src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine, text, inspect
from config import DATABASE_URL, engine

print("=" * 80)
print("DIAGNÓSTICO DE BASE DE DATOS - RAILWAY")
print("=" * 80)

# 1. Mostrar DATABASE_URL (sin password)
safe_url = DATABASE_URL.split('@')[0].split(':')[0] + ':****@' + DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL
print(f"\n1. DATABASE_URL: {safe_url}")

# 2. Verificar conexión
print("\n2. Verificando conexión...")
try:
    with engine.connect() as conn:
        # Info de conexión
        db_name = conn.execute(text("SELECT current_database()")).scalar()
        user_name = conn.execute(text("SELECT current_user")).scalar()
        host = conn.execute(text("SELECT inet_server_addr()")).scalar()
        port = conn.execute(text("SELECT inet_server_port()")).scalar()

        print(f"   ✅ Conectado a: {db_name}")
        print(f"   Usuario: {user_name}")
        print(f"   Host: {host}")
        print(f"   Puerto: {port}")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# 3. Listar todas las tablas
print("\n3. Tablas en la base de datos:")
try:
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    if tables:
        for table in tables:
            print(f"   - {table}")
    else:
        print("   ⚠️  No hay tablas")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 4. Verificar tabla usuarios
print("\n4. Verificando tabla 'usuarios':")
if 'usuarios' in tables:
    print("   ✅ Tabla existe")

    # Contar usuarios
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM usuarios")).scalar()
        print(f"   Total de usuarios: {count}")

        if count > 0:
            # Listar usuarios
            result = conn.execute(text("SELECT id, username, email, rol FROM usuarios ORDER BY id"))
            print("\n   Usuarios encontrados:")
            for row in result:
                print(f"   - ID: {row[0]}, Username: {row[1]}, Email: {row[2]}, Rol: {row[3]}")
        else:
            print("   ⚠️  La tabla está VACÍA")
else:
    print("   ❌ La tabla NO existe")

# 5. Verificar otras tablas importantes
print("\n5. Verificando otras tablas:")
important_tables = ['upload_history', 'resultados_prediccion', 'student_data']
for table in important_tables:
    if table in tables:
        with engine.connect() as conn:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"   - {table}: {count} registros")
    else:
        print(f"   - {table}: NO EXISTE")

# 6. Variables de entorno críticas
print("\n6. Variables de entorno:")
env_vars = ['DATABASE_URL', 'SECRET_KEY', 'SUPERADMIN_USERNAME', 'ADMIN_ACCESS_CODE']
for var in env_vars:
    value = os.getenv(var)
    if value:
        if 'URL' in var or 'KEY' in var or 'PASSWORD' in var:
            print(f"   {var}: ****** (configurada)")
        else:
            print(f"   {var}: {value}")
    else:
        print(f"   {var}: ⚠️  NO CONFIGURADA")

print("\n" + "=" * 80)
print("FIN DEL DIAGNÓSTICO")
print("=" * 80)

