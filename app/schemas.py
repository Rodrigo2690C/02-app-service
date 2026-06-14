"""
Esquemas Pydantic: definen la forma de los datos que entran y salen de la API.
FastAPI los usa para validar automáticamente y generar la documentación Swagger.
"""
from datetime import datetime
from pydantic import BaseModel


class TareaCrear(BaseModel):
    titulo: str


class TareaActualizar(BaseModel):
    titulo: str | None = None
    completada: bool | None = None


class TareaRespuesta(BaseModel):
    id: int
    titulo: str
    completada: bool
    creada_en: datetime | None = None

    class Config:
        from_attributes = True
