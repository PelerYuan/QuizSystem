
# 📚 Quiz System

Web-based quiz platform built with Flask. Create, run, and analyze quizzes with a visual editor and CSV/Excel export.

![Flask](https://img.shields.io/badge/Flask-3.1.1-blue?logo=flask)
![Python](https://img.shields.io/badge/Python-3.12-green?logo=python)
![Docker](https://img.shields.io/badge/Docker-Compose-blue?logo=docker)
![License](https://img.shields.io/badge/License-GPLv3-red)

## ✨ Overview

QuizSystem is a simple but capable quiz application. It includes an admin interface, a visual quiz editor, multiple question types, results storage in SQLite, and export to Excel.

Key features:
- Visual quiz editor (drag-and-drop, image support)
- Single/multiple-choice and text questions
- Results export to Excel
- Docker-Compose deployment with persistent volumes

---

## 🐳 Step-by-step deployment with Docker Compose (recommended)

These steps run the app on your machine using Docker and Docker Compose v2.

### 1) Prerequisites
- Docker Engine and Docker Compose v2 installed
- Ports 8000 available on your host (or adjust mapping below)

### 2) Clone this repository
```bash
git clone https://github.com/PelerYuan/QuizSystem
cd QuizSystem
```

### 3) (Optional) Configure admin password
The admin password lives in `configure.json` and is mounted read-only into the container.

Default content:
```json
{
  "admin password": "123456"
}
```
If you change it here before starting, it will be used immediately by the container.

### 4) Build the image
```bash
docker compose build
```

### 5) Start the stack
```bash
docker compose up -d
```

What this does:
- Builds the image defined in `Dockerfile`
- Starts the `quizsystem` service from `docker-compose.yml`
- Maps container port 8000 to host port 8000
- Mounts volumes so your data and media persist on the host

### 6) Verify the service
```bash
curl -fsS http://localhost:8000/health && echo "OK"
```
Open the app in your browser:
- User interface: http://localhost:8000
- Admin login: http://localhost:8000/admin_login (password from `configure.json`)

### 7) Operate the stack
- View logs: `docker compose logs -f`
- Stop: `docker compose down`
- Restart after edits: `docker compose up -d --build`

### 8) Persisted data and volumes
By default, the compose file uses named Docker volumes for writable data. Inside the container these paths are used:
- `/app/data` (named volume `db`) — contains the SQLite database at `/app/data/data.sqlite`
- `/app/img` (named volume `img`) — uploaded images
- `/app/quiz` (named volume `quiz`) — quiz JSON files
- `/app/result` (named volume `result`) — exported results
- `/app/tmp` (named volume `tmp`) — temporary files
- `./configure.json -> /app/configure.json:ro` — admin password (bind-mounted read-only from the repo)

Notes:
- On first start, the container auto-initializes the database schema (idempotent). No manual step is needed.
- To change the host port, edit `docker-compose.yml` and modify `ports: - "8000:8000"` (format is `HOST:CONTAINER`).

### 9) Healthcheck and readiness
- Container exposes `GET /health` which returns JSON and is used by the Compose `healthcheck`.
- The Dockerfile runs `flask run` on port 8000.

### 10) Backup and restore
Because writable data lives in named volumes, you can back them up with a temporary helper container:

- Backup the DB volume to a local folder:
  ```bash
  mkdir -p backup/db
  docker run --rm \
    -v quizsystem_db:/from \
    -v $(pwd)/backup/db:/to \
    busybox sh -c "cp -a /from/. /to/"
  ```
- Similarly backup other volumes (`quizsystem_img`, `quizsystem_quiz`, `quizsystem_result`, `quizsystem_tmp`) if desired by replacing the volume name after `-v`.

To restore, reverse the copy (from your backup folder into the corresponding volume) using the same pattern.

---

## 💻 Local development (without Docker)

1) Clone and prepare folders
```bash
git clone https://github.com/PelerYuan/QuizSystem
cd QuizSystem
mkdir -p img quiz result tmp
```

2) Create a virtual environment and install deps
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3) Initialize database (first run only)
```bash
python -c "from app import db; db.create_all()"
```

4) Run the app
```bash
python app.py
```
Open http://localhost:5000 by default (Flask dev server). For production, prefer Docker Compose above.

---

## 🔐 Admin area
- Login page: `/admin_login`
- Password source: `configure.json` (`"admin password"` key)

## 📊 Results export
Exports are saved to the `result/` folder as Excel files (OpenPyXL).

## 🔎 Troubleshooting
- Port already in use: change the host port in `docker-compose.yml` (`ports:` section) and restart.
- Health check failing: run `docker compose logs -f` to see startup logs. The container automatically initializes the database; if it still fails, share the logs.

## 🤝 Contributing
PRs are welcome! Fork the repo, create a feature branch, and open a pull request.

## 📄 License
Licensed under the GNU General Public License v3.0. See `LICENSE.md`.

## 🙋 Support
Open an issue: https://github.com/PelerYuan/QuizSystem/issues