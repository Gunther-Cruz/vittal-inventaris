from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from app.security.decorators import permissao_requerida
from app.security.permissions import can_manage_workstations, can_view_workstations
from app.services.inventory_service import InventoryService

workstations_bp = Blueprint("workstations", __name__)


@workstations_bp.get("/laboratories/<int:laboratory_id>/workstations")
@permissao_requerida(can_view_workstations)
def list_workstations(laboratory_id: int):
    """Internal workstation list scoped to a laboratory."""
    inventory_service = InventoryService()
    laboratory = _get_laboratory_or_404(inventory_service, laboratory_id)
    return render_template(
        "workstations/list.html",
        laboratory=laboratory,
        workstations=inventory_service.list_workstations_by_laboratory(laboratory),
    )


@workstations_bp.get("/laboratories/<int:laboratory_id>/workstations/new")
@permissao_requerida(can_manage_workstations)
def new_workstation(laboratory_id: int):
    """Shows the workstation creation form for a laboratory."""
    inventory_service = InventoryService()
    laboratory = _get_laboratory_or_404(inventory_service, laboratory_id)
    return render_template("workstations/new.html", laboratory=laboratory)


@workstations_bp.post("/laboratories/<int:laboratory_id>/workstations/new")
@permissao_requerida(can_manage_workstations)
def create_workstation(laboratory_id: int):
    """Creates a fixed workstation position inside a laboratory."""
    inventory_service = InventoryService()
    laboratory = _get_laboratory_or_404(inventory_service, laboratory_id)
    try:
        workstation = inventory_service.create_workstation(laboratory, request.form)
    except ValueError as exc:
        flash(str(exc), "error")
        return render_template("workstations/new.html", laboratory=laboratory), 400

    flash(f"Workstation created successfully: {workstation.code}", "success")
    return redirect(url_for("workstations.list_workstations", laboratory_id=laboratory.id))


@workstations_bp.get("/workstations/<int:workstation_id>/edit")
@permissao_requerida(can_manage_workstations)
def edit_workstation(workstation_id: int):
    """Shows the edition form for a workstation."""
    inventory_service = InventoryService()
    workstation = _get_workstation_or_404(inventory_service, workstation_id)
    return render_template("workstations/edit.html", workstation=workstation)


@workstations_bp.post("/workstations/<int:workstation_id>/edit")
@permissao_requerida(can_manage_workstations)
def update_workstation(workstation_id: int):
    """Updates workstation code and map position without touching future assets."""
    inventory_service = InventoryService()
    workstation = _get_workstation_or_404(inventory_service, workstation_id)
    try:
        inventory_service.update_workstation(workstation, request.form)
    except ValueError as exc:
        flash(str(exc), "error")
        return render_template("workstations/edit.html", workstation=workstation), 400

    flash("Workstation updated successfully.", "success")
    return redirect(url_for("workstations.list_workstations", laboratory_id=workstation.laboratory_id))


@workstations_bp.post("/workstations/<int:workstation_id>/status")
@permissao_requerida(can_manage_workstations)
def update_workstation_status(workstation_id: int):
    """Soft-deletes or reactivates a workstation through its active flag."""
    inventory_service = InventoryService()
    workstation = _get_workstation_or_404(inventory_service, workstation_id)
    inventory_service.set_workstation_status(workstation, request.form.get("active") == "true")
    flash("Workstation status updated successfully.", "success")
    return redirect(url_for("workstations.list_workstations", laboratory_id=workstation.laboratory_id))


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
