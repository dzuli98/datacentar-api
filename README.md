# Data Center API

## 🚀 Overview

Data Center API is a RESTful application for managing devices and racks in a data center, tracking power consumption, and providing suggestions for optimal device placement.

**Key Features:**
- Device and Rack management (CRUD operations)
- Device placement tracking within racks
- Device distribution algorithm for good rack utilization
- Power consumption tracking and utilization metrics
- Health monitoring endpoints

**Tech Stack:**
- **Framework:** FastAPI (Python async web framework)
- **Database:** PostgreSQL with SQLModel ORM
- **Containerization:** Docker & Docker Compose
- **API Documentation:** Swagger UI

---

## 🏗️ Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration and environment variables
│   ├── database.py             # Database connection and session management
│   ├── exceptions.py           # Custom exceptions
│   ├── models/                 # SQLModel data models
│   │   ├── device.py           # Device model
│   │   ├── rack.py             # Rack model
│   │   ├── placement.py        # Device placement in rack model
│   │   └── distribution.py     # Distribution algorithm request/response models
│   ├── routers/                # API endpoint routers
│   │   ├── device_router.py
│   │   ├── rack_router.py
│   │   ├── placement_router.py
│   │   └── distribution_router.py
│   ├── services/               # Business logic services
│   │   ├── device_service.py
│   │   ├── rack_service.py
│   │   ├── placement_service.py
│   │   └── distribution_service.py
│   └── alembic/                # Database migrations
├── tests/                      # Test suite
│   ├── conftest.py            # Pytest fixtures and configuration
│   └── test_distribution.py   # Distribution algorithm tests
└── Dockerfile
```

---

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose installed
- Python 3.12+ (for local development without Docker)
- UV package manager (for local development)

### Quick Start with Docker

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/datacentar-api.git
   cd datacentar-api
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   Default values are suitable for local development.

3. **Start the application:**
   ```bash
   docker compose up --build --watch
   ```

4. **Access the API:**
   - REST API: [http://localhost:8000](http://localhost:8000)
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Database Admin (Adminer): [http://localhost:8080](http://localhost:8080)

---

## 📡 Available API Endpoints

All endpoints are versioned under `/api/v1` and return JSON responses.

### Device Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/devices` | Create a new device |
| `GET` | `/api/v1/devices` | List all devices (paginated) |
| `GET` | `/api/v1/devices/{device_id}` | Get device details |
| `PUT` | `/api/v1/devices/{device_id}` | Update device information |
| `DELETE` | `/api/v1/devices/{device_id}` | Delete a device |

### Rack Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/racks` | Create a new rack |
| `GET` | `/api/v1/racks` | List all racks (paginated) |
| `GET` | `/api/v1/racks/{rack_id}` | Get rack details with utilization metrics |
| `PUT` | `/api/v1/racks/{rack_id}` | Update rack configuration |
| `DELETE` | `/api/v1/racks/{rack_id}` | Delete a rack |

### Placement Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/placements` | Place a device in a specific rack |
| `GET` | `/api/v1/placements` | List all device placements |
| `DELETE` | `/api/v1/placements/{placement_id}` | Remove a device from a rack |

### Distribution Algorithm
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/distribution/calculate` | Calculate optimal device placement across racks |

### Health & System
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/health` | Health check endpoint |

---

## 🔧 Services & Business Logic

The application uses a layered architecture with service classes that contain business logic:

### Device Service (`app/services/device_service.py`)
- CRUD operations for devices
- Power consumption tracking
- Device validation (serial number uniqueness, power constraints)

### Rack Service (`app/services/rack_service.py`)
- CRUD operations for racks
- Rack capacity calculations
- Utilization metrics computation

### Placement Service (`app/services/placement_service.py`)
- Device placement validation
- Unit allocation management
- Power capacity checks

### Distribution Service (`app/services/distribution_service.py`)
- **Algorithm:** Balances device distribution across racks
- **Input:** Device IDs and Rack IDs
- **Output:** Optimal placement suggestions with utilization metrics
- **Strategy:** Largest-first fit with power-balanced distribution
  - Sorts devices by power consumption (largest first)
  - Assigns each device to the rack with lowest current utilization
  - Ensures power limits are not exceeded

**Example Usage:**

```bash
curl -X POST http://localhost:8000/api/v1/distribution/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "device_ids": [1, 2, 3],
    "rack_ids": [1, 2]
  }'
```

## 🧪 Testing

### Running Tests with Docker

```bash
docker compose exec backend bash scripts/tests-start.sh
```
When the tests are run, a file htmlcov/index.html is generated, you can open it in your browser to see the coverage of the tests.

### Test Structure

- **`tests/conftest.py`** — Pytest fixtures and database session management
  - Database initialization and cleanup
  - Sample data fixtures (devices, racks)
  - Test client configuration

- **`tests/test_distribution.py`** — Distribution algorithm tests
  - 13 service-level tests for distribution logic
  - 5 API endpoint tests for distribution router
  - Edge case coverage (capacity exceeded, no racks available, etc.)

---

## 🗄️ Database

### Migrations with Alembic

Create a new migration:
```bash
cd backend
alembic revision --autogenerate -m "Add new column"
```

Apply migrations:
```bash
alembic upgrade head
```

Downgrade:
```bash
alembic downgrade -1
```

### Database Models

- **Device** — Server hardware specifications (power, units, serial number)
- **Rack** — Physical server rack with capacity constraints
- **RackPlacement** — Association between devices and racks with unit positions
- **DistributionRequest/Response** — Algorithm input/output models

---

## 📚 API Documentation

Interactive documentation is auto-generated:

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🛠️ Development Tips

1. **Hot reload:** Docker compose is configured with `--watch` for automatic server restart on file changes
2. **Database browser:** Use Adminer at [http://localhost:8080](http://localhost:8080)
3. **Database user:** `postgres` | **Password:** `postgres` (from `.env.example`)

---

## 📝 License

MIT

---
