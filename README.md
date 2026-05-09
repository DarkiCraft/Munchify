# Munchify

A simple food recommendation project.

This repository is the parent/orchestration repo. The backend application lives in the `backend` submodule, the frontend will eventually go in a `frontend` submodule (WIP) and this root project provides Docker Compose to run everything together.

Both backend and frontend (WIP) are also independently runnable as their own Dockerized service with any external PostgreSQL database. See their respective READMEs for more info.

## Why this project

- Demonstrates backend API design with FastAPI.
- Demonstrates PostgreSQL integration with SQLAlchemy.
- Demonstrates hybrid recommendation-system techniques depending on context.
- Demonstrates basic recommendation-system workflows (including retraining hooks).
- Demonstrates containerized local setup with Docker Compose.

## Tech stack

- Python 3.11
- FastAPI
- PostgreSQL
- SQLAlchemy
- Docker + Docker Compose

## Repository structure

- `backend/` - FastAPI app, models, services, controllers, and Dockerfile
- `docker-compose.yml` - runs backend + PostgreSQL together

## Quick start (Docker)

From this root folder:

```bash
docker compose up -d --build
docker compose ps
```

Then open:

- API docs: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

Stop everything:

```bash
docker compose down
```

## Environment setup

Main app configurations are in:

- `backend/.env` (real values for local dev)
- `backend/.env.example` (template)
- `frontend/.env` (WIP)
- `frontent/.env.example` (WIP)

## Optional: seed/reset data

The backend includes an `init.py` script that:

- Drops and recreates DB tables
- Seeds mock users/items/interactions
- Retrains recommender artifacts

This is destructive by design and intended for local/demo bootstrap.

One-off run:

```bash
docker compose run --rm backend python init.py
```

Or set `RUN_INIT=1` in `backend/.env` for a startup-triggered run, then set it back to `0`.

## License

Project is licensed under the [MIT](LICENSE) License.