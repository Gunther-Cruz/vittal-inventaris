import unittest

from app import create_app
from app.extensions import db
from app.services.inventory_service import InventoryService


class WorkstationServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.inventory_service = InventoryService()
        self.lab_10 = self.inventory_service.create_laboratory(
            {"code": "LAB-10", "name": "Laboratory 10", "pavilion": "Pavilion 10"}
        )
        self.lab_11 = self.inventory_service.create_laboratory(
            {"code": "LAB-11", "name": "Laboratory 11", "pavilion": "Pavilion 11"}
        )

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_workstation_normalizes_code_and_assigns_first_position(self):
        workstation = self.inventory_service.create_workstation(
            self.lab_10,
            {
                "code": " e01 ",
                "notes": "First position",
            },
        )

        self.assertIsNotNone(workstation.id)
        self.assertEqual("E01", workstation.code)
        self.assertEqual(1, workstation.map_position_x)
        self.assertEqual(1, workstation.map_position_y)
        self.assertTrue(workstation.active)

    def test_create_workstations_assigns_positions_in_four_column_matrix(self):
        workstations = [self._create_workstation(self.lab_10, f"E0{index}") for index in range(1, 6)]

        self.assertEqual((1, 1), (workstations[0].map_position_x, workstations[0].map_position_y))
        self.assertEqual((2, 1), (workstations[1].map_position_x, workstations[1].map_position_y))
        self.assertEqual((3, 1), (workstations[2].map_position_x, workstations[2].map_position_y))
        self.assertEqual((4, 1), (workstations[3].map_position_x, workstations[3].map_position_y))
        self.assertEqual((1, 2), (workstations[4].map_position_x, workstations[4].map_position_y))

    def test_rejects_duplicate_code_in_same_laboratory(self):
        self._create_workstation(self.lab_10, "E01")

        with self.assertRaises(ValueError):
            self._create_workstation(self.lab_10, "e01")

    def test_allows_same_code_in_different_laboratories(self):
        first = self._create_workstation(self.lab_10, "E01")
        second = self._create_workstation(self.lab_11, "E01")

        self.assertNotEqual(first.id, second.id)
        self.assertEqual("E01", first.code)
        self.assertEqual("E01", second.code)

    def test_update_workstation(self):
        workstation = self._create_workstation(self.lab_10, "E01")

        self.inventory_service.update_workstation(
            workstation,
            {
                "code": "E02",
                "notes": " ",
            },
        )

        self.assertEqual("E02", workstation.code)
        self.assertEqual(1, workstation.map_position_x)
        self.assertEqual(1, workstation.map_position_y)
        self.assertIsNone(workstation.notes)

    def test_update_rejects_duplicate_in_same_laboratory(self):
        self._create_workstation(self.lab_10, "E01")
        workstation = self._create_workstation(self.lab_10, "E02")

        with self.assertRaises(ValueError):
            self.inventory_service.update_workstation(
                workstation,
                {"code": "E01", "map_position_x": "", "map_position_y": "", "notes": ""},
            )

    def test_set_status_hides_from_public_list(self):
        workstation = self._create_workstation(self.lab_10, "E01")

        self.inventory_service.set_workstation_status(workstation, False)

        self.assertFalse(workstation.active)
        self.assertEqual([], self.inventory_service.list_public_workstations_by_laboratory(self.lab_10))

    def test_public_list_returns_empty_for_inactive_laboratory(self):
        self._create_workstation(self.lab_10, "E01")
        self.inventory_service.set_laboratory_status(self.lab_10, False)

        self.assertEqual([], self.inventory_service.list_public_workstations_by_laboratory(self.lab_10))

    def test_get_workstation_not_found(self):
        with self.assertRaises(LookupError):
            self.inventory_service.get_workstation(999)

    def _create_workstation(self, laboratory, code):
        return self.inventory_service.create_workstation(
            laboratory,
            {"code": code, "map_position_x": "", "map_position_y": "", "notes": ""},
        )


if __name__ == "__main__":
    unittest.main()
