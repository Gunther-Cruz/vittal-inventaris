from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user

from app.domain.enums import OperationalStatus
from app.security.decorators import permissao_requerida
from app.security.permissions import can_manage_asset_allocations, can_view_asset_allocations
from app.services.inventory_service import InventoryService

asset_allocations_bp = Blueprint("asset_allocations", __name__, url_prefix="/workstations")

UNASSIGNMENT_STATUSES = (
    OperationalStatus.FUNCIONAL_DESALOCADO,
    OperationalStatus.EM_MANUTENCAO,
    OperationalStatus.DESATIVADO,
)


@asset_allocations_bp.get("/<int:workstation_id>/assets")
@permissao_requerida(can_view_asset_allocations)
def show_workstation_assets(workstation_id: int):
    """Shows current workstation assets and allocation history."""
    inventory_service = InventoryService()
    workstation = _get_workstation_or_404(inventory_service, workstation_id)
    return _render_assets_page(inventory_service, workstation)


@asset_allocations_bp.post("/<int:workstation_id>/computer-case")
@permissao_requerida(can_manage_asset_allocations)
def assign_computer_case(workstation_id: int):
    """Assigns an available computer case to an empty workstation slot."""
    inventory_service = InventoryService()
    workstation = _get_workstation_or_404(inventory_service, workstation_id)
    computer_case = _get_computer_case_or_404(inventory_service, request.form.get("computer_case_id"))
    try:
        inventory_service.assign_computer_case_to_workstation(
            computer_case,
            workstation,
            current_user,
            request.form,
        )
    except ValueError as exc:
        flash(str(exc), "error")
        return _render_assets_page(inventory_service, workstation), 400

    flash("Computer case assigned successfully.", "success")
    return redirect(url_for("asset_allocations.show_workstation_assets", workstation_id=workstation.id))


@asset_allocations_bp.post("/<int:workstation_id>/computer-case/unassign")
@permissao_requerida(can_manage_asset_allocations)
def unassign_computer_case(workstation_id: int):
    """Unassigns the current computer case and closes its active allocation."""
    inventory_service = InventoryService()
    workstation = _get_workstation_or_404(inventory_service, workstation_id)
    try:
        inventory_service.unassign_computer_case_from_workstation(
            workstation,
            current_user,
            request.form,
        )
    except ValueError as exc:
        flash(str(exc), "error")
        return _render_assets_page(inventory_service, workstation), 400

    flash("Computer case unassigned successfully.", "success")
    return redirect(url_for("asset_allocations.show_workstation_assets", workstation_id=workstation.id))


@asset_allocations_bp.post("/<int:workstation_id>/monitor")
@permissao_requerida(can_manage_asset_allocations)
def assign_monitor(workstation_id: int):
    """Assigns an available monitor to an empty workstation slot."""
    inventory_service = InventoryService()
    workstation = _get_workstation_or_404(inventory_service, workstation_id)
    monitor = _get_monitor_or_404(inventory_service, request.form.get("monitor_id"))
    try:
        inventory_service.assign_monitor_to_workstation(
            monitor,
            workstation,
            current_user,
            request.form,
        )
    except ValueError as exc:
        flash(str(exc), "error")
        return _render_assets_page(inventory_service, workstation), 400

    flash("Monitor assigned successfully.", "success")
    return redirect(url_for("asset_allocations.show_workstation_assets", workstation_id=workstation.id))


@asset_allocations_bp.post("/<int:workstation_id>/monitor/unassign")
@permissao_requerida(can_manage_asset_allocations)
def unassign_monitor(workstation_id: int):
    """Unassigns the current monitor and closes its active allocation."""
    inventory_service = InventoryService()
    workstation = _get_workstation_or_404(inventory_service, workstation_id)
    try:
        inventory_service.unassign_monitor_from_workstation(
            workstation,
            current_user,
            request.form,
        )
    except ValueError as exc:
        flash(str(exc), "error")
        return _render_assets_page(inventory_service, workstation), 400

    flash("Monitor unassigned successfully.", "success")
    return redirect(url_for("asset_allocations.show_workstation_assets", workstation_id=workstation.id))


def _render_assets_page(inventory_service: InventoryService, workstation):
    return render_template(
        "asset_allocations/detail.html",
        workstation=workstation,
        available_computer_cases=inventory_service.list_available_computer_cases(),
        available_monitors=inventory_service.list_available_monitors(),
        computer_case_history=inventory_service.list_workstation_computer_case_allocations(workstation),
        monitor_history=inventory_service.list_workstation_monitor_allocations(workstation),
        unassignment_statuses=UNASSIGNMENT_STATUSES,
    )


def _get_workstation_or_404(inventory_service: InventoryService, workstation_id: int):
    try:
        return inventory_service.get_workstation(workstation_id)
    except LookupError:
        abort(404)


def _get_computer_case_or_404(inventory_service: InventoryService, computer_case_id):
    try:
        return inventory_service.get_computer_case(int(computer_case_id))
    except (LookupError, TypeError, ValueError):
        abort(404)


def _get_monitor_or_404(inventory_service: InventoryService, monitor_id):
    try:
        return inventory_service.get_monitor(int(monitor_id))
    except (LookupError, TypeError, ValueError):
        abort(404)
