import re
import unittest

from app import create_app
from app.extensions import db
from app.services.inventory_service import InventoryService
from app.services.usuario_service import UsuarioService


class AssetAllocationFlowTestCase(unittest.TestCase):
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
        self.workstation = self.inventory_service.create_workstation(
            self.laboratory,
            {"code": "E01", "map_position_x": "", "map_position_y": "", "notes": ""},
        )
        self.computer_case = self.inventory_service.create_computer_case(
            {"asset_tag": "PAT-001", "manufacturer": "Dell", "model": "OptiPlex"}
        )
        self.monitor = self.inventory_service.create_monitor(
            {"asset_tag": "MON-001", "manufacturer": "Dell", "model": "E2216H"}
        )
        self.usuario_service.cadastrar_usuario(
            {"nome": "Professor IFRS", "email": "professor@ifrs.edu.br", "senha": "SenhaTeste123", "perfil": "PROFESSOR"}
        )
        self.usuario_service.cadastrar_usuario(
            {"nome": "Tecnico IFRS", "email": "tecnico@ifrs.edu.br", "senha": "SenhaTeste123", "perfil": "TECNICO"}
        )
        self.usuario_service.cadastrar_usuario(
            {"nome": "Coordenador IFRS", "email": "coordenador@ifrs.edu.br", "senha": "SenhaTeste123", "perfil": "COORDENADOR"}
        )

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_assets_page_requires_login(self):
        response = self.client.get(f"/workstations/{self.workstation.id}/assets")

        self.assertEqual(302, response.status_code)
        self.assertIn("/auth/login", response.headers["Location"])

    def test_professor_cannot_access_asset_allocations(self):
        self._login("professor@ifrs.edu.br")

        response = self.client.get(f"/workstations/{self.workstation.id}/assets")

        self.assertEqual(403, response.status_code)

    def test_coordinator_views_but_cannot_assign_assets(self):
        self._login("coordenador@ifrs.edu.br")
        page_response = self.client.get(f"/workstations/{self.workstation.id}/assets")
        csrf_token = self._csrf_token_from("/auth/perfil")
        post_response = self.client.post(
            f"/workstations/{self.workstation.id}/computer-case",
            data={"computer_case_id": self.computer_case.id, "movement_reason": "Install", "csrf_token": csrf_token},
        )

        self.assertEqual(200, page_response.status_code)
        self.assertIn(b"No computer case assigned.", page_response.data)
        self.assertEqual(403, post_response.status_code)

    def test_technician_assigns_and_unassigns_computer_case(self):
        self._login("tecnico@ifrs.edu.br")
        csrf_token = self._csrf_token_from(f"/workstations/{self.workstation.id}/assets")

        assign_response = self.client.post(
            f"/workstations/{self.workstation.id}/computer-case",
            data={
                "computer_case_id": self.computer_case.id,
                "movement_reason": "Initial installation",
                "csrf_token": csrf_token,
            },
            follow_redirects=True,
        )
        csrf_token = self._csrf_token_from(f"/workstations/{self.workstation.id}/assets")
        unassign_response = self.client.post(
            f"/workstations/{self.workstation.id}/computer-case/unassign",
            data={
                "operational_status": "EM_MANUTENCAO",
                "movement_reason": "Removed for assessment",
                "csrf_token": csrf_token,
            },
            follow_redirects=True,
        )

        self.assertEqual(200, assign_response.status_code)
        self.assertIn(b"Computer case assigned successfully.", assign_response.data)
        self.assertIn(b"PAT-001", assign_response.data)
        self.assertEqual(200, unassign_response.status_code)
        self.assertIn(b"Computer case unassigned successfully.", unassign_response.data)
        self.assertIn(b"No computer case assigned.", unassign_response.data)

    def test_technician_assigns_and_unassigns_monitor(self):
        self._login("tecnico@ifrs.edu.br")
        csrf_token = self._csrf_token_from(f"/workstations/{self.workstation.id}/assets")

        assign_response = self.client.post(
            f"/workstations/{self.workstation.id}/monitor",
            data={
                "monitor_id": self.monitor.id,
                "movement_reason": "Initial installation",
                "csrf_token": csrf_token,
            },
            follow_redirects=True,
        )
        csrf_token = self._csrf_token_from(f"/workstations/{self.workstation.id}/assets")
        unassign_response = self.client.post(
            f"/workstations/{self.workstation.id}/monitor/unassign",
            data={
                "operational_status": "FUNCIONAL_DESALOCADO",
                "movement_reason": "Reserve monitor",
                "csrf_token": csrf_token,
            },
            follow_redirects=True,
        )

        self.assertEqual(200, assign_response.status_code)
        self.assertIn(b"Monitor assigned successfully.", assign_response.data)
        self.assertIn(b"MON-001", assign_response.data)
        self.assertEqual(200, unassign_response.status_code)
        self.assertIn(b"Monitor unassigned successfully.", unassign_response.data)
        self.assertIn(b"No monitor assigned.", unassign_response.data)

    def test_assignment_requires_csrf(self):
        self._login("tecnico@ifrs.edu.br")

        response = self.client.post(
            f"/workstations/{self.workstation.id}/computer-case",
            data={"computer_case_id": self.computer_case.id, "movement_reason": "Install"},
        )

        self.assertEqual(400, response.status_code)

    def test_assignment_without_reason_returns_400(self):
        self._login("tecnico@ifrs.edu.br")
        csrf_token = self._csrf_token_from(f"/workstations/{self.workstation.id}/assets")

        response = self.client.post(
            f"/workstations/{self.workstation.id}/computer-case",
            data={"computer_case_id": self.computer_case.id, "movement_reason": "", "csrf_token": csrf_token},
        )

        self.assertEqual(400, response.status_code)
        self.assertIn(b"Movement reason is required.", response.data)

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
