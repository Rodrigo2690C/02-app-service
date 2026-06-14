"""
Configuración de la base de datos.

Lección clave del manual (Sección 2 y 7):
- La cadena de conexión NO se hardcodea: se lee de una variable de entorno.
- En local, si no hay DATABASE_URL, usamos SQLite y la app corre al instante.
- En Azure App Service, defines DATABASE_URL como "App Setting" apuntando a Azure SQL.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Cargar variables desde un archivo .env si existe (solo para desarrollo local)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 1) ¿Hay una cadena de conexión inyectada por el entorno? (lo normal en Azure)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # 2) Fallback para desarrollo local: SQLite, un archivo en disco.
    #    Así la app funciona sin instalar nada antes de la demo.
    DATABASE_URL = "sqlite:///./tareas.db"

# SQLite necesita este parámetro extra; Azure SQL no.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Entrega una sesión de BD por request y la cierra al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
