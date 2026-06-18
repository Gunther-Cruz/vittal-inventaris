import unittest

from app import create_app
from app.domain.enums import PerfilUsuario
from app.extensions import db
from app.services.auth_service import AuthService
from app.services.usuario_service import UsuarioService


class UsuarioServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.usuario_service = UsuarioService()
        self.coordenador = self.usuario_service.cadastrar_usuario(
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

    def test_valida_email_institucional_no_cadastro(self):
        with self.assertRaises(ValueError):
            self.usuario_service.cadastrar_usuario(
                {
                    "nome": "Usuario Externo",
                    "email": "externo@example.com",
                    "senha": "SenhaTeste123",
                    "perfil": "PROFESSOR",
                },
                ator=self.coordenador,
            )

    def test_cadastrar_usuario_por_coordenador(self):
        usuario = self.usuario_service.cadastrar_usuario(
            {
                "nome": "Professor IFRS",
                "email": "professor@ifrs.edu.br",
                "senha": "SenhaProfessor123",
                "perfil": "PROFESSOR",
            },
            ator=self.coordenador,
        )

        self.assertEqual(PerfilUsuario.PROFESSOR, usuario.perfil)
        self.assertIsNotNone(AuthService().autenticar("professor@ifrs.edu.br", "SenhaProfessor123"))

    def test_atualizar_usuario(self):
        usuario = self._criar_tecnico()

        self.usuario_service.atualizar_usuario(
            usuario,
            {"nome": "Tecnico Atualizado", "email": "tecnico.atualizado@ifrs.edu.br"},
        )

        self.assertEqual("Tecnico Atualizado", usuario.nome)
        self.assertEqual("tecnico.atualizado@ifrs.edu.br", usuario.email)

    def test_alterar_perfil_status_e_dashboard(self):
        usuario = self._criar_tecnico()

        self.usuario_service.alterar_perfil(usuario, "PROFESSOR")
        self.usuario_service.alterar_status_usuario(usuario, False, ator=self.coordenador)
        self.usuario_service.definir_permissao_dashboard(usuario, True)

        self.assertEqual(PerfilUsuario.PROFESSOR, usuario.perfil)
        self.assertFalse(usuario.ativo)
        self.assertTrue(usuario.pode_visualizar_dashboard)

    def test_usuario_nao_pode_desativar_a_si_mesmo(self):
        with self.assertRaisesRegex(ValueError, "You cannot deactivate your own user."):
            self.usuario_service.alterar_status_usuario(self.coordenador, False, ator=self.coordenador)

        self.assertTrue(self.coordenador.ativo)

    def test_listar_usuarios(self):
        self._criar_tecnico()

        usuarios = self.usuario_service.listar_usuarios()

        self.assertEqual(2, len(usuarios))

    def test_usuario_sem_permissao_nao_cadastra_usuario(self):
        tecnico = self._criar_tecnico()

        with self.assertRaises(PermissionError):
            self.usuario_service.cadastrar_usuario(
                {
                    "nome": "Professor Bloqueado",
                    "email": "professor.bloqueado@ifrs.edu.br",
                    "senha": "SenhaProfessor123",
                    "perfil": "PROFESSOR",
                },
                ator=tecnico,
            )

    def _criar_tecnico(self):
        return self.usuario_service.cadastrar_usuario(
            {
                "nome": "Tecnico IFRS",
                "email": "tecnico@ifrs.edu.br",
                "senha": "SenhaTecnico123",
                "perfil": "TECNICO",
            },
            ator=self.coordenador,
        )


if __name__ == "__main__":
    unittest.main()
