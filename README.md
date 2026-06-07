# Docker Multi-Container Todo App — Practice Project

## Architecture

```
Browser
  │
  ▼
[Nginx :8080]  ──static HTML──▶  served directly
  │
  │  /api/*  (reverse proxy)
  ▼
[Flask Backend :5000]
  │
  │  SQLAlchemy ORM
  ▼
[PostgreSQL :5432]
```

Three containers. Two custom Docker networks. One named volume.

---

## Prerequisites

- Docker Desktop (or Docker Engine + Compose plugin)
- Git (optional)

---

## Quick Start

```bash
# 1. Clone / enter the project
cd docker-todo-app

# 2. Build images and start all containers
docker compose up --build

# 3. Open the app
open http://localhost:8080
```

Stop everything:
```bash
docker compose down          # stop containers, keep volume
docker compose down -v       # stop + delete the database volume
```

---

## Practice Tasks (do these one by one)

### Task 1 — Inspect running containers
```bash
docker compose ps
docker stats                          # live CPU/memory per container
docker inspect todo_db               # full container metadata
```

### Task 2 — Read logs
```bash
docker compose logs -f                # all services, follow
docker compose logs backend           # only Flask logs
docker compose logs --tail=20 nginx   # last 20 lines from nginx
```

### Task 3 — Exec into a container
```bash
# Shell into the backend
docker exec -it todo_backend sh

# Shell into the database and run a query
docker exec -it todo_db psql -U todo_user -d todo_db
  \dt                         -- list tables
  SELECT * FROM todos;        -- view data
  \q                          -- quit
```

### Task 4 — Test the API directly (bypass Nginx)
The backend port is NOT published to the host (only Nginx is).
This is intentional — it forces traffic through the proxy.

To test the Flask API directly, exec into nginx:
```bash
docker exec -it todo_nginx sh
curl http://backend:5000/health
curl http://backend:5000/todos
```

Or expose the backend temporarily in docker-compose.yml:
```yaml
backend:
  ports:
    - "5001:5000"   # add this line, then docker compose up -d
```
Then: `curl http://localhost:5001/todos`

### Task 5 — Volume persistence
```bash
# Add some todos in the browser, then restart containers
docker compose down
docker compose up -d        # data should still be there (volume persists)

# Now destroy the volume too
docker compose down -v
docker compose up --build   # todos are gone, seed data reloads
```

### Task 6 — Environment variables
Change the DB password in docker-compose.yml:
```yaml
POSTGRES_PASSWORD: mynewpassword
DATABASE_URL: postgresql://todo_user:mynewpassword@db:5432/todo_db
```
Then: `docker compose down -v && docker compose up --build`

### Task 7 — Scale the backend (load balancing practice)
```bash
docker compose up --scale backend=3 -d
docker compose ps           # see 3 backend containers
```
Note: Nginx will round-robin between them automatically
because of `upstream backend { server backend:5000; }`.

### Task 8 — Networks (isolation practice)
```bash
docker network ls
docker network inspect docker-todo-app_backend_net
docker network inspect docker-todo-app_frontend_net
```
Try to ping db from nginx (should FAIL — different network):
```bash
docker exec todo_nginx ping todo_db    # expected: network unreachable
docker exec todo_backend ping todo_db  # expected: works
```

### Task 9 — Build a new image version
Edit backend/app.py — add a new endpoint:
```python
@app.route("/todos/count")
def count():
    return jsonify({"count": Todo.query.count()})
```
Then rebuild only the backend:
```bash
docker compose build backend
docker compose up -d backend    # rolling restart, no downtime for db/nginx
```

### Task 10 — Multi-stage build inspection
```bash
docker images | grep docker-todo-app   # compare image sizes
docker history docker-todo-app-backend # see each layer
```

---

## API Reference

| Method | Endpoint         | Body                   | Description        |
|--------|------------------|------------------------|--------------------|
| GET    | /api/health      | —                      | Health check       |
| GET    | /api/todos       | —                      | List all todos     |
| POST   | /api/todos       | `{"task": "string"}`   | Create a todo      |
| PUT    | /api/todos/:id   | `{"done": true/false}` | Update a todo      |
| DELETE | /api/todos/:id   | —                      | Delete a todo      |

Test with curl:
```bash
curl http://localhost:8080/api/todos
curl -X POST http://localhost:8080/api/todos \
  -H "Content-Type: application/json" \
  -d '{"task":"Study Docker networking"}'
curl -X PUT http://localhost:8080/api/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"done":true}'
curl -X DELETE http://localhost:8080/api/todos/1
```

---

## Key Concepts Covered

| Concept                  | Where used                              |
|--------------------------|-----------------------------------------|
| Multi-stage build        | backend/Dockerfile (builder + runtime)  |
| Named volumes            | db_data for Postgres persistence        |
| Custom networks          | backend_net, frontend_net               |
| Health checks            | db and backend services                 |
| depends_on + condition   | backend waits for db to be healthy      |
| Reverse proxy            | Nginx routes /api/* to Flask            |
| Non-root container user  | appuser in backend Dockerfile           |
| Service discovery        | backend connects to "db" by name        |
| Init scripts             | postgres-init/seed.sql                  |
| Scaling                  | --scale backend=3                       |

---

## Troubleshooting

**App not loading:**
```bash
docker compose logs nginx
docker compose ps           # check all containers are "running"
```

**Database connection error:**
```bash
docker compose logs db
docker compose logs backend
# Usually means db isn't healthy yet — wait 10s and retry
```

**Port 8080 already in use:**
Change the nginx ports mapping in docker-compose.yml:
```yaml
ports:
  - "9090:80"   # use 9090 instead
```
