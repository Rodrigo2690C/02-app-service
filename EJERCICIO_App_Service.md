# Ejercicio práctico — Azure App Service (PaaS)

> **Track:** DEVELOPER · **Tema:** Sección 2 del manual (Azure App Service)
> **Duración estimada:** 45–55 min · **Modalidad:** demostración guiada + práctica

---

## 🎯 Objetivo

Que el participante **despliegue una aplicación Python real en Azure App Service**,
la conecte a una **base de datos gestionada (Azure SQL)** y entienda en la práctica
por qué PaaS reemplaza al clásico servidor con IIS.

Al terminar, el participante sabrá:

- Subir código a App Service desde un repositorio de GitHub.
- Configurar la cadena de conexión **sin hardcodearla** (App Settings).
- Crear y conectar una base de datos Azure SQL.
- Usar **deployment slots** (staging → swap a producción sin downtime).

---

## 🧩 El aplicativo

Una mini-API + página web para gestionar **tareas** (lista de pendientes con CRUD).
El código está en la carpeta [`app/`](./app/). Es deliberadamente pequeño para que el
foco esté en **el despliegue y la base de datos**, no en la lógica.

| Ruta | Qué hace |
|------|----------|
| `/` | Página web (agregar/marcar/borrar tareas) |
| `/docs` | Documentación Swagger autogenerada |
| `/health` | Estado de la app (lo usa App Service para saber si vive) |
| `/api/tareas` | API REST (GET, POST, PUT, DELETE) |

**Idea pedagógica clave:** el mismo código corre en local con SQLite y en Azure con
Azure SQL. Lo único que cambia es la variable de entorno `DATABASE_URL`. Eso es PaaS:
tú traes el código, el entorno se inyecta desde fuera.

---

## ✅ Prerrequisitos

- Cuenta de Azure (ver `Manual_Crear_Cuenta_Azure.docx`).
- Cuenta de GitHub.
- Python 3.11+ instalado en local.
- (Opcional) Azure CLI: `az` — útil para los retos avanzados.

---

## Parte A — Probar la app en local (10 min)

> Meta: ver la app funcionando ANTES de subirla, para entender qué vamos a desplegar.

```bash
cd app
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

Abre en el navegador:
- http://localhost:8000 → agrega un par de tareas.
- http://localhost:8000/docs → prueba los endpoints desde Swagger.

> 💡 **Pregunta al grupo:** ¿dónde se están guardando las tareas ahora mismo?
> Respuesta: en un archivo SQLite local (`tareas.db`), porque no definimos `DATABASE_URL`.

---

## Parte B — Subir el código a GitHub (5 min)

```bash
git init
git add .
git commit -m "App de tareas para demo de App Service"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/demo-app-service.git
git push -u origin main
```

> ⚠️ Confirma que el `.env` NO se subió (está en `.gitignore`). Los secretos nunca van al repo.

---

## Parte C — Crear la base de datos Azure SQL (10 min)

En el **Portal de Azure** → *Crear un recurso* → **Azure SQL**:

1. **SQL Database** → *Crear*.
2. Crea un **servidor SQL** nuevo:
   - Nombre del servidor: `sql-capacitacion-<tusiniciales>`
   - Autenticación: usuario y contraseña (anótalos).
3. Base de datos:
   - Nombre: `tareasdb`
   - Capacidad de cómputo: **Básico / Serverless** (lo más barato para la demo).
4. En **Redes** → marca *"Permitir que los servicios de Azure accedan a este servidor"*.
5. Crear y esperar el despliegue.

> 💡 Aquí App Service y Azure SQL son **dos servicios gestionados separados**: Azure
> administra backups, parches y disponibilidad de ambos. Tú solo defines esquema y datos.

Anota la **cadena de conexión** (Portal → tu BD → *Cadenas de conexión* → ADO.NET),
la adaptaremos al formato de SQLAlchemy en la Parte E.

---

## Parte D — Crear el App Service y desplegar (10 min)

Portal de Azure → *Crear un recurso* → **Web App**:

1. **Pila en tiempo de ejecución:** Python 3.11.
2. **Sistema operativo:** Linux.
3. **Plan (App Service Plan):** Basic **B1** (tiene slots; los planes Free no).
4. Crear.
5. En la Web App → **Centro de implementación (Deployment Center)**:
   - Origen: **GitHub** → autoriza → elige tu repo y rama `main`.
   - Azure crea un workflow de GitHub Actions automáticamente (¡esto adelanta CI/CD!).
6. **Comando de inicio** (Configuración → Configuración general):
   ```
   gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app
   ```
   (también está en [`app/startup.txt`](./app/startup.txt))

Espera a que el deploy termine y abre la URL `https://<tu-app>.azurewebsites.net`.

> ⚠️ En la primera carga aún usa SQLite dentro del contenedor (se pierde al reiniciar).
> Lo conectamos a Azure SQL en el siguiente paso.

---

## Parte E — Conectar la app a Azure SQL (10 min)

> Esta es la lección central: **la conexión se inyecta por configuración, no por código.**

En la Web App → **Configuración** → **Variables de entorno / App Settings** → *Nueva*:

- **Nombre:** `DATABASE_URL`
- **Valor:** (reemplaza tus datos)
  ```
  mssql+pyodbc://USUARIO:CONTRASEÑA@sql-capacitacion-xx.database.windows.net:1433/tareasdb?driver=ODBC+Driver+18+for+SQL+Server&Encrypt=yes&TrustServerCertificate=no
  ```

Guarda. La app se reinicia y ahora **lee y escribe en Azure SQL**.

Verifica:
1. Abre la web, agrega una tarea.
2. En el Portal → tu BD → **Editor de consultas** → `SELECT * FROM tareas;`
3. La tarea creada desde la web aparece en la base de datos gestionada. ✅

> 💡 Compara con `app/database.py`: el código solo hace `os.getenv("DATABASE_URL")`.
> Nunca conoció la contraseña: Azure se la entregó como variable de entorno.

---

## Parte F — Deployment Slots: desplegar sin downtime (10 min)

> Demuestra el "swap" que el manual menciona como zero-downtime deploy.

1. Web App → **Ranuras de implementación (Deployment slots)** → *Agregar ranura* → `staging`.
2. Haz un cambio visible en el código (ej: cambia el título `📋 Lista de Tareas`
   por `📋 Lista de Tareas (v2)` en `app/static/index.html`) y haz push.
3. Despliega ese cambio al slot **staging** y ábrelo: `https://<tu-app>-staging.azurewebsites.net`.
4. Valida que se ve bien en staging.
5. **Swap**: botón *Intercambiar* (staging ↔ producción). El cambio pasa a producción
   **al instante y sin caída**. Si algo sale mal, otro swap lo revierte.

---

## ✏️ Retos para el participante

Resuelve al menos **dos**:

1. **Healthcheck en Azure:** configura el *Health check* de App Service apuntando a
   `/health`. ¿Qué pasa si la ruta devuelve error?
2. **Escalar:** sube el plan de B1 a S1 y activa *scale out* a 2 instancias.
   ¿La app sigue funcionando? ¿Por qué la BD no se duplica?
3. **Nuevo campo:** agrega un campo `prioridad` (alta/media/baja) a la tarea
   (modelo + schema + frontend) y vuelve a desplegar vía push.
4. **Seguridad:** mueve la `DATABASE_URL` a **Azure Key Vault** y referénciala desde
   App Settings (Key Vault reference). Conecta con la Sección 6 del manual (Entra ID).
5. **Slot con su propia BD:** haz que el slot `staging` use una base de datos distinta
   configurando un `DATABASE_URL` diferente marcado como *slot setting*.

---

## ⚠️ Errores comunes (recordar del manual)

- Hardcodear la cadena de conexión en el código en vez de usar App Settings.
- Desplegar directo a producción sin pasar por el slot de staging.
- Abrir el firewall de Azure SQL a todo internet (`0.0.0.0`) por comodidad.
- Usar un plan Free esperando slots o autoescalado (no los tiene).
- Olvidar el *startup command*: sin él, App Service no sabe cómo arrancar FastAPI.

---

## 📌 Cierre del ejercicio

Repasa en voz alta: *"Subimos código, Azure instaló dependencias, corrió la app,
le inyectamos la BD por configuración y desplegamos sin downtime — sin tocar un solo
servidor ni IIS."* Eso es **App Service (PaaS)**.
