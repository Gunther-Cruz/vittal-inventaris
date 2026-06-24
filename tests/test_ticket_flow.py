import re
import unittest

from app import create_app
from app.extensions import db
from app.services.inventory_service import InventoryService
from app.services.ticket_service import TicketService
from app.services.usuario_service import UsuarioService


class TicketFlowTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        self.inventory_service = InventoryService()
        self.ticket_service = TicketService()
        self.usuario_service = UsuarioService()
        self.laboratory = self.inventory_service.create_laboratory(
            {"code": "LAB-10", "name": "Laboratory 10", "pavilion": "Pavilion 10"}
        )
        self.workstation = self.inventory_service.create_workstation(self.laboratory, {"code": "E01"})
        self.computer_case = self.inventory_service.create_computer_case(
            {"asset_tag": "PAT-001", "manufacturer": "Dell", "model": "OptiPlex"}
        )
        self.monitor = self.inventory_service.create_monitor(
            {"asset_tag": "MON-001", "manufacturer": "Dell", "model": "E2216H"}
        )
        self.professor = self.usuario_service.cadastrar_usuario(
            {"nome": "Professor IFRS", "email": "professor@ifrs.edu.br", "senha": "SenhaTeste123", "perfil": "PROFESSOR"}
        )
        self.technician = self.usuario_service.cadastrar_usuario(
            {"nome": "Tecnico IFRS", "email": "tecnico@ifrs.edu.br", "senha": "SenhaTeste123", "perfil": "TECNICO"}
        )
        self.coordinator = self.usuario_service.cadastrar_usuario(
            {"nome": "Coordenador IFRS", "email": "coordenador@ifrs.edu.br", "senha": "SenhaTeste123", "perfil": "COORDENADOR"}
        )
        self.inventory_service.assign_computer_case_to_workstation(
            self.computer_case,
            self.workstation,
            self.technician,
            {"movement_reason": "Initial allocation"},
        )
        self.inventory_service.assign_monitor_to_workstation(
            self.monitor,
            self.workstation,
            self.technician,
            {"movement_reason": "Initial allocation"},
        )

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_public_pages_link_ticket_creation(self):
        laboratories_response = self.client.get("/")
        workstations_response = self.client.get(f"/public/laboratories/{self.laboratory.id}/workstations")

        self.assertEqual(200, laboratories_response.status_code)
        self.assertIn(b"Abrir chamado do laboratorio", laboratories_response.data)
        self.assertEqual(200, workstations_response.status_code)
        self.assertIn(b"Abrir chamado da estacao", workstations_response.data)
        self.assertIn(b"Abrir chamado do gabinete", workstations_response.data)
        self.assertIn(b"Abrir chamado do monitor", workstations_response.data)

    def test_public_opens_laboratory_ticket_and_sees_protocol(self):
        csrf_token = self._csrf_token_from(f"/public/laboratories/{self.laboratory.id}/ticket/new")

        response = self.client.post(
            "/public/tickets",
            data={
                "scope": "LABORATORY",
                "laboratory_id": self.laboratory.id,
                "requester_name": "Aluno IFRS",
                "requester_email": "aluno@ifrs.edu.br",
                "description": "Laboratorio sem energia.",
                "csrf_token": csrf_token,
            },
            follow_redirects=True,
        )

        self.assertEqual(200, response.status_code)
        self.assertIn(b"Chamado VIT-", response.data)
        self.assertIn(b"Guarde este protocolo", response.data)

    def test_public_opens_computer_case_ticket(self):
        csrf_token = self._csrf_token_from(
            f"/public/workstations/{self.workstation.id}/ticket/new?scope=COMPUTER_CASE"
        )

        response = self.client.post(
            "/public/tickets",
            data={
                "scope": "COMPUTER_CASE",
                "workstation_id": self.workstation.id,
                "computer_case_id": self.computer_case.id,
                "requester_name": "Aluno IFRS",
                "requester_email": "aluno@ifrs.edu.br",
                "description": "Computador nao liga.",
                "csrf_token": csrf_token,
            },
            follow_redirects=True,
        )

        self.assertEqual(200, response.status_code)
        self.assertIn(b"PAT-001", response.data)

    def test_public_ticket_requires_institutional_email(self):
        csrf_token = self._csrf_token_from(f"/public/laboratories/{self.laboratory.id}/ticket/new")

        response = self.client.post(
            "/public/tickets",
            data={
                "scope": "LABORATORY",
                "laboratory_id": self.laboratory.id,
                "requester_name": "Aluno IFRS",
                "requester_email": "aluno@example.com",
                "description": "Falha.",
                "csrf_token": csrf_token,
            },
        )

        self.assertEqual(400, response.status_code)
        self.assertIn(b"Invalid institutional email.", response.data)

    def test_lookup_ticket_by_protocol(self):
        ticket = self._open_ticket()
        csrf_token = self._csrf_token_from("/tickets/lookup")

        response = self.client.post(
            "/tickets/lookup",
            data={"protocol": ticket.protocol.lower(), "csrf_token": csrf_token},
            follow_redirects=True,
        )

        self.assertEqual(200, response.status_code)
        self.assertIn(ticket.protocol.encode(), response.data)

    def test_internal_queue_requires_login(self):
        response = self.client.get("/tickets")

        self.assertEqual(302, response.status_code)
        self.assertIn("/auth/login", response.headers["Location"])

    def test_professor_cannot_access_internal_queue(self):
        self._login("professor@ifrs.edu.br")

        response = self.client.get("/tickets")

        self.assertEqual(403, response.status_code)

    def test_technician_lists_and_assigns_ticket(self):
        ticket = self._open_ticket()
        self._login("tecnico@ifrs.edu.br")
        list_response = self.client.get("/tickets")
        csrf_token = self._csrf_token_from(f"/tickets/{ticket.id}")
        assign_response = self.client.post(
            f"/tickets/{ticket.id}/assign",
            data={"csrf_token": csrf_token},
            follow_redirects=True,
        )

        self.assertEqual(200, list_response.status_code)
        self.assertIn(ticket.protocol.encode(), list_response.data)
        self.assertEqual(200, assign_response.status_code)
        self.assertIn(b"Ticket assigned successfully.", assign_response.data)
        self.assertIn(b"EM_ATENDIMENTO", assign_response.data)

    def test_technician_cannot_change_status_manually(self):
        ticket = self._open_ticket()
        self._login("tecnico@ifrs.edu.br")
        csrf_token = self._csrf_token_from(f"/tickets/{ticket.id}")

        response = self.client.post(
            f"/tickets/{ticket.id}/status",
            data={"status": "CANCELADO", "reason": "Duplicado", "csrf_token": csrf_token},
        )

        self.assertEqual(403, response.status_code)

    def test_coordinator_changes_status_and_history_is_visible(self):
        ticket = self._open_ticket()
        self._login("coordenador@ifrs.edu.br")
        csrf_token = self._csrf_token_from(f"/tickets/{ticket.id}")

        response = self.client.post(
            f"/tickets/{ticket.id}/status",
            data={"status": "CANCELADO", "reason": "Chamado duplicado", "csrf_token": csrf_token},
            follow_redirects=True,
        )

        self.assertEqual(200, response.status_code)
        self.assertIn(b"Ticket status updated successfully.", response.data)
        self.assertIn(b"CANCELED", response.data)

    def _open_ticket(self):
        return self.ticket_service.open_public_ticket(
            {
                "scope": "LABORATORY",
                "laboratory_id": self.laboratory.id,
                "requester_name": "Aluno IFRS",
                "requester_email": "aluno@ifrs.edu.br",
                "description": "Problema no laboratorio.",
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
