from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from app.domain.enums import DisplayConnection, OperationalStatus
from app.security.decorators import permissao_requerida
from app.security.permissions import can_manage_monitors, can_view_monitors
from app.services.inventory_service import InventoryService

monitors_bp = Blueprint("monitors", __name__, url_prefix="/monitors")


@monitors_bp.get("")
@permissao_requerida(can_view_monitors)
def list_monitors():
    """Lists monitors for authenticated inventory users."""
    inventory_service = InventoryService()
    return render_template(
        "monitors/list.html",
        monitors=inventory_service.list_monitors(),
        assigned_monitor_ids=inventory_service.list_assigned_monitor_ids(),
        statuses=OperationalStatus,
    )


@monitors_bp.get("/new")
@permissao_requerida(can_manage_monitors)
def new_monitor():
    """Shows the monitor creation form."""
    return render_template(
        "monitors/new.html",
        statuses=OperationalStatus,
        display_connections=DisplayConnection,
    )


@monitors_bp.post("/new")
@permissao_requerida(can_manage_monitors)
def create_monitor():
    """Registers a new monitor as an independent inventory asset."""
    inventory_service = InventoryService()
    try:
        monitor = inventory_service.create_monitor(request.form)
    except ValueError as exc:
        flash(str(exc), "error")
        return (
            render_template(
                "monitors/new.html",
                statuses=OperationalStatus,
                display_connections=DisplayConnection,
                form_data=request.form,
            ),
            400,
        )

    flash(f"Monitor created successfully: {monitor.asset_tag}", "success")
    return redirect(url_for("monitors.list_monitors"))


@monitors_bp.get("/<int:monitor_id>")
@permissao_requerida(can_view_monitors)
def show_monitor(monitor_id: int):
    """Shows the complete technical record of a monitor."""
    inventory_service = InventoryService()
    monitor = _get_monitor_or_404(inventory_service, monitor_id)
    return render_template(
        "monitors/detail.html",
        monitor=monitor,
        allocation_history=inventory_service.list_monitor_allocations(monitor),
    )


@monitors_bp.get("/<int:monitor_id>/edit")
@permissao_requerida(can_manage_monitors)
def edit_monitor(monitor_id: int):
    """Shows the edit form for monitor inventory corrections."""
    inventory_service = InventoryService()
    monitor = _get_monitor_or_404(inventory_service, monitor_id)
    return render_template(
        "monitors/edit.html",
        monitor=monitor,
        asset_assigned=monitor.id in inventory_service.list_assigned_monitor_ids(),
        statuses=OperationalStatus,
        display_connections=DisplayConnection,
    )


@monitors_bp.post("/<int:monitor_id>/edit")
@permissao_requerida(can_manage_monitors)
def update_monitor(monitor_id: int):
    """Updates monitor inventory data without binding it to a workstation."""
    inventory_service = InventoryService()
    monitor = _get_monitor_or_404(inventory_service, monitor_id)
    try:
        inventory_service.update_monitor(monitor, request.form)
    except ValueError as exc:
        flash(str(exc), "error")
        return (
            render_template(
                "monitors/edit.html",
                monitor=monitor,
                asset_assigned=monitor.id in inventory_service.list_assigned_monitor_ids(),
                statuses=OperationalStatus,
                display_connections=DisplayConnection,
                form_data=request.form,
            ),
            400,
        )

    flash("Monitor updated successfully.", "success")
    return redirect(url_for("monitors.show_monitor", monitor_id=monitor.id))


@monitors_bp.post("/<int:monitor_id>/status")
@permissao_requerida(can_manage_monitors)
def update_monitor_status(monitor_id: int):
    """Changes monitor operational status without moving the asset."""
    inventory_service = InventoryService()
    monitor = _get_monitor_or_404(inventory_service, monitor_id)
    try:
        inventory_service.set_monitor_status(
            monitor,
            request.form.get("operational_status", ""),
        )
    except ValueError as exc:
        flash(str(exc), "error")
        return redirect(url_for("monitors.list_monitors"))

    flash("Monitor status updated successfully.", "success")
    return redirect(url_for("monitors.list_monitors"))


def _get_monitor_or_404(inventory_service: InventoryService, monitor_id: int):
    try:
        return inventory_service.get_monitor(monitor_id)
    except LookupError:
        abort(404)
