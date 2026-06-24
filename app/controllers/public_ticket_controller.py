from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user

from app.domain.enums import TicketScope
from app.services.inventory_service import InventoryService
from app.services.ticket_service import TicketService

public_tickets_bp = Blueprint("public_tickets", __name__)


@public_tickets_bp.get("/public/laboratories/<int:laboratory_id>/ticket/new")
def new_laboratory_ticket(laboratory_id: int):
    """Public form for opening a laboratory-scoped ticket."""
    inventory_service = InventoryService()
    laboratory = _get_laboratory_or_404(inventory_service, laboratory_id)
    if not laboratory.active:
        abort(404)

    return render_template(
        "tickets/public_form.html",
        scope=TicketScope.LABORATORY,
        laboratory=laboratory,
        workstation=None,
        computer_case=None,
        monitor=None,
    )


@public_tickets_bp.get("/public/workstations/<int:workstation_id>/ticket/new")
def new_workstation_ticket(workstation_id: int):
    """Public form for opening workstation, computer case, or monitor tickets."""
    inventory_service = InventoryService()
    workstation = _get_workstation_or_404(inventory_service, workstation_id)
    if not workstation.active or not workstation.laboratory.active:
        abort(404)

    scope = _scope_from_query()
    computer_case = workstation.current_computer_case if scope == TicketScope.COMPUTER_CASE else None
    monitor = workstation.current_monitor if scope == TicketScope.MONITOR else None
    if scope == TicketScope.COMPUTER_CASE and computer_case is None:
        abort(404)
    if scope == TicketScope.MONITOR and monitor is None:
        abort(404)
    if scope == TicketScope.LABORATORY:
        return redirect(url_for("public_tickets.new_laboratory_ticket", laboratory_id=workstation.laboratory_id))

    return render_template(
        "tickets/public_form.html",
        scope=scope,
        laboratory=workstation.laboratory,
        workstation=workstation,
        computer_case=computer_case,
        monitor=monitor,
    )


@public_tickets_bp.post("/public/tickets")
def create_public_ticket():
    """Creates a public ticket and returns the protocol summary."""
    ticket_service = TicketService()
    try:
        if current_user.is_authenticated:
            ticket = ticket_service.open_authenticated_ticket(request.form, current_user)
        else:
            ticket = ticket_service.open_public_ticket(request.form)
    except ValueError as exc:
        flash(str(exc), "error")
        return _rerender_public_form_from_submission(str(exc)), 400

    return redirect(url_for("public_tickets.public_ticket_success", protocol=ticket.protocol))


@public_tickets_bp.get("/tickets/<protocol>/public")
def public_ticket_success(protocol: str):
    """Public protocol result page shown after opening or looking up a ticket."""
    ticket_service = TicketService()
    try:
        ticket = ticket_service.get_ticket_by_protocol(protocol)
    except LookupError:
        abort(404)

    return render_template("tickets/public_detail.html", ticket=ticket)


@public_tickets_bp.get("/tickets/lookup")
def lookup_ticket_form():
    """Public lookup form for requesters who only have a protocol."""
    return render_template("tickets/lookup.html")


@public_tickets_bp.post("/tickets/lookup")
def lookup_ticket():
    """Redirects to the public ticket page when a protocol exists."""
    protocol = str(request.form.get("protocol", "")).strip().upper()
    ticket_service = TicketService()
    try:
        ticket = ticket_service.get_ticket_by_protocol(protocol)
    except LookupError:
        flash("Ticket not found.", "error")
        return render_template("tickets/lookup.html", protocol=protocol), 404

    return redirect(url_for("public_tickets.public_ticket_success", protocol=ticket.protocol))


def _rerender_public_form_from_submission(error_message: str):
    scope = _scope_from_form()
    inventory_service = InventoryService()
    laboratory = _get_optional_laboratory(inventory_service, request.form.get("laboratory_id"))
    workstation = _get_optional_workstation(inventory_service, request.form.get("workstation_id"))
    computer_case = workstation.current_computer_case if workstation and scope == TicketScope.COMPUTER_CASE else None
    monitor = workstation.current_monitor if workstation and scope == TicketScope.MONITOR else None
    return render_template(
        "tickets/public_form.html",
        scope=scope,
        laboratory=laboratory,
        workstation=workstation,
        computer_case=computer_case,
        monitor=monitor,
        form_data=request.form,
        error_message=error_message,
    )


def _scope_from_query() -> TicketScope:
    normalized = str(request.args.get("scope", TicketScope.WORKSTATION.value)).strip().upper()
    try:
        return TicketScope(normalized)
    except ValueError:
        abort(404)


def _scope_from_form() -> TicketScope:
    try:
        return TicketScope(str(request.form.get("scope", "")).strip().upper())
    except ValueError:
        return TicketScope.WORKSTATION


def _get_laboratory_or_404(inventory_service: InventoryService, laboratory_id: int):
    try:
        return inventory_service.get_laboratory(laboratory_id)
    except LookupError:
        abort(404)


def _get_workstation_or_404(inventory_service: InventoryService, workstation_id: int):
    try:
        return inventory_service.get_workstation(workstation_id)
    except LookupError:
        abort(404)


def _get_optional_laboratory(inventory_service: InventoryService, laboratory_id):
    try:
        return inventory_service.get_laboratory(int(laboratory_id))
    except (LookupError, TypeError, ValueError):
        return None


def _get_optional_workstation(inventory_service: InventoryService, workstation_id):
    try:
        return inventory_service.get_workstation(int(workstation_id))
    except (LookupError, TypeError, ValueError):
        return None
