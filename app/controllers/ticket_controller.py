from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user

from app.domain.enums import TicketScope, TicketStatus
from app.security.decorators import permissao_requerida
from app.security.permissions import (
    can_assign_tickets,
    can_change_ticket_status_manually,
    can_view_tickets,
)
from app.services.ticket_service import TicketService

tickets_bp = Blueprint("tickets", __name__, url_prefix="/tickets")


@tickets_bp.get("")
@permissao_requerida(can_view_tickets)
def list_tickets():
    """Internal ticket queue for technicians and coordinators."""
    ticket_service = TicketService()
    tickets = ticket_service.list_tickets(request.args)
    return render_template(
        "tickets/list.html",
        tickets=tickets,
        statuses=TicketStatus,
        scopes=TicketScope,
        can_assign=can_assign_tickets(current_user),
        can_change_status=can_change_ticket_status_manually(current_user),
    )


@tickets_bp.get("/<int:ticket_id>")
@permissao_requerida(can_view_tickets)
def show_ticket(ticket_id: int):
    """Internal ticket details with audit history and allowed actions."""
    ticket_service = TicketService()
    ticket = _get_ticket_or_404(ticket_service, ticket_id)
    return render_template(
        "tickets/detail.html",
        ticket=ticket,
        history=ticket_service.list_ticket_history(ticket),
        statuses=TicketStatus,
        can_assign=can_assign_tickets(current_user),
        can_change_status=can_change_ticket_status_manually(current_user),
    )


@tickets_bp.post("/<int:ticket_id>/assign")
@permissao_requerida(can_assign_tickets)
def assign_ticket(ticket_id: int):
    """Assigns a ticket to the logged technician."""
    ticket_service = TicketService()
    ticket = _get_ticket_or_404(ticket_service, ticket_id)
    try:
        ticket_service.assign_ticket(ticket, current_user)
    except (PermissionError, ValueError) as exc:
        flash(str(exc), "error")
        return redirect(url_for("tickets.show_ticket", ticket_id=ticket.id))

    flash("Ticket assigned successfully.", "success")
    return redirect(url_for("tickets.show_ticket", ticket_id=ticket.id))


@tickets_bp.post("/<int:ticket_id>/status")
@permissao_requerida(can_change_ticket_status_manually)
def change_ticket_status(ticket_id: int):
    """Coordinator-only exceptional manual status change."""
    ticket_service = TicketService()
    ticket = _get_ticket_or_404(ticket_service, ticket_id)
    try:
        ticket_service.change_status_by_coordinator(
            ticket,
            request.form.get("status", ""),
            current_user,
            request.form.get("reason", ""),
        )
    except (PermissionError, ValueError) as exc:
        flash(str(exc), "error")
        return redirect(url_for("tickets.show_ticket", ticket_id=ticket.id))

    flash("Ticket status updated successfully.", "success")
    return redirect(url_for("tickets.show_ticket", ticket_id=ticket.id))


def _get_ticket_or_404(ticket_service: TicketService, ticket_id: int):
    try:
        return ticket_service.get_ticket(ticket_id)
    except LookupError:
        abort(404)
