import unittest

from app import create_app
from app.commands.auth_commands import COORDENADOR_INICIAL_EMAIL, COORDENADOR_INICIAL_SENHA
from app.domain.enums import PerfilUsuario
from app.extensions import db
from app.repositories.usuario_repository import UsuarioRepository
from app.services.auth_service import AuthService


class AuthCommandsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.runner = self.app.test_cli_runner()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_criar_usuario_por_cli(self):
        result = self.runner.invoke(
            args=[
                "auth",
                "criar-usuario",
                "--nome",
                "Coordenador IFRS",
                "--email",
                "coord@ifrs.edu.br",
                "--perfil",
                "COORDENADOR",
                "--senha",
                "SenhaTeste123",
            ],
        )

        self.assertEqual(0, result.exit_code, result.output)
        self.assertIn("Usuario criado com sucesso", result.output)

        usuario = UsuarioRepository().buscar_por_email("coord@ifrs.edu.br")
        self.assertIsNotNone(usuario)
        self.assertEqual(PerfilUsuario.COORDENADOR, usuario.perfil)

    def test_cli_nao_permite_usuario_duplicado(self):
        args = [
            "auth",
            "criar-usuario",
            "--nome",
            "Tecnico IFRS",
            "--email",
            "tecnico@ifrs.edu.br",
            "--perfil",
            "TECNICO",
            "--senha",
            "SenhaTeste123",
        ]

        primeiro = self.runner.invoke(args=args)
        segundo = self.runner.invoke(args=args)

        self.assertEqual(0, primeiro.exit_code, primeiro.output)
        self.assertNotEqual(0, segundo.exit_code)
        self.assertIn("Ja existe usuario cadastrado", segundo.output)

    def test_criar_coordenador_inicial_por_cli(self):
        result = self.runner.invoke(args=["auth", "criar-coordenador-inicial"])

        self.assertEqual(0, result.exit_code, result.output)
        self.assertIn("Coordenador inicial criado", result.output)

        usuario = UsuarioRepository().buscar_por_email(COORDENADOR_INICIAL_EMAIL)
        self.assertIsNotNone(usuario)
        self.assertEqual(PerfilUsuario.COORDENADOR, usuario.perfil)
        self.assertIsNotNone(AuthService().autenticar(COORDENADOR_INICIAL_EMAIL, COORDENADOR_INICIAL_SENHA))

    def test_criar_coordenador_inicial_e_idempotente(self):
        primeiro = self.runner.invoke(args=["auth", "criar-coordenador-inicial"])
        segundo = self.runner.invoke(args=["auth", "criar-coordenador-inicial"])

        self.assertEqual(0, primeiro.exit_code, primeiro.output)
        self.assertEqual(0, segundo.exit_code, segundo.output)
        self.assertIn("Coordenador inicial ja existe", segundo.output)


if __name__ == "__main__":
    unittest.main()
