import unittest

from app import create_app
from app.extensions import db
from app.services.inventory_service import InventoryService


class LaboratoryServiceTestCase(unittest.TestCase):
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

    def test_create_laboratory_normalizes_code(self):
        laboratory = self.inventory_service.create_laboratory(
            {
                "code": " lab-10 ",
                "name": "Laboratory 10",
                "pavilion": "Pavilion 10",
                "notes": "Initial lab",
            }
        )

        self.assertIsNotNone(laboratory.id)
        self.assertEqual("LAB-10", laboratory.code)
        self.assertEqual("Laboratory 10", laboratory.name)
        self.assertTrue(laboratory.active)

    def test_create_laboratory_requires_unique_code(self):
        self._create_laboratory("LAB-10")

        with self.assertRaises(ValueError):
            self._create_laboratory("lab-10")

    def test_update_laboratory(self):
        laboratory = self._create_laboratory("LAB-10")

        self.inventory_service.update_laboratory(
            laboratory,
            {
                "code": "LAB-11",
                "name": "Updated laboratory",
                "pavilion": "Pavilion 11",
                "notes": "",
            },
        )

        self.assertEqual("LAB-11", laboratory.code)
        self.assertEqual("Updated laboratory", laboratory.name)
        self.assertEqual("Pavilion 11", laboratory.pavilion)
        self.assertIsNone(laboratory.notes)

    def test_update_laboratory_rejects_duplicate_code(self):
        self._create_laboratory("LAB-10")
        laboratory = self._create_laboratory("LAB-11")

        with self.assertRaises(ValueError):
            self.inventory_service.update_laboratory(
                laboratory,
                {
                    "code": "LAB-10",
                    "name": "Duplicate",
                    "pavilion": "Pavilion 10",
                    "notes": "",
                },
            )

    def test_set_laboratory_status(self):
        laboratory = self._create_laboratory("LAB-10")

        self.inventory_service.set_laboratory_status(laboratory, False)

        self.assertFalse(laboratory.active)
        self.assertEqual([], self.inventory_service.list_public_laboratories())

    def test_list_laboratories(self):
        self._create_laboratory("LAB-11")
        self._create_laboratory("LAB-10")

        laboratories = self.inventory_service.list_laboratories()

        self.assertEqual(["LAB-10", "LAB-11"], [laboratory.code for laboratory in laboratories])

    def test_get_laboratory_not_found(self):
        with self.assertRaises(LookupError):
            self.inventory_service.get_laboratory(999)

    def _create_laboratory(self, code):
        return self.inventory_service.create_laboratory(
            {
                "code": code,
                "name": f"{code} name",
                "pavilion": "Pavilion 10",
                "notes": "",
            }
        )


if __name__ == "__main__":
    unittest.main()
