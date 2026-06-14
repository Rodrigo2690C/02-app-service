# API de Tareas — Demo Azure App Service

Aplicativo de ejemplo para la capacitación (Track DEVELOPER). Es una mini-API REST
con una página web simple para gestionar tareas (CRUD), construida con **FastAPI** y
preparada para desplegarse en **Azure App Service** conectada a **Azure SQL**.

## Estructura

```
app/
├── main.py            # La API (rutas CRUD) + sirve la página web
├── database.py        # Conexión a BD (lee DATABASE_URL del entorno)
├── models.py          # Tabla 'tareas' (ORM SQLAlchemy)
├── schemas.py         # Validación de datos (Pydantic)
├── static/index.html  # Frontend simple (HTML + JS)
├── requirements.txt   # Dependencias
├── startup.txt        # Comando de inicio para App Service
└── .env.example       # Plantilla de variables de entorno
```

## Correr en local (3 pasos)

```bash
# 1. Crear entorno virtual e instalar dependencias
python -m venv .venv
.venv\Scripts\activate        # En Windows
pip install -r requirements.txt

# 2. Arrancar (sin configurar nada, usa SQLite automáticamente)
uvicorn main:app --reload

# 3. Abrir en el navegador
#    http://localhost:8000        -> página web
#    http://localhost:8000/docs   -> documentación Swagger
```

## Desplegar en Azure

Sigue la guía paso a paso: **`../EJERCICIO_App_Service.md`**

## Idea clave

La cadena de conexión a la base de datos **no está en el código**: se lee de la
variable de entorno `DATABASE_URL`. En local no la defines (usa SQLite); en Azure
la configuras como *App Setting* apuntando a Azure SQL. Mismo código, distinto entorno.
