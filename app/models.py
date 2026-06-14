"""
Modelo de datos (ORM con SQLAlchemy).
Una sola tabla 'tareas' para mantener el ejercicio simple.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from database import Base


class Tarea(Base):
    __tablename__ = "tareas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), nullable=False)
    completada = Column(Boolean, default=False, nullable=False)
    creada_en = Column(DateTime(timezone=True), server_default=func.now())
