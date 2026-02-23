import pytest
from app.models.device import Device
from app.models.distribution import DistributionRequest
from app.models.rack import Rack
from app.services.distribution_service import calculate_distribution
from sqlmodel import Session


class TestDistributionBasic:
    def test_empty_devices_list(self, session: Session, sample_racks: list[Rack]):
        request = DistributionRequest(
            device_ids=[],
            rack_ids=[r.id for r in sample_racks],
        )
        result = calculate_distribution(session, request)

        assert result.distribution is not None
        assert len(result.unplaced_devices) == 0
        assert result.summary["total_devices"] == 0
        assert result.summary["placed_devices"] == 0

    def test_single_device_single_rack(self, session: Session):
        device = Device(
            name="Test Server", serial_number="TEST001", units_required=4, power_w=1000
        )
        session.add(device)

        rack = Rack(
            name="Test Rack", serial_number="RACK001", total_units=42, max_power_w=5000
        )
        session.add(rack)
        session.commit()
        session.refresh(device)
        session.refresh(rack)

        request = DistributionRequest(
            device_ids=[device.id],
            rack_ids=[rack.id],
        )
        result = calculate_distribution(session, request)

        assert len(result.unplaced_devices) == 0
        assert result.summary["placed_devices"] == 1
        assert len(result.distribution) == 1
        assert len(result.distribution[0].devices) == 1
        assert result.distribution[0].devices[0].id == device.id

    def test_all_devices_placed(
        self, session: Session, sample_devices: list[Device], sample_racks: list[Rack]
    ):
        request = DistributionRequest(
            device_ids=[d.id for d in sample_devices],
            rack_ids=[r.id for r in sample_racks],
        )
        result = calculate_distribution(session, request)

        assert len(result.unplaced_devices) == 0
        assert result.summary["placed_devices"] == len(sample_devices)
        assert result.summary["unplaced_devices"] == 0


class TestDistributionBalancing:

    def test_balanced_distribution(self, session: Session):
        devices = []
        for i in range(4):
            d = Device(
                name=f"Server {i}",
                serial_number=f"SRV{i:03d}",
                units_required=2,
                power_w=1000,
            )
            session.add(d)
            devices.append(d)

        racks = []
        for i in range(2):
            r = Rack(
                name=f"Rack {i}",
                serial_number=f"RACK{i:03d}",
                total_units=42,
                max_power_w=5000,
            )
            session.add(r)
            racks.append(r)

        session.commit()
        for d in devices:
            session.refresh(d)
        for r in racks:
            session.refresh(r)

        request = DistributionRequest(
            device_ids=[d.id for d in devices],
            rack_ids=[r.id for r in racks],
        )
        result = calculate_distribution(session, request)

        assert len(result.unplaced_devices) == 0

        devices_per_rack = [len(r.devices) for r in result.distribution]
        assert sum(devices_per_rack) == 4
        utilizations = [r.utilization_percent for r in result.distribution]
        spread = max(utilizations) - min(utilizations)
        assert spread < 10, f"Utilization spread too high: {spread}%"

    def test_utilization_spread_minimized(self, session: Session):
        devices = [
            Device(
                name="Big Server",
                serial_number="BIG001",
                units_required=4,
                power_w=2000,
            ),
            Device(
                name="Medium Server",
                serial_number="MED001",
                units_required=2,
                power_w=1000,
            ),
            Device(
                name="Small Server",
                serial_number="SML001",
                units_required=1,
                power_w=500,
            ),
        ]
        for d in devices:
            session.add(d)

        racks = [
            Rack(
                name="Rack A", serial_number="RA001", total_units=42, max_power_w=5000
            ),
            Rack(
                name="Rack B", serial_number="RB001", total_units=42, max_power_w=5000
            ),
        ]
        for r in racks:
            session.add(r)

        session.commit()
        for d in devices:
            session.refresh(d)
        for r in racks:
            session.refresh(r)

        request = DistributionRequest(
            device_ids=[d.id for d in devices],
            rack_ids=[r.id for r in racks],
        )
        result = calculate_distribution(session, request)

        assert (
            result.summary["utilization_spread"] <= 30
        ), f"Spread is {result.summary['utilization_spread']}%, expected <= 30%"


class TestDistributionUnplacedDevices:
    def test_device_too_big_for_any_rack_units(self, session: Session):

        device = Device(
            name="Huge Device", serial_number="HUGE001", units_required=50, power_w=500
        )
        session.add(device)

        rack = Rack(
            name="Standard Rack",
            serial_number="STD001",
            total_units=42,
            max_power_w=10000,
        )
        session.add(rack)
        session.commit()
        session.refresh(device)
        session.refresh(rack)

        request = DistributionRequest(
            device_ids=[device.id],
            rack_ids=[rack.id],
        )
        result = calculate_distribution(session, request)

        assert len(result.unplaced_devices) == 1
        assert result.unplaced_devices[0].device_id == device.id
        assert "units" in result.unplaced_devices[0].reason.lower()

    def test_device_exceeds_power_capacity(self, session: Session):
        device = Device(
            name="Power Hungry", serial_number="PWR001", units_required=4, power_w=6000
        )
        session.add(device)

        rack = Rack(
            name="Standard Rack",
            serial_number="STD001",
            total_units=42,
            max_power_w=5000,
        )
        session.add(rack)
        session.commit()
        session.refresh(device)
        session.refresh(rack)

        request = DistributionRequest(
            device_ids=[device.id],
            rack_ids=[rack.id],
        )
        result = calculate_distribution(session, request)

        assert len(result.unplaced_devices) == 1
        assert result.unplaced_devices[0].device_id == device.id
        assert "power" in result.unplaced_devices[0].reason.lower()

    def test_not_enough_total_capacity(self, session: Session):
        devices = []
        for i in range(10):
            d = Device(
                name=f"Server {i}",
                serial_number=f"SRV{i:03d}",
                units_required=5,
                power_w=400,
            )
            session.add(d)
            devices.append(d)

        rack = Rack(
            name="Single Rack",
            serial_number="SINGLE001",
            total_units=42,
            max_power_w=10000,
        )
        session.add(rack)
        session.commit()

        for d in devices:
            session.refresh(d)
        session.refresh(rack)

        request = DistributionRequest(
            device_ids=[d.id for d in devices],
            rack_ids=[rack.id],
        )
        result = calculate_distribution(session, request)

        assert len(result.unplaced_devices) > 0
        placed = result.summary["placed_devices"]
        unplaced = result.summary["unplaced_devices"]
        assert placed + unplaced == 10


class TestDistributionEdgeCases:

    def test_no_racks_available(self, session: Session):
        device = Device(
            name="Orphan", serial_number="ORP001", units_required=2, power_w=500
        )
        session.add(device)
        session.commit()
        session.refresh(device)

        request = DistributionRequest(
            device_ids=[device.id],
            rack_ids=[],
        )
        result = calculate_distribution(session, request)

        assert len(result.unplaced_devices) == 1
        assert "no racks" in result.unplaced_devices[0].reason.lower()

    def test_device_not_found(self, session: Session, sample_racks: list[Rack]):
        from app.exceptions import NotFoundError

        request = DistributionRequest(
            device_ids=[99999],  # Ne postoji
            rack_ids=[r.id for r in sample_racks],
        )

        with pytest.raises(NotFoundError):
            calculate_distribution(session, request)

    def test_rack_not_found(self, session: Session, sample_devices: list[Device]):
        from app.exceptions import NotFoundError

        request = DistributionRequest(
            device_ids=[d.id for d in sample_devices],
            rack_ids=[99999],  # Ne postoji
        )

        with pytest.raises(NotFoundError):
            calculate_distribution(session, request)


class TestDistributionSummary:

    def test_summary_statistics(
        self, session: Session, sample_devices: list[Device], sample_racks: list[Rack]
    ):
        request = DistributionRequest(
            device_ids=[d.id for d in sample_devices],
            rack_ids=[r.id for r in sample_racks],
        )
        result = calculate_distribution(session, request)

        summary = result.summary

        assert "total_devices" in summary
        assert "placed_devices" in summary
        assert "unplaced_devices" in summary
        assert "total_racks" in summary
        assert "average_utilization_percent" in summary
        assert "max_utilization_percent" in summary
        assert "min_utilization_percent" in summary
        assert "utilization_spread" in summary

        assert summary["total_devices"] == len(sample_devices)
        assert summary["total_racks"] == len(sample_racks)
        assert (
            summary["placed_devices"] + summary["unplaced_devices"]
            == summary["total_devices"]
        )
