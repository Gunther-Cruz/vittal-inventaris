import re
import unittest

from app import create_app
from app.domain.enums import DisplayConnection
from app.extensions import db
from app.services.inventory_service import InventoryService
from app.services.usuario_service import UsuarioService


class MonitorFlowTestCase(unittest.TestCase):
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

    def test_monitor_list_requires_login(self):
        response = self.client.get("/monitors")

        self.assertEqual(302, response.status_code)
        self.assertIn("/auth/login", response.headers["Location"])

    def test_professor_cannot_access_monitor_inventory(self):
        self._login("professor@ifrs.edu.br")

        response = self.client.get("/monitors")

        self.assertEqual(403, response.status_code)

    def test_coordinator_can_view_but_cannot_manage_monitors(self):
        monitor = self._create_monitor()
        self._login("coordenador@ifrs.edu.br")

        list_response = self.client.get("/monitors")
        detail_response = self.client.get(f"/monitors/{monitor.id}")
        new_response = self.client.get("/monitors/new")
        edit_response = self.client.get(f"/monitors/{monitor.id}/edit")
        csrf_token = self._csrf_token_from("/auth/perfil")
        status_response = self.client.post(
            f"/monitors/{monitor.id}/status",
            data={"operational_status": "DESATIVADO", "csrf_token": csrf_token},
        )

        self.assertEqual(200, list_response.status_code)
        self.assertIn(b"MON-001", list_response.data)
        self.assertEqual(200, detail_response.status_code)
        self.assertEqual(403, new_response.status_code)
        self.assertEqual(403, edit_response.status_code)
        self.assertEqual(403, status_response.status_code)

    def test_technician_creates_monitor(self):
        self._login("tecnico@ifrs.edu.br")
        csrf_token = self._csrf_token_from("/monitors/new")

        response = self.client.post(
            "/monitors/new",
            data={**self._monitor_data(), "csrf_token": csrf_token},
            follow_redirects=True,
        )

        self.assertEqual(200, response.status_code)
        self.assertIn(b"Monitor created successfully", response.data)
        self.assertIn(b"MON-001", response.data)

    def test_technician_views_monitor_detail(self):
        monitor = self._create_monitor()
        self._login("tecnico@ifrs.edu.br")

        response = self.client.get(f"/monitors/{monitor.id}")

        self.assertEqual(200, response.status_code)
        self.assertIn(b"E2216H", response.data)
        self.assertIn(b"HDMI", response.data)

    def test_technician_updates_monitor(self):
        monitor = self._create_monitor()
        self._login("tecnico@ifrs.edu.br")
        csrf_token = self._csrf_token_from(f"/monitors/{monitor.id}/edit")

        response = self.client.post(
            f"/monitors/{monitor.id}/edit",
            data={
                **self._monitor_data(asset_tag="MON-002", model="P2219H", display_connection="DISPLAYPORT"),
                "csrf_token": csrf_token,
            },
            follow_redirects=True,
        )

        self.assertEqual(200, response.status_code)
        self.assertIn(b"Monitor updated successfully.", response.data)
        self.assertIn(b"P2219H", response.data)
        self.assertIn(b"DISPLAYPORT", response.data)

    def test_technician_cannot_change_operational_status_directly(self):
        monitor = self._create_monitor()
        self._login("tecnico@ifrs.edu.br")
        csrf_token = self._csrf_token_from("/monitors")

        response = self.client.post(
            f"/monitors/{monitor.id}/status",
            data={"operational_status": "DESATIVADO", "csrf_token": csrf_token},
            follow_redirects=True,
        )

        self.assertEqual(200, response.status_code)
        self.assertIn(b"Asset status must be changed through assignment", response.data)

    def test_duplicate_asset_tag_returns_400(self):
        self._create_monitor()
        self._login("tecnico@ifrs.edu.br")
        csrf_token = self._csrf_token_from("/monitors/new")

        response = self.client.post(
            "/monitors/new",
            data={**self._monitor_data(asset_tag="mon-001", serial_number="MSN-002"), "csrf_token": csrf_token},
        )

        self.assertEqual(400, response.status_code)
        self.assertIn(b"Asset tag already exists.", response.data)

    def test_invalid_display_connection_returns_400_on_create(self):
        self._login("tecnico@ifrs.edu.br")
        csrf_token = self._csrf_token_from("/monitors/new")

        response = self.client.post(
            "/monitors/new",
            data={**self._monitor_data(display_connection="SCART"), "csrf_token": csrf_token},
        )

        self.assertEqual(400, response.status_code)
        self.assertIn(b"Invalid display connection.", response.data)

    def test_mutation_requires_csrf(self):
        self._login("tecnico@ifrs.edu.br")

        response = self.client.post("/monitors/new", data=self._monitor_data())

        self.assertEqual(400, response.status_code)

    def test_missing_monitor_returns_404(self):
        self._login("tecnico@ifrs.edu.br")

        response = self.client.get("/monitors/999")

        self.assertEqual(404, response.status_code)

    def _create_monitor(self):
        return self.inventory_service.create_monitor(self._monitor_data())

    def _monitor_data(self, **overrides):
        data = {
            "asset_tag": "MON-001",
            "serial_number": "MSN-001",
            "manufacturer": "Dell",
            "model": "E2216H",
            "purchase_date": "2022-03-15",
            "screen_size_inches": "21.50",
            "display_connection": "HDMI",
            "notes": "Initial monitor collection",
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
