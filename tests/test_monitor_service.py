import unittest
from decimal import Decimal

from app import create_app
from app.domain.enums import DisplayConnection, OperationalStatus
from app.extensions import db
from app.services.inventory_service import InventoryService


class MonitorServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.inventory_service = InventoryService()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_monitor_with_complete_data(self):
        monitor = self.inventory_service.create_monitor(self._monitor_data())

        self.assertIsNotNone(monitor.id)
        self.assertEqual("MON-001", monitor.asset_tag)
        self.assertEqual("MSN-001", monitor.serial_number)
        self.assertEqual(Decimal("21.50"), monitor.screen_size_inches)
        self.assertEqual(DisplayConnection.HDMI, monitor.display_connection)
        self.assertEqual(OperationalStatus.FUNCIONAL_DESALOCADO, monitor.operational_status)

    def test_create_rejects_duplicate_asset_tag(self):
        self.inventory_service.create_monitor(self._monitor_data(asset_tag="MON-001"))

        with self.assertRaisesRegex(ValueError, "Asset tag already exists."):
            self.inventory_service.create_monitor(self._monitor_data(asset_tag="mon-001", serial_number="MSN-002"))

    def test_create_rejects_duplicate_serial_number(self):
        self.inventory_service.create_monitor(self._monitor_data(serial_number="MSN-001"))

        with self.assertRaisesRegex(ValueError, "Serial number already exists."):
            self.inventory_service.create_monitor(self._monitor_data(asset_tag="MON-002", serial_number="msn-001"))

    def test_create_allows_empty_serial_number_in_multiple_records(self):
        first = self.inventory_service.create_monitor(self._monitor_data(asset_tag="MON-001", serial_number=""))
        second = self.inventory_service.create_monitor(self._monitor_data(asset_tag="MON-002", serial_number=""))

        self.assertIsNone(first.serial_number)
        self.assertIsNone(second.serial_number)

    def test_update_monitor(self):
        monitor = self.inventory_service.create_monitor(self._monitor_data())

        self.inventory_service.update_monitor(
            monitor,
            self._monitor_data(
                asset_tag="MON-002",
                serial_number="MSN-002",
                model="P2219H",
                display_connection="DISPLAYPORT",
                operational_status="EM_MANUTENCAO",
            ),
        )

        self.assertEqual("MON-002", monitor.asset_tag)
        self.assertEqual("MSN-002", monitor.serial_number)
        self.assertEqual("P2219H", monitor.model)
        self.assertEqual(DisplayConnection.DISPLAYPORT, monitor.display_connection)
        self.assertEqual(OperationalStatus.EM_MANUTENCAO, monitor.operational_status)

    def test_set_operational_status(self):
        monitor = self.inventory_service.create_monitor(self._monitor_data())

        self.inventory_service.set_monitor_status(monitor, "DESATIVADO")

        self.assertEqual(OperationalStatus.DESATIVADO, monitor.operational_status)

    def test_rejects_invalid_display_connection(self):
        with self.assertRaisesRegex(ValueError, "Invalid display connection."):
            self.inventory_service.create_monitor(self._monitor_data(display_connection="SCART"))

    def test_rejects_invalid_screen_size(self):
        with self.assertRaisesRegex(ValueError, "Screen size must be a valid decimal number."):
            self.inventory_service.create_monitor(self._monitor_data(screen_size_inches="large"))

    def test_rejects_invalid_purchase_date(self):
        with self.assertRaisesRegex(ValueError, "Purchase date must use YYYY-MM-DD."):
            self.inventory_service.create_monitor(self._monitor_data(purchase_date="15/03/2022"))

    def test_get_monitor_not_found(self):
        with self.assertRaises(LookupError):
            self.inventory_service.get_monitor(999)

    def _monitor_data(self, **overrides):
        data = {
            "asset_tag": "mon-001",
            "serial_number": "msn-001",
            "manufacturer": "Dell",
            "model": "E2216H",
            "purchase_date": "2022-03-15",
            "screen_size_inches": "21.50",
            "display_connection": "HDMI",
            "operational_status": "FUNCIONAL_DESALOCADO",
            "notes": "Initial monitor collection",
        }
        data.update(overrides)
        return data


if __name__ == "__main__":
    unittest.main()
