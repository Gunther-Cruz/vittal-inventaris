import re
import unittest

from app import create_app
from app.domain.enums import TicketScope, TicketStatus
from app.extensions import db
from app.services.inventory_service import InventoryService
from app.services.ticket_service import TicketService
from app.services.usuario_service import UsuarioService


class TicketServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app("testing")
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
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
        self.technician = self.usuario_service.cadastrar_usuario(
            {"nome": "Tecnico IFRS", "email": "tecnico@ifrs.edu.br", "senha": "SenhaTeste123", "perfil": "TECNICO"}
        )
        self.coordinator = self.usuario_service.cadastrar_usuario(
            {
                "nome": "Coordenador IFRS",
                "email": "coordenador@ifrs.edu.br",
                "senha": "SenhaTeste123",
                "perfil": "COORDENADOR",
            }
        )
        self.professor = self.usuario_service.cadastrar_usuario(
            {
                "nome": "Professor IFRS",
                "email": "professor@ifrs.edu.br",
                "senha": "SenhaTeste123",
                "perfil": "PROFESSOR",
            }
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

    def test_open_public_laboratory_ticket_generates_protocol_and_history(self):
        ticket = self.ticket_service.open_public_ticket(
            {
                "scope": "LABORATORY",
                "laboratory_id": self.laboratory.id,
                "requester_name": "Aluno IFRS",
                "requester_email": "aluno@ifrs.edu.br",
                "description": "Laboratorio sem energia.",
            }
        )

        self.assertEqual(TicketScope.LABORATORY, ticket.scope)
        self.assertEqual(TicketStatus.ABERTO, ticket.status)
        self.assertRegex(ticket.protocol, r"^VIT-\d{2}-[A-Z2-9]{5}$")
        self.assertEqual(1, len(self.ticket_service.list_ticket_history(ticket)))

    def test_open_workstation_ticket_uses_laboratory_from_workstation(self):
        ticket = self.ticket_service.open_public_ticket(
            {
                "scope": "WORKSTATION",
                "workstation_id": self.workstation.id,
                "requester_name": "Aluno IFRS",
                "requester_email": "aluno@ifrs.edu.br",
                "description": "Estacao sem rede.",
            }
        )

        self.assertEqual(self.laboratory.id, ticket.laboratory_id)
        self.assertEqual(self.workstation.id, ticket.workstation_id)

    def test_open_computer_case_ticket_requires_current_assignment(self):
        ticket = self.ticket_service.open_public_ticket(
            {
                "scope": "COMPUTER_CASE",
                "workstation_id": self.workstation.id,
                "computer_case_id": self.computer_case.id,
                "requester_name": "Aluno IFRS",
                "requester_email": "aluno@ifrs.edu.br",
                "description": "Computador nao liga.",
            }
        )

        self.assertEqual(self.computer_case.id, ticket.computer_case_id)

    def test_open_monitor_ticket_requires_current_assignment(self):
        ticket = self.ticket_service.open_public_ticket(
            {
                "scope": "MONITOR",
                "workstation_id": self.workstation.id,
                "monitor_id": self.monitor.id,
                "requester_name": "Aluno IFRS",
                "requester_email": "aluno@ifrs.edu.br",
                "description": "Monitor sem imagem.",
            }
        )

        self.assertEqual(self.monitor.id, ticket.monitor_id)

    def test_rejects_non_institutional_email(self):
        with self.assertRaisesRegex(ValueError, "Invalid institutional email."):
            self.ticket_service.open_public_ticket(
                {
                    "scope": "LABORATORY",
                    "laboratory_id": self.laboratory.id,
                    "requester_name": "Aluno IFRS",
                    "requester_email": "aluno@example.com",
                    "description": "Falha.",
                }
            )

    def test_authenticated_ticket_keeps_user_reference(self):
        ticket = self.ticket_service.open_authenticated_ticket(
            {
                "scope": "LABORATORY",
                "laboratory_id": self.laboratory.id,
                "description": "Solicitacao autenticada.",
            },
            self.professor,
        )

        self.assertEqual(self.professor.id, ticket.created_by_user_id)
        self.assertEqual("professor@ifrs.edu.br", ticket.requester_email)

    def test_technician_assigns_ticket_and_history_tracks_status(self):
        ticket = self._open_laboratory_ticket()

        self.ticket_service.assign_ticket(ticket, self.technician)

        self.assertEqual(TicketStatus.EM_ATENDIMENTO, ticket.status)
        self.assertEqual(self.technician.id, ticket.assigned_to_user_id)
        self.assertEqual(2, len(self.ticket_service.list_ticket_history(ticket)))

    def test_technician_cannot_change_status_manually(self):
        ticket = self._open_laboratory_ticket()

        with self.assertRaisesRegex(PermissionError, "Only coordinators"):
            self.ticket_service.change_status_by_coordinator(
                ticket,
                "CANCELADO",
                self.technician,
                "Chamado duplicado.",
            )

    def test_coordinator_changes_status_manually(self):
        ticket = self._open_laboratory_ticket()

        self.ticket_service.change_status_by_coordinator(
            ticket,
            "CANCELADO",
            self.coordinator,
            "Chamado duplicado.",
        )

        self.assertEqual(TicketStatus.CANCELADO, ticket.status)
        self.assertIsNotNone(ticket.closed_at)

    def _open_laboratory_ticket(self):
        return self.ticket_service.open_public_ticket(
            {
                "scope": "LABORATORY",
                "laboratory_id": self.laboratory.id,
                "requester_name": "Aluno IFRS",
                "requester_email": "aluno@ifrs.edu.br",
                "description": "Problema no laboratorio.",
            }
        )


if __name__ == "__main__":
    unittest.main()
