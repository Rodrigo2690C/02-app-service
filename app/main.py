"""
Aplicativo de ejemplo para la capacitación — Track DEVELOPER.
Ejercicio: Azure App Service (PaaS).

Es una mini-API REST + una página web simple para gestionar TAREAS (CRUD).
Sirve para enseñar:
  - Cómo se sube código a App Service (sin administrar el servidor).
  - Cómo la app lee la cadena de conexión desde una variable de entorno.
  - Cómo se conecta a una base de datos gestionada (Azure SQL).

Para verla funcionando:
  - Página web:   /
  - Documentación: /docs   (Swagger autogenerado por FastAPI)
  - Healthcheck:  /health
"""
import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from database import Base, engine, get_db
import models
import schemas

# Crea las tablas si no existen (en una app real esto se hace con migraciones).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Tareas — Capacitación Azure",
    description="Aplicativo de ejemplo para el ejercicio de Azure App Service (PaaS).",
    version="1.0.0",
)

BASE_DIR = os.path.dirname(__file__)


@app.get("/health", tags=["sistema"])
def health():
    """Endpoint de salud: App Service y los monitores lo usan para saber si la app vive."""
    return {"status": "ok"}


@app.get("/api/tareas", response_model=list[schemas.TareaRespuesta], tags=["tareas"])
def listar_tareas(db: Session = Depends(get_db)):
    return db.query(models.Tarea).order_by(models.Tarea.id.desc()).all()


@app.post("/api/tareas", response_model=schemas.TareaRespuesta, status_code=201, tags=["tareas"])
def crear_tarea(datos: schemas.TareaCrear, db: Session = Depends(get_db)):
    tarea = models.Tarea(titulo=datos.titulo)
    db.add(tarea)
    db.commit()
    db.refresh(tarea)
    return tarea


@app.get("/api/tareas/{tarea_id}", response_model=schemas.TareaRespuesta, tags=["tareas"])
def obtener_tarea(tarea_id: int, db: Session = Depends(get_db)):
    tarea = db.get(models.Tarea, tarea_id)
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return tarea


@app.put("/api/tareas/{tarea_id}", response_model=schemas.TareaRespuesta, tags=["tareas"])
def actualizar_tarea(tarea_id: int, datos: schemas.TareaActualizar, db: Session = Depends(get_db)):
    tarea = db.get(models.Tarea, tarea_id)
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    if datos.titulo is not None:
        tarea.titulo = datos.titulo
    if datos.completada is not None:
        tarea.completada = datos.completada
    db.commit()
    db.refresh(tarea)
    return tarea


@app.delete("/api/tareas/{tarea_id}", status_code=204, tags=["tareas"])
def eliminar_tarea(tarea_id: int, db: Session = Depends(get_db)):
    tarea = db.get(models.Tarea, tarea_id)
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    db.delete(tarea)
    db.commit()
    return None


# Página web simple (frontend) servida desde /static
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(os.path.join(BASE_DIR, "static", "index.html"))
