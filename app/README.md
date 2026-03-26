# Example application

A web application to monitor.

## Containers

| Container       | Image         | Port  | Role                     |
|-----------------|---------------|-------|--------------------------|
| `todo-frontend` | nginx:alpine  | 8080  | HTML/JS app              |
| `todo-backend`  | python:3.12   | 8000  | FastAPI REST API         |
| `todo-db`       | postgres:16   | 5432  | PostgreSQL database      |

## Run the app

```bash
docker compose up --build
```

- App →      http://localhost:8080
- Health →   http://localhost:8000/health
- Stats →    http://localhost:8000/stats

## API Endpoints

| Method | Path            | Description              |
|--------|-----------------|--------------------------|
| GET    | /health         | Liveness check           |
| GET    | /stats          | Todo counts by status    |
| GET    | /todos          | List todos (filterable)  |
| POST   | /todos          | Create a todo            |
| GET    | /todos/{id}     | Get a specific todo      |
| PATCH  | /todos/{id}     | Update a todo            |
| DELETE | /todos/{id}     | Delete a todo            |

### Filter todos

```
GET /todos?completed=false          # pending only
GET /todos?priority=high            # high priority only
```

## What to monitor

This app is set up for monitoring practice:

- **Health endpoint** at `/health` — ideal for liveness/readiness probes
- **Stats endpoint** at `/stats` — todo counts you can track over time
- **PostgreSQL** — query counts, connection pool, table sizes
- **3 named containers** with Docker healthchecks configured
- Realistic CRUD traffic: GET, POST, PATCH, DELETE
