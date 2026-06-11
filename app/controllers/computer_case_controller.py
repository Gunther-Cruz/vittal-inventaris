from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from app.domain.enums import OperationalStatus
from app.security.decorators import permissao_requerida
from app.security.permissions import can_manage_computer_cases, can_view_computer_cases
from app.services.inventory_service import InventoryService

computer_cases_bp = Blueprint("computer_cases", __name__, url_prefix="/computer-cases")


@computer_cases_bp.get("")
@permissao_requerida(can_view_computer_cases)
def list_computer_cases():
    """Lists computer cases for authenticated inventory users."""
    inventory_service = InventoryService()
    return render_template(
        "computer_cases/list.html",
        computer_cases=inventory_service.list_computer_cases(),
        assigned_computer_case_ids=inventory_service.list_assigned_computer_case_ids(),
        statuses=OperationalStatus,
    )


@computer_cases_bp.get("/new")
@permissao_requerida(can_manage_computer_cases)
def new_computer_case():
    """Shows the technical inventory form for a new computer case."""
    return render_template(
        "computer_cases/new.html",
        statuses=OperationalStatus,
    )


@computer_cases_bp.post("/new")
@permissao_requerida(can_manage_computer_cases)
def create_computer_case():
    """Registers a new computer case without requiring a service order."""
    inventory_service = InventoryService()
    try:
        computer_case = inventory_service.create_computer_case(request.form)
    except ValueError as exc:
        flash(str(exc), "error")
        return (
            render_template(
                "computer_cases/new.html",
                statuses=OperationalStatus,
                form_data=request.form,
            ),
            400,
        )

    flash(f"Computer case created successfully: {computer_case.asset_tag}", "success")
    return redirect(url_for("computer_cases.list_computer_cases"))


@computer_cases_bp.get("/<int:computer_case_id>")
@permissao_requerida(can_view_computer_cases)
def show_computer_case(computer_case_id: int):
    """Shows the complete technical record of a computer case."""
    inventory_service = InventoryService()
    computer_case = _get_computer_case_or_404(inventory_service, computer_case_id)
    return render_template(
        "computer_cases/detail.html",
        computer_case=computer_case,
        allocation_history=inventory_service.list_computer_case_allocations(computer_case),
    )


@computer_cases_bp.get("/<int:computer_case_id>/edit")
@permissao_requerida(can_manage_computer_cases)
def edit_computer_case(computer_case_id: int):
    """Shows the edit form for initial inventory corrections."""
    inventory_service = InventoryService()
    computer_case = _get_computer_case_or_404(inventory_service, computer_case_id)
    return render_template(
        "computer_cases/edit.html",
        computer_case=computer_case,
        asset_assigned=computer_case.id in inventory_service.list_assigned_computer_case_ids(),
        statuses=OperationalStatus,
    )


@computer_cases_bp.post("/<int:computer_case_id>/edit")
@permissao_requerida(can_manage_computer_cases)
def update_computer_case(computer_case_id: int):
    """Updates inventory data while future technical changes remain reserved for service orders."""
    inventory_service = InventoryService()
    computer_case = _get_computer_case_or_404(inventory_service, computer_case_id)
    try:
        inventory_service.update_computer_case(computer_case, request.form)
    except ValueError as exc:
        flash(str(exc), "error")
        return (
            render_template(
                "computer_cases/edit.html",
                computer_case=computer_case,
                asset_assigned=computer_case.id in inventory_service.list_assigned_computer_case_ids(),
                statuses=OperationalStatus,
                form_data=request.form,
            ),
            400,
        )

    flash("Computer case updated successfully.", "success")
    return redirect(url_for("computer_cases.show_computer_case", computer_case_id=computer_case.id))


@computer_cases_bp.post("/<int:computer_case_id>/status")
@permissao_requerida(can_manage_computer_cases)
def update_computer_case_status(computer_case_id: int):
    """Changes the operational status without moving the asset between workstations."""
    inventory_service = InventoryService()
    computer_case = _get_computer_case_or_404(inventory_service, computer_case_id)
    try:
        inventory_service.set_computer_case_status(
            computer_case,
            request.form.get("operational_status", ""),
        )
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("computer_cases.list_computer_cases"))

    flash("Computer case status updated successfully.", "success")
    return redirect(url_for("computer_cases.list_computer_cases"))


def _get_computer_case_or_404(
    inventory_service: InventoryService,
    computer_case_id: int,
):
    try:
        return inventory_service.get_computer_case(computer_case_id)
    except LookupError:
        abort(404)
