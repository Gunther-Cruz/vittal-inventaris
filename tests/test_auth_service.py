import unittest

from app import create_app
from app.domain.enums import PerfilUsuario
from app.extensions import db
from app.services.auth_service import AuthService


class AuthServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_hash_senha_nao_armazena_texto_puro(self):
        senha_hash = AuthService.gerar_hash_senha("SenhaTeste123")

        self.assertNotEqual("SenhaTeste123", senha_hash)
        self.assertTrue(AuthService.verificar_senha("SenhaTeste123", senha_hash))
        self.assertFalse(AuthService.verificar_senha("senha-errada", senha_hash))

    def test_registrar_usuario_com_perfil_valido(self):
        usuario = AuthService().registrar_usuario(
            nome="Tecnico IFRS",
            email="TECNICO@IFRS.EDU.BR",
            senha="SenhaTeste123",
            perfil="TECNICO",
        )

        self.assertIsNotNone(usuario.id)
        self.assertEqual("tecnico@ifrs.edu.br", usuario.email)
        self.assertEqual(PerfilUsuario.TECNICO, usuario.perfil)
        self.assertTrue(usuario.ativo)

    def test_nao_aceita_aluno_como_usuario_persistido(self):
        with self.assertRaises(ValueError):
            AuthService().registrar_usuario(
                nome="Aluno",
                email="aluno@ifrs.edu.br",
                senha="SenhaTeste123",
                perfil="ALUNO",
            )


if __name__ == "__main__":
    unittest.main()
