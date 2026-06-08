import re
import unittest

from app import create_app
from app.extensions import db
from app.services.inventory_service import InventoryService
from app.services.usuario_service import UsuarioService


class LaboratoryFlowTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        self.inventory_service = InventoryService()
        self.usuario_service = UsuarioService()
        self.professor = self.usuario_service.cadastrar_usuario(
            {
                "nome": "Professor IFRS",
                "email": "professor@ifrs.edu.br",
                "senha": "SenhaTeste123",
                "perfil": "PROFESSOR",
            }
        )
        self.technician = self.usuario_service.cadastrar_usuario(
            {
                "nome": "Tecnico IFRS",
                "email": "tecnico@ifrs.edu.br",
                "senha": "SenhaTeste123",
                "perfil": "TECNICO",
            }
        )
        self.coordinator = self.usuario_service.cadastrar_usuario(
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

    def test_home_public_laboratory_page(self):
        self.inventory_service.create_laboratory(
            {"code": "LAB-10", "name": "Laboratory 10", "pavilion": "Pavilion 10"}
        )

        response = self.client.get("/")

        self.assertEqual(200, response.status_code)
        self.assertIn(b"VITTAL Inventaris", response.data)
        self.assertIn(b"LAB-10", response.data)

    def test_public_laboratories_only_show_active_labs(self):
        active = self.inventory_service.create_laboratory(
            {"code": "LAB-10", "name": "Laboratory 10", "pavilion": "Pavilion 10"}
        )
        inactive = self.inventory_service.create_laboratory(
            {"code": "LAB-11", "name": "Laboratory 11", "pavilion": "Pavilion 11"}
        )
        self.inventory_service.set_laboratory_status(inactive, False)

        response = self.client.get("/public/laboratories")

        self.assertEqual(200, response.status_code)
        self.assertIn(active.code.encode(), response.data)
        self.assertNotIn(inactive.code.encode(), response.data)

    def test_internal_laboratory_list_requires_login(self):
        response = self.client.get("/laboratories")

        self.assertEqual(302, response.status_code)
        self.assertIn("/auth/login", response.headers["Location"])

    def test_professor_can_list_but_cannot_manage_laboratories(self):
        self._login("professor@ifrs.edu.br")

        list_response = self.client.get("/laboratories")
        new_response = self.client.get("/laboratories/new")

        self.assertEqual(200, list_response.status_code)
        self.assertEqual(403, new_response.status_code)

    def test_technician_creates_laboratory(self):
        self._login("tecnico@ifrs.edu.br")
        csrf_token = self._csrf_token_from("/laboratories/new")

        response = self.client.post(
            "/laboratories/new",
            data={
                "code": "LAB-10",
                "name": "Laboratory 10",
                "pavilion": "Pavilion 10",
                "notes": "Created by test",
                "csrf_token": csrf_token,
            },
            follow_redirects=True,
        )

        self.assertEqual(200, response.status_code)
        self.assertIn(b"Laboratory created successfully", response.data)
        self.assertIn(b"LAB-10", response.data)

    def test_coordinator_creates_laboratory(self):
        self._login("coordenador@ifrs.edu.br")
        csrf_token = self._csrf_token_from("/laboratories/new")

        response = self.client.post(
            "/laboratories/new",
            data={
                "code": "LAB-20",
                "name": "Laboratory 20",
                "pavilion": "Pavilion 20",
                "csrf_token": csrf_token,
            },
            follow_redirects=True,
        )

        self.assertEqual(200, response.status_code)
        self.assertIn(b"LAB-20", response.data)

    def test_duplicate_laboratory_code_returns_400(self):
        self.inventory_service.create_laboratory(
            {"code": "LAB-10", "name": "Laboratory 10", "pavilion": "Pavilion 10"}
        )
        self._login("tecnico@ifrs.edu.br")
        csrf_token = self._csrf_token_from("/laboratories/new")

        response = self.client.post(
            "/laboratories/new",
            data={
                "code": "lab-10",
                "name": "Duplicate",
                "pavilion": "Pavilion 10",
                "csrf_token": csrf_token,
            },
        )

        self.assertEqual(400, response.status_code)
        self.assertIn(b"Laboratory code already exists.", response.data)

    def test_technician_updates_laboratory(self):
        laboratory = self.inventory_service.create_laboratory(
            {"code": "LAB-10", "name": "Laboratory 10", "pavilion": "Pavilion 10"}
        )
        self._login("tecnico@ifrs.edu.br")
        csrf_token = self._csrf_token_from(f"/laboratories/{laboratory.id}/edit")

        response = self.client.post(
            f"/laboratories/{laboratory.id}/edit",
            data={
                "code": "LAB-10A",
                "name": "Updated Laboratory",
                "pavilion": "Pavilion 10",
                "notes": "Updated",
                "csrf_token": csrf_token,
            },
            follow_redirects=True,
        )

        self.assertEqual(200, response.status_code)
        self.assertIn(b"Laboratory updated successfully.", response.data)
        self.assertIn(b"LAB-10A", response.data)

    def test_technician_deactivates_and_reactivates_laboratory(self):
        laboratory = self.inventory_service.create_laboratory(
            {"code": "LAB-10", "name": "Laboratory 10", "pavilion": "Pavilion 10"}
        )
        self._login("tecnico@ifrs.edu.br")
        csrf_token = self._csrf_token_from("/laboratories")

        deactivate_response = self.client.post(
            f"/laboratories/{laboratory.id}/status",
            data={"active": "false", "csrf_token": csrf_token},
            follow_redirects=True,
        )
        public_response = self.client.get("/")

        csrf_token = self._csrf_token_from("/laboratories")
        reactivate_response = self.client.post(
            f"/laboratories/{laboratory.id}/status",
            data={"active": "true", "csrf_token": csrf_token},
            follow_redirects=True,
        )

        self.assertEqual(200, deactivate_response.status_code)
        self.assertIn(b"Inactive", deactivate_response.data)
        self.assertNotIn(b"LAB-10", public_response.data)
        self.assertEqual(200, reactivate_response.status_code)
        self.assertIn(b"Active", reactivate_response.data)

    def test_internal_laboratory_map_requires_authenticated_user(self):
        laboratory = self.inventory_service.create_laboratory(
            {"code": "LAB-10", "name": "Laboratory 10", "pavilion": "Pavilion 10"}
        )

        anonymous_response = self.client.get(f"/laboratories/{laboratory.id}/map")
        self._login("professor@ifrs.edu.br")
        professor_response = self.client.get(f"/laboratories/{laboratory.id}/map")

        self.assertEqual(302, anonymous_response.status_code)
        self.assertEqual(200, professor_response.status_code)
        self.assertIn(b"Internal laboratory map.", professor_response.data)

    def _login(self, email: str):
        csrf_token = self._csrf_token_from("/auth/login")
        return self.client.post(
            "/auth/login",
            data={
                "email": email,
                "senha": "SenhaTeste123",
                "csrf_token": csrf_token,
            },
        )

    def _csrf_token_from(self, path: str) -> str:
        response = self.client.get(path)
        self.assertEqual(200, response.status_code)
        match = re.search(rb'name="csrf_token" value="([^"]+)"', response.data)
        self.assertIsNotNone(match)
        return match.group(1).decode("utf-8")


if __name__ == "__main__":
    unittest.main()
