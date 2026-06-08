import re
import unittest

from app import create_app
from app.extensions import db
from app.services.inventory_service import InventoryService
from app.services.usuario_service import UsuarioService


class WorkstationFlowTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        self.inventory_service = InventoryService()
        self.usuario_service = UsuarioService()
        self.laboratory = self.inventory_service.create_laboratory(
            {"code": "LAB-10", "name": "Laboratory 10", "pavilion": "Pavilion 10"}
        )
        self.other_laboratory = self.inventory_service.create_laboratory(
            {"code": "LAB-11", "name": "Laboratory 11", "pavilion": "Pavilion 11"}
        )
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

    def test_public_workstations_page_shows_active_workstations(self):
        active = self._create_workstation(self.laboratory, "E01")
        inactive = self._create_workstation(self.laboratory, "E02")
        self.inventory_service.set_workstation_status(inactive, False)

        response = self.client.get(f"/public/laboratories/{self.laboratory.id}/workstations")

        self.assertEqual(200, response.status_code)
        self.assertIn(active.code.encode(), response.data)
        self.assertNotIn(inactive.code.encode(), response.data)

    def test_public_workstations_for_inactive_laboratory_returns_404(self):
        self.inventory_service.set_laboratory_status(self.laboratory, False)

        response = self.client.get(f"/public/laboratories/{self.laboratory.id}/workstations")

        self.assertEqual(404, response.status_code)

    def test_internal_workstation_list_requires_login(self):
        response = self.client.get(f"/laboratories/{self.laboratory.id}/workstations")

        self.assertEqual(302, response.status_code)
        self.assertIn("/auth/login", response.headers["Location"])

    def test_professor_can_list_but_cannot_manage_workstations(self):
        self._login("professor@ifrs.edu.br")

        list_response = self.client.get(f"/laboratories/{self.laboratory.id}/workstations")
        new_response = self.client.get(f"/laboratories/{self.laboratory.id}/workstations/new")

        self.assertEqual(200, list_response.status_code)
        self.assertEqual(403, new_response.status_code)

    def test_technician_creates_workstation(self):
        self._login("tecnico@ifrs.edu.br")
        csrf_token = self._csrf_token_from(f"/laboratories/{self.laboratory.id}/workstations/new")

        response = self.client.post(
            f"/laboratories/{self.laboratory.id}/workstations/new",
            data={
                "code": "E01",
                "map_position_x": "10",
                "map_position_y": "20",
                "notes": "Created by test",
                "csrf_token": csrf_token,
            },
            follow_redirects=True,
        )

        self.assertEqual(200, response.status_code)
        self.assertIn(b"Workstation created successfully", response.data)
        self.assertIn(b"E01", response.data)

    def test_coordinator_creates_workstation(self):
        self._login("coordenador@ifrs.edu.br")
        csrf_token = self._csrf_token_from(f"/laboratories/{self.laboratory.id}/workstations/new")

        response = self.client.post(
            f"/laboratories/{self.laboratory.id}/workstations/new",
            data={
                "code": "E03",
                "map_position_x": "",
                "map_position_y": "",
                "csrf_token": csrf_token,
            },
            follow_redirects=True,
        )

        self.assertEqual(200, response.status_code)
        self.assertIn(b"E03", response.data)

    def test_duplicate_workstation_code_in_same_laboratory_returns_400(self):
        self._create_workstation(self.laboratory, "E01")
        self._login("tecnico@ifrs.edu.br")
        csrf_token = self._csrf_token_from(f"/laboratories/{self.laboratory.id}/workstations/new")

        response = self.client.post(
            f"/laboratories/{self.laboratory.id}/workstations/new",
            data={"code": "e01", "csrf_token": csrf_token},
        )

        self.assertEqual(400, response.status_code)
        self.assertIn(b"Workstation code already exists in this laboratory.", response.data)

    def test_same_workstation_code_in_different_laboratory_is_allowed(self):
        self._create_workstation(self.laboratory, "E01")
        self._login("tecnico@ifrs.edu.br")
        csrf_token = self._csrf_token_from(f"/laboratories/{self.other_laboratory.id}/workstations/new")

        response = self.client.post(
            f"/laboratories/{self.other_laboratory.id}/workstations/new",
            data={"code": "E01", "csrf_token": csrf_token},
            follow_redirects=True,
        )

        self.assertEqual(200, response.status_code)
        self.assertIn(b"E01", response.data)

    def test_technician_updates_workstation(self):
        workstation = self._create_workstation(self.laboratory, "E01")
        self._login("tecnico@ifrs.edu.br")
        csrf_token = self._csrf_token_from(f"/workstations/{workstation.id}/edit")

        response = self.client.post(
            f"/workstations/{workstation.id}/edit",
            data={
                "code": "E02",
                "map_position_x": "30",
                "map_position_y": "40",
                "notes": "Updated",
                "csrf_token": csrf_token,
            },
            follow_redirects=True,
        )

        self.assertEqual(200, response.status_code)
        self.assertIn(b"Workstation updated successfully.", response.data)
        self.assertIn(b"E02", response.data)

    def test_technician_deactivates_and_reactivates_workstation(self):
        workstation = self._create_workstation(self.laboratory, "E01")
        self._login("tecnico@ifrs.edu.br")
        csrf_token = self._csrf_token_from(f"/laboratories/{self.laboratory.id}/workstations")

        deactivate_response = self.client.post(
            f"/workstations/{workstation.id}/status",
            data={"active": "false", "csrf_token": csrf_token},
            follow_redirects=True,
        )
        public_response = self.client.get(f"/public/laboratories/{self.laboratory.id}/workstations")

        csrf_token = self._csrf_token_from(f"/laboratories/{self.laboratory.id}/workstations")
        reactivate_response = self.client.post(
            f"/workstations/{workstation.id}/status",
            data={"active": "true", "csrf_token": csrf_token},
            follow_redirects=True,
        )

        self.assertEqual(200, deactivate_response.status_code)
        self.assertIn(b"Inactive", deactivate_response.data)
        self.assertNotIn(b"E01", public_response.data)
        self.assertEqual(200, reactivate_response.status_code)
        self.assertIn(b"Active", reactivate_response.data)

    def test_internal_laboratory_map_shows_workstations(self):
        self._create_workstation(self.laboratory, "E01")
        self._login("professor@ifrs.edu.br")

        response = self.client.get(f"/laboratories/{self.laboratory.id}/map")

        self.assertEqual(200, response.status_code)
        self.assertIn(b"E01", response.data)
        self.assertIn(b"Internal laboratory map.", response.data)

    def test_missing_workstation_routes_return_404(self):
        self._login("tecnico@ifrs.edu.br")

        response = self.client.get("/workstations/999/edit")

        self.assertEqual(404, response.status_code)

    def _create_workstation(self, laboratory, code):
        return self.inventory_service.create_workstation(
            laboratory,
            {"code": code, "map_position_x": "", "map_position_y": "", "notes": ""},
        )

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
