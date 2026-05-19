import re
import unittest

from app import create_app
from app.extensions import db
from app.services.auth_service import AuthService


class AuthFlowTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        self.auth_service = AuthService()
        self.auth_service.registrar_usuario(
            nome="Professor IFRS",
            email="professor@ifrs.edu.br",
            senha="SenhaTeste123",
            perfil="PROFESSOR",
        )
        self.auth_service.registrar_usuario(
            nome="Tecnico IFRS",
            email="tecnico@ifrs.edu.br",
            senha="SenhaTeste123",
            perfil="TECNICO",
        )
        self.auth_service.registrar_usuario(
            nome="Coordenador IFRS",
            email="coordenador@ifrs.edu.br",
            senha="SenhaTeste123",
            perfil="COORDENADOR",
        )

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_rota_protegida_redireciona_para_login(self):
        response = self.client.get("/auth/perfil")

        self.assertEqual(302, response.status_code)
        self.assertIn("/auth/login", response.headers["Location"])

    def test_login_exige_csrf(self):
        response = self.client.post(
            "/auth/login",
            data={"email": "professor@ifrs.edu.br", "senha": "SenhaTeste123"},
        )

        self.assertEqual(400, response.status_code)

    def test_login_logout_com_sessao(self):
        csrf_token = self._csrf_token_from("/auth/login")
        login_response = self.client.post(
            "/auth/login",
            data={
                "email": "professor@ifrs.edu.br",
                "senha": "SenhaTeste123",
                "csrf_token": csrf_token,
            },
            follow_redirects=True,
        )

        self.assertEqual(200, login_response.status_code)
        self.assertIn(b"Area autenticada", login_response.data)
        self.assertIn(b"professor@ifrs.edu.br", login_response.data)

        csrf_token = self._csrf_token_from("/auth/perfil")
        logout_response = self.client.post(
            "/auth/logout",
            data={"csrf_token": csrf_token},
            follow_redirects=False,
        )

        self.assertEqual(302, logout_response.status_code)
        perfil_response = self.client.get("/auth/perfil")
        self.assertEqual(302, perfil_response.status_code)

    def test_credenciais_invalidas_nao_autenticam(self):
        csrf_token = self._csrf_token_from("/auth/login")
        response = self.client.post(
            "/auth/login",
            data={
                "email": "professor@ifrs.edu.br",
                "senha": "senha-errada",
                "csrf_token": csrf_token,
            },
        )

        self.assertEqual(401, response.status_code)
        self.assertIn(b"Email ou senha invalidos.", response.data)

    def test_controle_de_acesso_por_perfil(self):
        csrf_token = self._csrf_token_from("/auth/login")
        self.client.post(
            "/auth/login",
            data={
                "email": "professor@ifrs.edu.br",
                "senha": "SenhaTeste123",
                "csrf_token": csrf_token,
            },
        )

        response = self.client.get("/auth/area-tecnica")
        self.assertEqual(403, response.status_code)

    def test_tecnico_acessa_area_tecnica(self):
        self._login("tecnico@ifrs.edu.br")

        response = self.client.get("/auth/area-tecnica")
        self.assertEqual(200, response.status_code)
        self.assertIn(b"Area tecnica", response.data)

    def test_login_nao_redireciona_para_url_externa(self):
        csrf_token = self._csrf_token_from("/auth/login?next=https://example.com")
        response = self.client.post(
            "/auth/login?next=https://example.com",
            data={
                "email": "tecnico@ifrs.edu.br",
                "senha": "SenhaTeste123",
                "csrf_token": csrf_token,
            },
        )

        self.assertEqual(302, response.status_code)
        self.assertIn("/auth/perfil", response.headers["Location"])
        self.assertNotIn("example.com", response.headers["Location"])

    def test_coordenador_cria_usuario_pela_interface(self):
        self._login("coordenador@ifrs.edu.br")
        csrf_token = self._csrf_token_from("/usuarios/novo")

        response = self.client.post(
            "/usuarios/novo",
            data={
                "nome": "Novo Professor",
                "email": "novo.professor@ifrs.edu.br",
                "perfil": "PROFESSOR",
                "senha": "SenhaProfessor123",
                "csrf_token": csrf_token,
            },
            follow_redirects=True,
        )

        self.assertEqual(200, response.status_code)
        self.assertIn(b"Usuario criado com sucesso", response.data)
        self.assertIsNotNone(self.auth_service.autenticar("novo.professor@ifrs.edu.br", "SenhaProfessor123"))

    def test_usuario_sem_permissao_nao_acessa_criacao(self):
        self._login("tecnico@ifrs.edu.br")

        response = self.client.get("/usuarios/novo")

        self.assertEqual(403, response.status_code)

    def test_nao_cria_perfil_aluno_pela_interface(self):
        self._login("coordenador@ifrs.edu.br")
        csrf_token = self._csrf_token_from("/usuarios/novo")

        response = self.client.post(
            "/usuarios/novo",
            data={
                "nome": "Aluno Indevido",
                "email": "aluno@ifrs.edu.br",
                "perfil": "ALUNO",
                "senha": "SenhaAluno123",
                "csrf_token": csrf_token,
            },
        )

        self.assertEqual(400, response.status_code)
        self.assertIn(b"Perfil de usuario invalido.", response.data)
        self.assertIsNone(self.auth_service.autenticar("aluno@ifrs.edu.br", "SenhaAluno123"))

    def test_fluxo_completo_cria_usuario_logout_e_login_com_usuario_criado(self):
        self._login("coordenador@ifrs.edu.br")
        csrf_token = self._csrf_token_from("/usuarios/novo")
        response = self.client.post(
            "/usuarios/novo",
            data={
                "nome": "Tecnico Novo",
                "email": "tecnico.novo@ifrs.edu.br",
                "perfil": "TECNICO",
                "senha": "SenhaTecnico123",
                "csrf_token": csrf_token,
            },
            follow_redirects=True,
        )
        self.assertEqual(200, response.status_code)

        csrf_token = self._csrf_token_from("/auth/perfil")
        logout_response = self.client.post("/auth/logout", data={"csrf_token": csrf_token})
        self.assertEqual(302, logout_response.status_code)

        login_response = self._login("tecnico.novo@ifrs.edu.br", senha="SenhaTecnico123", follow_redirects=True)
        self.assertEqual(200, login_response.status_code)
        self.assertIn(b"tecnico.novo@ifrs.edu.br", login_response.data)

    def _login(self, email: str, senha: str = "SenhaTeste123", follow_redirects: bool = False):
        csrf_token = self._csrf_token_from("/auth/login")
        return self.client.post(
            "/auth/login",
            data={
                "email": email,
                "senha": senha,
                "csrf_token": csrf_token,
            },
            follow_redirects=follow_redirects,
        )

    def _csrf_token_from(self, path: str) -> str:
        response = self.client.get(path)
        self.assertEqual(200, response.status_code)
        match = re.search(rb'name="csrf_token" value="([^"]+)"', response.data)
        self.assertIsNotNone(match)
        return match.group(1).decode("utf-8")


if __name__ == "__main__":
    unittest.main()
