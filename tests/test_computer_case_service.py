import unittest
from decimal import Decimal

from app import create_app
from app.domain.enums import OperationalStatus
from app.extensions import db
from app.services.inventory_service import InventoryService


class ComputerCaseServiceTestCase(unittest.TestCase):
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

    def test_create_computer_case_with_complete_technical_data(self):
        computer_case = self.inventory_service.create_computer_case(self._computer_case_data())

        self.assertIsNotNone(computer_case.id)
        self.assertEqual("PAT-001", computer_case.asset_tag)
        self.assertEqual("SN-001", computer_case.serial_number)
        self.assertEqual(Decimal("3.70"), computer_case.processor_frequency_ghz)
        self.assertEqual(Decimal("8.00"), computer_case.installed_memory_gb)
        self.assertEqual(OperationalStatus.EM_FUNCIONAMENTO, computer_case.operational_status)

    def test_create_rejects_duplicate_asset_tag(self):
        self.inventory_service.create_computer_case(self._computer_case_data(asset_tag="PAT-001"))

        with self.assertRaisesRegex(ValueError, "Asset tag already exists."):
            self.inventory_service.create_computer_case(self._computer_case_data(asset_tag="pat-001", serial_number="SN-002"))

    def test_create_rejects_duplicate_serial_number(self):
        self.inventory_service.create_computer_case(self._computer_case_data(serial_number="SN-001"))

        with self.assertRaisesRegex(ValueError, "Serial number already exists."):
            self.inventory_service.create_computer_case(self._computer_case_data(asset_tag="PAT-002", serial_number="sn-001"))

    def test_create_allows_empty_serial_number_in_multiple_records(self):
        first = self.inventory_service.create_computer_case(self._computer_case_data(asset_tag="PAT-001", serial_number=""))
        second = self.inventory_service.create_computer_case(self._computer_case_data(asset_tag="PAT-002", serial_number=""))

        self.assertIsNone(first.serial_number)
        self.assertIsNone(second.serial_number)

    def test_update_computer_case(self):
        computer_case = self.inventory_service.create_computer_case(self._computer_case_data())

        self.inventory_service.update_computer_case(
            computer_case,
            self._computer_case_data(
                asset_tag="PAT-002",
                serial_number="SN-002",
                model="OptiPlex 7050",
                operational_status="EM_MANUTENCAO",
            ),
        )

        self.assertEqual("PAT-002", computer_case.asset_tag)
        self.assertEqual("SN-002", computer_case.serial_number)
        self.assertEqual("OptiPlex 7050", computer_case.model)
        self.assertEqual(OperationalStatus.EM_MANUTENCAO, computer_case.operational_status)

    def test_set_operational_status(self):
        computer_case = self.inventory_service.create_computer_case(self._computer_case_data())

        self.inventory_service.set_computer_case_status(computer_case, "DESATIVADO")

        self.assertEqual(OperationalStatus.DESATIVADO, computer_case.operational_status)

    def test_rejects_invalid_operational_status(self):
        with self.assertRaisesRegex(ValueError, "Invalid operational status."):
            self.inventory_service.create_computer_case(self._computer_case_data(operational_status="QUEBRADO"))

    def test_rejects_invalid_purchase_date(self):
        with self.assertRaisesRegex(ValueError, "Purchase date must use YYYY-MM-DD."):
            self.inventory_service.create_computer_case(self._computer_case_data(purchase_date="15/03/2022"))

    def test_rejects_invalid_decimal_field(self):
        with self.assertRaisesRegex(ValueError, "Processor frequency must be a valid decimal number."):
            self.inventory_service.create_computer_case(self._computer_case_data(processor_frequency_ghz="abc"))

    def test_rejects_invalid_integer_field(self):
        with self.assertRaisesRegex(ValueError, "Memory speed must be an integer."):
            self.inventory_service.create_computer_case(self._computer_case_data(memory_speed_mhz="fast"))

    def test_get_computer_case_not_found(self):
        with self.assertRaises(LookupError):
            self.inventory_service.get_computer_case(999)

    def _computer_case_data(self, **overrides):
        data = {
            "asset_tag": "pat-001",
            "serial_number": "sn-001",
            "manufacturer": "Dell",
            "model": "OptiPlex 3040",
            "batch": "Lote 2022-A",
            "purchase_date": "2022-03-15",
            "processor_model": "Intel Core i3-6100",
            "processor_frequency_ghz": "3.70",
            "motherboard_model": "Dell 0XJ8C4",
            "installed_memory_gb": "8",
            "memory_technology": "DDR4",
            "memory_speed_mhz": "2133",
            "memory_slots_total": "2",
            "memory_slots_usage": "1x8GB",
            "storage_description": "SSD 240GB SATA",
            "power_supply_description": "Fonte Dell 240W",
            "operating_system": "Ubuntu MATE 22.04",
            "operational_status": "EM_FUNCIONAMENTO",
            "notes": "Initial technical collection",
        }
        data.update(overrides)
        return data


if __name__ == "__main__":
    unittest.main()
