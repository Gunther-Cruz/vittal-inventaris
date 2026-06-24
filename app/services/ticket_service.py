from __future__ import annotations

import re
import secrets
import string
from collections.abc import Mapping
from datetime import datetime, timezone

from app.domain.enums import PerfilUsuario, TicketHistoryEvent, TicketScope, TicketStatus
from app.domain.models import ComputerCase, Laboratory, Monitor, Ticket, TicketHistory, Usuario, Workstation
from app.extensions import db
from app.repositories.computer_case_repository import ComputerCaseRepository
from app.repositories.laboratory_repository import LaboratoryRepository
from app.repositories.monitor_repository import MonitorRepository
from app.repositories.ticket_history_repository import TicketHistoryRepository
from app.repositories.ticket_repository import TicketRepository
from app.repositories.workstation_repository import WorkstationRepository

EMAIL_INSTITUCIONAL_RE = re.compile(r"^[A-Z0-9._%+-]+@ifrs\.edu\.br$", re.IGNORECASE)
PROTOCOL_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


class TicketService:
    """Use cases for help requests, preserving simple public opening and audit history."""

    FUTURE_STATUS_NOTE = (
        "Future OS flow must become the normal path for technical ticket status evolution."
    )

    def __init__(
        self,
        ticket_repository: TicketRepository | None = None,
        history_repository: TicketHistoryRepository | None = None,
        laboratory_repository: LaboratoryRepository | None = None,
        workstation_repository: WorkstationRepository | None = None,
        computer_case_repository: ComputerCaseRepository | None = None,
        monitor_repository: MonitorRepository | None = None,
    ) -> None:
        self.ticket_repository = ticket_repository or TicketRepository()
        self.history_repository = history_repository or TicketHistoryRepository()
        self.laboratory_repository = laboratory_repository or LaboratoryRepository()
        self.workstation_repository = workstation_repository or WorkstationRepository()
        self.computer_case_repository = computer_case_repository or ComputerCaseRepository()
        self.monitor_repository = monitor_repository or MonitorRepository()

    # -------------------------------------------------------------------------
    # Opening and lookup
    # -------------------------------------------------------------------------

    def open_public_ticket(self, data: Mapping[str, object]) -> Ticket:
        """Opens a ticket from the public flow without requiring a persisted user."""
        return self._open_ticket(data, created_by_user=None)

    def open_authenticated_ticket(self, data: Mapping[str, object], user: Usuario) -> Ticket:
        """Opens a ticket while keeping a snapshot of the authenticated requester's data."""
        enriched_data = dict(data)
        enriched_data.setdefault("requester_name", user.nome)
        enriched_data.setdefault("requester_email", user.email)
        return self._open_ticket(enriched_data, created_by_user=user)

    def get_ticket_by_protocol(self, protocol: str) -> Ticket:
        ticket = self.ticket_repository.find_by_protocol(protocol)
        if ticket is None:
            raise LookupError("Ticket not found.")

        return ticket

    def get_ticket(self, ticket_id: int) -> Ticket:
        ticket = self.ticket_repository.find_by_id(ticket_id)
        if ticket is None:
            raise LookupError("Ticket not found.")

        return ticket

    def list_tickets(self, filters: Mapping[str, object] | None = None) -> list[Ticket]:
        normalized_filters: dict[str, object] = {}
        filters = filters or {}

        status = str(filters.get("status", "")).strip()
        if status:
            normalized_filters["status"] = self._normalize_status(status)

        scope = str(filters.get("scope", "")).strip()
        if scope:
            normalized_filters["scope"] = self._normalize_scope(scope)

        return self.ticket_repository.list_all(normalized_filters)

    def list_ticket_history(self, ticket: Ticket) -> list[TicketHistory]:
        return self.history_repository.list_by_ticket(ticket.id)

    # -------------------------------------------------------------------------
    # Internal lifecycle
    # -------------------------------------------------------------------------

    def assign_ticket(self, ticket: Ticket, technician: Usuario) -> Ticket:
        """Assigns a ticket to a technician; full technical evolution will be handled by OS later."""
        if technician.perfil != PerfilUsuario.TECNICO:
            raise PermissionError("Only technicians can assume tickets.")
        if not technician.ativo:
            raise PermissionError("Inactive users cannot assume tickets.")
        if ticket.status in (TicketStatus.RESOLVIDO, TicketStatus.CANCELADO):
            raise ValueError("Closed or canceled tickets cannot be assigned.")

        previous_status = ticket.status
        ticket.assigned_to_user = technician
        ticket.status = TicketStatus.EM_ATENDIMENTO
        self._add_history(
            ticket,
            TicketHistoryEvent.ASSIGNED,
            "Ticket assigned to technician.",
            created_by_user=technician,
            previous_status=previous_status,
            new_status=ticket.status,
        )
        return self.ticket_repository.commit(ticket)

    def change_status_by_coordinator(
        self,
        ticket: Ticket,
        status: object,
        coordinator: Usuario,
        reason: object,
    ) -> Ticket:
        """Allows exceptional administrative status changes until the OS flow exists."""
        self._ensure_coordinator(coordinator)
        new_status = self._normalize_status(status)
        if new_status == ticket.status:
            raise ValueError("Ticket already has this status.")

        reason_text = self._normalize_required_text(reason, "Reason is required.")
        previous_status = ticket.status
        ticket.status = new_status
        ticket.closed_at = datetime.now(timezone.utc) if new_status in self._final_statuses() else None
        self._add_history(
            ticket,
            self._event_for_status(new_status),
            reason_text,
            created_by_user=coordinator,
            previous_status=previous_status,
            new_status=new_status,
        )
        return self.ticket_repository.commit(ticket)

    def close_ticket_by_coordinator(self, ticket: Ticket, coordinator: Usuario, reason: object) -> Ticket:
        return self.change_status_by_coordinator(ticket, TicketStatus.RESOLVIDO, coordinator, reason)

    def cancel_ticket_by_coordinator(self, ticket: Ticket, coordinator: Usuario, reason: object) -> Ticket:
        return self.change_status_by_coordinator(ticket, TicketStatus.CANCELADO, coordinator, reason)

    # -------------------------------------------------------------------------
    # Builders and validation
    # -------------------------------------------------------------------------

    def _open_ticket(self, data: Mapping[str, object], created_by_user: Usuario | None) -> Ticket:
        scope = self._normalize_scope(data.get("scope", ""))
        context = self._resolve_context(scope, data)
        ticket = Ticket(
            protocol=self._generate_unique_protocol(),
            scope=scope,
            status=TicketStatus.ABERTO,
            requester_name=self._normalize_required_text(
                data.get("requester_name", ""),
                "Requester name is required.",
            ),
            requester_email=self._normalize_institutional_email(data.get("requester_email", "")),
            description=self._normalize_required_text(data.get("description", ""), "Description is required."),
            laboratory=context["laboratory"],
            workstation=context["workstation"],
            computer_case=context["computer_case"],
            monitor=context["monitor"],
            created_by_user=created_by_user,
        )
        self._add_history(
            ticket,
            TicketHistoryEvent.OPENED,
            "Ticket opened.",
            created_by_user=created_by_user,
            previous_status=None,
            new_status=TicketStatus.ABERTO,
        )
        db.session.add(ticket)
        return self.ticket_repository.commit(ticket)

    def _resolve_context(self, scope: TicketScope, data: Mapping[str, object]) -> dict[str, object]:
        laboratory = self._find_laboratory(data.get("laboratory_id"))
        workstation = self._find_workstation(data.get("workstation_id"))
        computer_case = self._find_computer_case(data.get("computer_case_id"))
        monitor = self._find_monitor(data.get("monitor_id"))

        if scope == TicketScope.LABORATORY:
            if laboratory is None:
                raise ValueError("Laboratory is required for laboratory tickets.")
        elif scope == TicketScope.WORKSTATION:
            if workstation is None:
                raise ValueError("Workstation is required for workstation tickets.")
            laboratory = workstation.laboratory
        elif scope == TicketScope.COMPUTER_CASE:
            if workstation is None or computer_case is None:
                raise ValueError("Workstation and computer case are required for computer case tickets.")
            if workstation.current_computer_case_id != computer_case.id:
                raise ValueError("Computer case is not currently assigned to this workstation.")
            laboratory = workstation.laboratory
        elif scope == TicketScope.MONITOR:
            if workstation is None or monitor is None:
                raise ValueError("Workstation and monitor are required for monitor tickets.")
            if workstation.current_monitor_id != monitor.id:
                raise ValueError("Monitor is not currently assigned to this workstation.")
            laboratory = workstation.laboratory

        if laboratory is not None and not laboratory.active:
            raise ValueError("Inactive laboratories cannot receive public tickets.")
        if workstation is not None and not workstation.active:
            raise ValueError("Inactive workstations cannot receive public tickets.")

        return {
            "laboratory": laboratory,
            "workstation": workstation,
            "computer_case": computer_case,
            "monitor": monitor,
        }

    def _add_history(
        self,
        ticket: Ticket,
        event_type: TicketHistoryEvent,
        description: str,
        created_by_user: Usuario | None = None,
        previous_status: TicketStatus | None = None,
        new_status: TicketStatus | None = None,
    ) -> None:
        # History is added to the same session so ticket and audit event commit atomically.
        db.session.add(
            TicketHistory(
                ticket=ticket,
                event_type=event_type,
                previous_status=previous_status,
                new_status=new_status,
                description=description,
                created_by_user=created_by_user,
            )
        )

    def _generate_unique_protocol(self) -> str:
        year = datetime.now(timezone.utc).strftime("%y")
        for _ in range(20):
            suffix = "".join(secrets.choice(PROTOCOL_ALPHABET) for _ in range(5))
            protocol = f"VIT-{year}-{suffix}"
            if self.ticket_repository.find_by_protocol(protocol) is None:
                return protocol

        raise RuntimeError("Unable to generate a unique ticket protocol.")

    def _find_laboratory(self, value: object) -> Laboratory | None:
        identifier = self._optional_int(value)
        return self.laboratory_repository.find_by_id(identifier) if identifier is not None else None

    def _find_workstation(self, value: object) -> Workstation | None:
        identifier = self._optional_int(value)
        return self.workstation_repository.find_by_id(identifier) if identifier is not None else None

    def _find_computer_case(self, value: object) -> ComputerCase | None:
        identifier = self._optional_int(value)
        return self.computer_case_repository.find_by_id(identifier) if identifier is not None else None

    def _find_monitor(self, value: object) -> Monitor | None:
        identifier = self._optional_int(value)
        return self.monitor_repository.find_by_id(identifier) if identifier is not None else None

    @staticmethod
    def _normalize_required_text(value: object, message: str) -> str:
        normalized = str(value).strip()
        if not normalized:
            raise ValueError(message)

        return normalized

    @staticmethod
    def _normalize_institutional_email(value: object) -> str:
        email = str(value).strip().lower()
        if not EMAIL_INSTITUCIONAL_RE.match(email):
            raise ValueError("Invalid institutional email.")

        return email

    @staticmethod
    def _normalize_scope(value: object) -> TicketScope:
        try:
            return value if isinstance(value, TicketScope) else TicketScope(str(value).strip().upper())
        except ValueError as exc:
            raise ValueError("Invalid ticket scope.") from exc

    @staticmethod
    def _normalize_status(value: object) -> TicketStatus:
        try:
            return value if isinstance(value, TicketStatus) else TicketStatus(str(value).strip().upper())
        except ValueError as exc:
            raise ValueError("Invalid ticket status.") from exc

    @staticmethod
    def _optional_int(value: object) -> int | None:
        normalized = str(value or "").strip()
        if not normalized:
            return None

        try:
            return int(normalized)
        except ValueError as exc:
            raise ValueError("Invalid identifier.") from exc

    @staticmethod
    def _ensure_coordinator(user: Usuario) -> None:
        if not user or not user.ativo or user.perfil != PerfilUsuario.COORDENADOR:
            raise PermissionError("Only coordinators can change ticket status manually.")

    @staticmethod
    def _final_statuses() -> tuple[TicketStatus, TicketStatus]:
        return (TicketStatus.RESOLVIDO, TicketStatus.CANCELADO)

    @staticmethod
    def _event_for_status(status: TicketStatus) -> TicketHistoryEvent:
        if status == TicketStatus.RESOLVIDO:
            return TicketHistoryEvent.CLOSED
        if status == TicketStatus.CANCELADO:
            return TicketHistoryEvent.CANCELED

        return TicketHistoryEvent.STATUS_CHANGED
