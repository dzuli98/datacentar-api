# Data Center API

## Overview

Data Center API is a RESTful application for managing devices and racks in a data center, tracking power consumption, and providing suggestions for optimal device placement. Built with FastAPI and SQLModel, PostgreSQL and Docker.

---

## Available API Endpoints

All endpoints are versioned under `/api/v1`.

- `POST /api/v1/devices` — Create a new device
- `GET /api/v1/devices` — List all devices
- `GET /api/v1/devices/{device_id}` — Get device details
- `PUT /api/v1/devices/{device_id}` — Update device
- `DELETE /api/v1/devices/{device_id}` — Delete device

- `POST /api/v1/racks` — Create a new rack
- `GET /api/v1/racks` — List all racks
- `GET /api/v1/racks/{rack_id}` — Get rack details
- `PUT /api/v1/racks/{rack_id}` — Update rack
- `DELETE /api/v1/racks/{rack_id}` — Delete rack

- `POST /api/v1/placements` — Place a device in a rack
- `GET /api/v1/placements` — List all placements
- `DELETE /api/v1/placements/{placement_id}` — Remove a device from a rack

- `POST /api/v1/distribution` — Suggest optimal device placement across racks
- `GET /api/v1/health` — Health check

Interactive API docs:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Running with Docker Compose

1. Copy `.env.example` to `.env` and adjust variables as needed.
2. Build and start services:

```bash
docker compose up --build --watch
```

- The backend will be available at [http://localhost:8000](http://localhost:8000)
- PostgreSQL and Adminer will also be started

---

## Running Tests

Tests for the device distribution algorithm are provided as unit/integration tests.

To run tests:

```bash
docker compose exec backend bash
```

To run tests in Docker:

```bash
docker compose exec backend bash scripts/tests-start.sh
```

---

## License

MIT