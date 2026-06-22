import re
import unittest

from app import create_app
from app.extensions import db
from app.services.problem_type_service import ProblemTypeService
from app.services.usuario_service import UsuarioService


class ProblemTypeFlowTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        self.problem_type_service = ProblemTypeService()
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

    def test_problem_type_list_requires_login(self):
        response = self.client.get("/problem-types")

        self.assertEqual(302, response.status_code)
        self.assertIn("/auth/login", response.headers["Location"])

    def test_professor_cannot_access_problem_types(self):
        self._login("professor@ifrs.edu.br")

        response = self.client.get("/problem-types")

        self.assertEqual(403, response.status_code)

    def test_technician_creates_problem_type(self):
        self._login("tecnico@ifrs.edu.br")
        csrf_token = self._csrf_token_from("/problem-types/new")

        response = self.client.post(
            "/problem-types/new",
            data={
                "code": "3010",
                "scope": "COMPUTER_CASE",
                "name": "Falha de energia do gabinete",
                "description": "Created by test",
                "csrf_token": csrf_token,
            },
            follow_redirects=True,
        )

        self.assertEqual(200, response.status_code)
        self.assertIn(b"Problem type created successfully", response.data)
        self.assertIn(b"3010", response.data)

    def test_coordinator_creates_problem_type(self):
        self._login("coordenador@ifrs.edu.br")
        csrf_token = self._csrf_token_from("/problem-types/new")

        response = self.client.post(
            "/problem-types/new",
            data={
                "code": "4110",
                "scope": "MONITOR",
                "name": "Ausencia de imagem",
                "description": "",
                "csrf_token": csrf_token,
            },
            follow_redirects=True,
        )

        self.assertEqual(200, response.status_code)
        self.assertIn(b"4110", response.data)

    def test_create_rejects_invalid_code_scope_pair(self):
        self._login("tecnico@ifrs.edu.br")
        csrf_token = self._csrf_token_from("/problem-types/new")

        response = self.client.post(
            "/problem-types/new",
            data={
                "code": "3010",
                "scope": "MONITOR",
                "name": "Wrong scope",
                "description": "",
                "csrf_token": csrf_token,
            },
        )

        self.assertEqual(400, response.status_code)
        self.assertIn(b"incompatible with scope MONITOR", response.data)

    def test_update_changes_name_and_description_only(self):
        problem_type = self._create_problem_type()
        self._login("tecnico@ifrs.edu.br")
        csrf_token = self._csrf_token_from(f"/problem-types/{problem_type.id}/edit")

        response = self.client.post(
            f"/problem-types/{problem_type.id}/edit",
            data={
                "name": "Falha de inicializacao",
                "description": "Updated by flow",
                "csrf_token": csrf_token,
            },
            follow_redirects=True,
        )

        self.assertEqual(200, response.status_code)
        self.assertIn(b"Problem type updated successfully.", response.data)
        self.assertIn(b"Falha de inicializacao", response.data)

    def test_update_rejects_code_or_scope_payload(self):
        problem_type = self._create_problem_type()
        self._login("tecnico@ifrs.edu.br")
        csrf_token = self._csrf_token_from(f"/problem-types/{problem_type.id}/edit")

        response = self.client.post(
            f"/problem-types/{problem_type.id}/edit",
            data={
                "code": "3020",
                "name": "Invalid edit",
                "description": "",
                "csrf_token": csrf_token,
            },
        )

        self.assertEqual(400, response.status_code)
        self.assertIn(b"code and scope cannot be changed", response.data)

    def test_status_toggle(self):
        problem_type = self._create_problem_type()
        self._login("coordenador@ifrs.edu.br")
        csrf_token = self._csrf_token_from("/problem-types")

        response = self.client.post(
            f"/problem-types/{problem_type.id}/status",
            data={"active": "false", "csrf_token": csrf_token},
            follow_redirects=True,
        )

        self.assertEqual(200, response.status_code)
        self.assertIn(b"Inactive", response.data)

    def test_mutation_requires_csrf(self):
        self._login("tecnico@ifrs.edu.br")

        response = self.client.post(
            "/problem-types/new",
            data={"code": "3010", "scope": "COMPUTER_CASE", "name": "No CSRF"},
        )

        self.assertEqual(400, response.status_code)

    def test_missing_problem_type_returns_404(self):
        self._login("tecnico@ifrs.edu.br")

        response = self.client.get("/problem-types/999/edit")

        self.assertEqual(404, response.status_code)

    def _create_problem_type(self):
        return self.problem_type_service.create_problem_type(
            {
                "code": "3010",
                "scope": "COMPUTER_CASE",
                "name": "Falha de energia do gabinete",
                "description": "Test classification",
            }
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
