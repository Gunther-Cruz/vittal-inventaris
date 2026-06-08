import re
import unittest

from app import create_app
from app.extensions import db
from app.services.inventory_service import InventoryService
from app.services.usuario_service import UsuarioService


class WorkstationExtraQaTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        self.inventory_service = InventoryService()
        self.usuario_service = UsuarioService()
        self.laboratory = self.inventory_service.create_laboratory(
            {"code": "QA-LAB", "name": "QA Lab", "pavilion": "P10"}
        )
        self.usuario_service.cadastrar_usuario(
            {
                "nome": "Professor QA",
                "email": "professor.ws.qa@ifrs.edu.br",
                "senha": "SenhaTeste123",
                "perfil": "PROFESSOR",
            }
        )
        self.usuario_service.cadastrar_usuario(
            {
                "nome": "Tecnico QA",
                "email": "tecnico.ws.qa@ifrs.edu.br",
                "senha": "SenhaTeste123",
                "perfil": "TECNICO",
            }
        )

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_workstation_mutations_require_csrf(self):
        workstation = self._create_workstation("E01")
        self._login("tecnico.ws.qa@ifrs.edu.br")

        create_response = self.client.post(
            f"/laboratories/{self.laboratory.id}/workstations/new",
            data={"code": "E02"},
        )
        update_response = self.client.post(
            f"/workstations/{workstation.id}/edit",
            data={"code": "E03"},
        )
        status_response = self.client.post(
            f"/workstations/{workstation.id}/status",
            data={"active": "false"},
        )

        self.assertEqual(400, create_response.status_code)
        self.assertEqual(400, update_response.status_code)
        self.assertEqual(400, status_response.status_code)

    def test_professor_cannot_post_workstation_mutations(self):
        workstation = self._create_workstation("E01")
        self._login("professor.ws.qa@ifrs.edu.br")
        csrf_token = self._csrf_token_from(f"/laboratories/{self.laboratory.id}/workstations")

        create_response = self.client.post(
            f"/laboratories/{self.laboratory.id}/workstations/new",
            data={"code": "E02", "csrf_token": csrf_token},
        )
        update_response = self.client.post(
            f"/workstations/{workstation.id}/edit",
            data={"code": "E03", "csrf_token": csrf_token},
        )
        status_response = self.client.post(
            f"/workstations/{workstation.id}/status",
            data={"active": "false", "csrf_token": csrf_token},
        )

        self.assertEqual(403, create_response.status_code)
        self.assertEqual(403, update_response.status_code)
        self.assertEqual(403, status_response.status_code)

    def test_create_workstation_rejects_blank_required_fields(self):
        self._login("tecnico.ws.qa@ifrs.edu.br")
        csrf_token = self._csrf_token_from(f"/laboratories/{self.laboratory.id}/workstations/new")

        response = self.client.post(
            f"/laboratories/{self.laboratory.id}/workstations/new",
            data={"code": " ", "csrf_token": csrf_token},
        )

        self.assertEqual(400, response.status_code)
        self.assertIn(b"Code is required.", response.data)

    def test_create_workstation_rejects_non_integer_positions(self):
        self._login("tecnico.ws.qa@ifrs.edu.br")
        csrf_token = self._csrf_token_from(f"/laboratories/{self.laboratory.id}/workstations/new")

        response = self.client.post(
            f"/laboratories/{self.laboratory.id}/workstations/new",
            data={
                "code": "E01",
                "map_position_x": "left",
                "map_position_y": "10",
                "csrf_token": csrf_token,
            },
        )

        self.assertEqual(400, response.status_code)
        self.assertIn(b"Map positions must be integers.", response.data)

    def test_missing_workstation_status_returns_404(self):
        self._login("tecnico.ws.qa@ifrs.edu.br")
        csrf_token = self._csrf_token_from(f"/laboratories/{self.laboratory.id}/workstations/new")

        response = self.client.post(
            "/workstations/999/status",
            data={"active": "false", "csrf_token": csrf_token},
        )

        self.assertEqual(404, response.status_code)

    def _create_workstation(self, code):
        return self.inventory_service.create_workstation(
            self.laboratory,
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
