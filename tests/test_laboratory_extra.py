import re
import unittest

from app import create_app
from app.extensions import db
from app.services.inventory_service import InventoryService
from app.services.usuario_service import UsuarioService


class LaboratoryExtraQaTestCase(unittest.TestCase):
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
                "nome": "Professor QA",
                "email": "professor.qa@ifrs.edu.br",
                "senha": "SenhaTeste123",
                "perfil": "PROFESSOR",
            }
        )
        self.usuario_service.cadastrar_usuario(
            {
                "nome": "Tecnico QA",
                "email": "tecnico.qa@ifrs.edu.br",
                "senha": "SenhaTeste123",
                "perfil": "TECNICO",
            }
        )

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_laboratory_mutations_require_csrf(self):
        laboratory = self._create_laboratory("QA-CSRF")
        self._login("tecnico.qa@ifrs.edu.br")

        create_response = self.client.post(
            "/laboratories/new",
            data={"code": "QA-NO-CSRF", "name": "No CSRF", "pavilion": "P10"},
        )
        update_response = self.client.post(
            f"/laboratories/{laboratory.id}/edit",
            data={"code": "QA-CSRF-2", "name": "No CSRF", "pavilion": "P10"},
        )
        status_response = self.client.post(
            f"/laboratories/{laboratory.id}/status",
            data={"active": "false"},
        )

        self.assertEqual(400, create_response.status_code)
        self.assertEqual(400, update_response.status_code)
        self.assertEqual(400, status_response.status_code)

    def test_professor_cannot_post_laboratory_mutations(self):
        laboratory = self._create_laboratory("QA-PROF")
        self._login("professor.qa@ifrs.edu.br")
        csrf_token = self._csrf_token_from("/laboratories")

        create_response = self.client.post(
            "/laboratories/new",
            data={
                "code": "QA-BLOCK",
                "name": "Blocked",
                "pavilion": "P10",
                "csrf_token": csrf_token,
            },
        )
        update_response = self.client.post(
            f"/laboratories/{laboratory.id}/edit",
            data={
                "code": "QA-BLOCK-2",
                "name": "Blocked",
                "pavilion": "P10",
                "csrf_token": csrf_token,
            },
        )
        status_response = self.client.post(
            f"/laboratories/{laboratory.id}/status",
            data={"active": "false", "csrf_token": csrf_token},
        )

        self.assertEqual(403, create_response.status_code)
        self.assertEqual(403, update_response.status_code)
        self.assertEqual(403, status_response.status_code)

    def test_create_laboratory_rejects_blank_required_fields(self):
        self._login("tecnico.qa@ifrs.edu.br")
        csrf_token = self._csrf_token_from("/laboratories/new")

        response = self.client.post(
            "/laboratories/new",
            data={"code": " ", "name": " ", "pavilion": " ", "csrf_token": csrf_token},
        )

        self.assertEqual(400, response.status_code)
        self.assertIn(b"Code is required.", response.data)
        self.assertEqual([], self.inventory_service.list_laboratories())

    def test_missing_laboratory_routes_return_404_for_authenticated_user(self):
        self._login("tecnico.qa@ifrs.edu.br")

        edit_response = self.client.get("/laboratories/999/edit")
        map_response = self.client.get("/laboratories/999/map")

        self.assertEqual(404, edit_response.status_code)
        self.assertEqual(404, map_response.status_code)

    def test_internal_list_keeps_inactive_laboratory_visible(self):
        laboratory = self._create_laboratory("QA-INACTIVE")
        self.inventory_service.set_laboratory_status(laboratory, False)
        self._login("tecnico.qa@ifrs.edu.br")

        internal_response = self.client.get("/laboratories")
        public_response = self.client.get("/")

        self.assertEqual(200, internal_response.status_code)
        self.assertIn(b"QA-INACTIVE", internal_response.data)
        self.assertIn(b"Inactive", internal_response.data)
        self.assertNotIn(b"QA-INACTIVE", public_response.data)

    def test_update_laboratory_normalizes_code_and_notes(self):
        laboratory = self._create_laboratory("QA-NORM")
        self._login("tecnico.qa@ifrs.edu.br")
        csrf_token = self._csrf_token_from(f"/laboratories/{laboratory.id}/edit")

        response = self.client.post(
            f"/laboratories/{laboratory.id}/edit",
            data={
                "code": " qa-norm-2 ",
                "name": " Laboratory Normalized ",
                "pavilion": " Pavilion QA ",
                "notes": " ",
                "csrf_token": csrf_token,
            },
            follow_redirects=True,
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual("QA-NORM-2", laboratory.code)
        self.assertEqual("Laboratory Normalized", laboratory.name)
        self.assertEqual("Pavilion QA", laboratory.pavilion)
        self.assertIsNone(laboratory.notes)

    def _create_laboratory(self, code):
        return self.inventory_service.create_laboratory(
            {"code": code, "name": f"{code} name", "pavilion": "Pavilion QA"}
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
