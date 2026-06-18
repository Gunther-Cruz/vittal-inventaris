import re
import unittest

from app import create_app
from app.extensions import db
from app.services.inventory_service import InventoryService
from app.services.usuario_service import UsuarioService


class ComputerCaseFlowTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        self.inventory_service = InventoryService()
        self.usuario_service = UsuarioService()
        self.usuario_service.cadastrar_usuario(
            {
                "nome": "Professor IFRS",
                "email": "professor@ifrs.edu.br",
                "senha": "SenhaTeste123",
                "perfil": "PROFESSOR",
            }
        )
        self.usuario_service.cadastrar_usuario(
            {
                "nome": "Tecnico IFRS",
                "email": "tecnico@ifrs.edu.br",
                "senha": "SenhaTeste123",
                "perfil": "TECNICO",
            }
        )
        self.usuario_service.cadastrar_usuario(
            {
                "nome": "Coordenador IFRS",
                "email": "coordenador@ifrs.edu.br",
                "senha": "SenhaTeste123",
                "perfil": "COORDENADOR",
            }
        )

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_computer_case_list_requires_login(self):
        response = self.client.get("/computer-cases")

        self.assertEqual(302, response.status_code)
        self.assertIn("/auth/login", response.headers["Location"])

    def test_professor_cannot_access_computer_case_inventory(self):
        self._login("professor@ifrs.edu.br")

        response = self.client.get("/computer-cases")

        self.assertEqual(403, response.status_code)

    def test_coordinator_can_view_but_cannot_manage_computer_cases(self):
        computer_case = self._create_computer_case()
        self._login("coordenador@ifrs.edu.br")

        list_response = self.client.get("/computer-cases")
        detail_response = self.client.get(f"/computer-cases/{computer_case.id}")
        new_response = self.client.get("/computer-cases/new")
        edit_response = self.client.get(f"/computer-cases/{computer_case.id}/edit")
        csrf_token = self._csrf_token_from("/auth/perfil")
        status_response = self.client.post(
            f"/computer-cases/{computer_case.id}/status",
            data={"operational_status": "DESATIVADO", "csrf_token": csrf_token},
        )

        self.assertEqual(200, list_response.status_code)
        self.assertIn(b"PAT-001", list_response.data)
        self.assertEqual(200, detail_response.status_code)
        self.assertEqual(403, new_response.status_code)
        self.assertEqual(403, edit_response.status_code)
        self.assertEqual(403, status_response.status_code)

    def test_technician_creates_computer_case(self):
        self._login("tecnico@ifrs.edu.br")
        csrf_token = self._csrf_token_from("/computer-cases/new")

        response = self.client.post(
            "/computer-cases/new",
            data={**self._computer_case_data(), "csrf_token": csrf_token},
            follow_redirects=True,
        )

        self.assertEqual(200, response.status_code)
        self.assertIn(b"Computer case created successfully", response.data)
        self.assertIn(b"PAT-001", response.data)

    def test_technician_views_computer_case_detail(self):
        computer_case = self._create_computer_case()
        self._login("tecnico@ifrs.edu.br")

        response = self.client.get(f"/computer-cases/{computer_case.id}")

        self.assertEqual(200, response.status_code)
        self.assertIn(b"OptiPlex 3040", response.data)
        self.assertIn(b"Ubuntu MATE 22.04", response.data)

    def test_technician_updates_computer_case(self):
        computer_case = self._create_computer_case()
        self._login("tecnico@ifrs.edu.br")
        csrf_token = self._csrf_token_from(f"/computer-cases/{computer_case.id}/edit")

        response = self.client.post(
            f"/computer-cases/{computer_case.id}/edit",
            data={
                **self._computer_case_data(asset_tag="PAT-002", model="OptiPlex 7050"),
                "csrf_token": csrf_token,
            },
            follow_redirects=True,
        )

        self.assertEqual(200, response.status_code)
        self.assertIn(b"Computer case updated successfully.", response.data)
        self.assertIn(b"OptiPlex 7050", response.data)

    def test_technician_cannot_change_operational_status_directly(self):
        computer_case = self._create_computer_case()
        self._login("tecnico@ifrs.edu.br")
        csrf_token = self._csrf_token_from("/computer-cases")

        response = self.client.post(
            f"/computer-cases/{computer_case.id}/status",
            data={"operational_status": "DESATIVADO", "csrf_token": csrf_token},
            follow_redirects=True,
        )

        self.assertEqual(200, response.status_code)
        self.assertIn(b"Asset status must be changed through assignment", response.data)

    def test_duplicate_asset_tag_returns_400(self):
        self._create_computer_case()
        self._login("tecnico@ifrs.edu.br")
        csrf_token = self._csrf_token_from("/computer-cases/new")

        response = self.client.post(
            "/computer-cases/new",
            data={
                **self._computer_case_data(asset_tag="pat-001", serial_number="SN-002"),
                "csrf_token": csrf_token,
            },
        )

        self.assertEqual(400, response.status_code)
        self.assertIn(b"Asset tag already exists.", response.data)

    def test_manual_status_returns_400_on_create(self):
        self._login("tecnico@ifrs.edu.br")
        csrf_token = self._csrf_token_from("/computer-cases/new")

        response = self.client.post(
            "/computer-cases/new",
            data={**self._computer_case_data(operational_status="QUEBRADO"), "csrf_token": csrf_token},
        )

        self.assertEqual(400, response.status_code)
        self.assertIn(b"Asset status must be changed through assignment", response.data)

    def test_mutation_requires_csrf(self):
        self._login("tecnico@ifrs.edu.br")

        response = self.client.post("/computer-cases/new", data=self._computer_case_data())

        self.assertEqual(400, response.status_code)

    def test_missing_computer_case_returns_404(self):
        self._login("tecnico@ifrs.edu.br")

        response = self.client.get("/computer-cases/999")

        self.assertEqual(404, response.status_code)

    def _create_computer_case(self):
        return self.inventory_service.create_computer_case(self._computer_case_data())

    def _computer_case_data(self, **overrides):
        data = {
            "asset_tag": "PAT-001",
            "serial_number": "SN-001",
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
            "notes": "Initial technical collection",
        }
        data.update(overrides)
        return data

    def _login(self, email: str):
        csrf_token = self._csrf_token_from("/auth/login")
        return self.client.post(
            "/auth/login",
            data={"email": email, "senha": "SenhaTeste123", "csrf_token": csrf_token},
        )

    def _csrf_token_from(self, path: str) -> str:
        response = self.client.get(path)
        self.assertEqual(200, response.status_code)
        match = re.search(rb'name="csrf_token" value="([^"]+)"', response.data)
        self.assertIsNotNone(match)
        return match.group(1).decode("utf-8")


if __name__ == "__main__":
    unittest.main()
