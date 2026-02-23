from collections.abc import Generator
from uuid import uuid4

import pytest
from app.database import engine
from app.main import app
from app.models.device import Device
from app.models.rack import Rack
from fastapi.testclient import TestClient
from sqlmodel import Session, delete


@pytest.fixture(scope="function")
def session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
        statement = delete(Device)
        session.exec(statement)
        statement = delete(Rack)
        session.exec(statement)
        session.commit()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_devices(session: Session) -> list[Device]:
    devices = [
        Device(name="Server 1", serial_number="SRV001", units_required=4, power_w=800),
        Device(name="Server 2", serial_number="SRV002", units_required=4, power_w=750),
        Device(name="Server 3", serial_number="SRV003", units_required=2, power_w=400),
        Device(name="Switch 1", serial_number="SW001", units_required=1, power_w=150),
        Device(name="Switch 2", serial_number="SW002", units_required=1, power_w=150),
    ]
    for device in devices:
        session.add(device)
    session.commit()
    for device in devices:
        session.refresh(device)
    return devices


@pytest.fixture
def sample_racks(session: Session) -> list[Rack]:
    racks = [
        Rack(name="Rack A", serial_number="RACK001", total_units=42, max_power_w=5000),
        Rack(name="Rack B", serial_number="RACK002", total_units=42, max_power_w=5000),
    ]
    for rack in racks:
        session.add(rack)
    session.commit()
    for rack in racks:
        session.refresh(rack)
    return racks
