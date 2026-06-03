from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from app.security.decorators import permissao_requerida
from app.security.permissions import can_manage_laboratories, can_view_laboratories
from app.services.inventory_service import InventoryService

laboratories_bp = Blueprint("laboratories", __name__, url_prefix="/laboratories")


@laboratories_bp.get("")
@permissao_requerida(can_view_laboratories)
def list_laboratories():
    """Internal laboratory list for authenticated users."""
    inventory_service = InventoryService()
    return render_template(
        "laboratories/list.html",
        laboratories=inventory_service.list_laboratories(),
    )


@laboratories_bp.get("/new")
@permissao_requerida(can_manage_laboratories)
def new_laboratory():
    """Shows the internal laboratory creation form."""
    return render_template("laboratories/new.html")


@laboratories_bp.post("/new")
@permissao_requerida(can_manage_laboratories)
def create_laboratory():
    """Creates an institutional laboratory through the inventory service."""
    inventory_service = InventoryService()
    try:
        laboratory = inventory_service.create_laboratory(request.form)
    except ValueError as exc:
        flash(str(exc), "error")
        return render_template("laboratories/new.html"), 400

    flash(f"Laboratory created successfully: {laboratory.code}", "success")
    return redirect(url_for("laboratories.list_laboratories"))


@laboratories_bp.get("/<int:laboratory_id>/edit")
@permissao_requerida(can_manage_laboratories)
def edit_laboratory(laboratory_id: int):
    """Shows the internal laboratory edition form."""
    inventory_service = InventoryService()
    laboratory = _get_laboratory_or_404(inventory_service, laboratory_id)
    return render_template("laboratories/edit.html", laboratory=laboratory)


@laboratories_bp.post("/<int:laboratory_id>/edit")
@permissao_requerida(can_manage_laboratories)
def update_laboratory(laboratory_id: int):
    """Updates laboratory data without touching future workstation relations."""
    inventory_service = InventoryService()
    laboratory = _get_laboratory_or_404(inventory_service, laboratory_id)
    try:
        inventory_service.update_laboratory(laboratory, request.form)
    except ValueError as exc:
        flash(str(exc), "error")
        return render_template("laboratories/edit.html", laboratory=laboratory), 400

    flash("Laboratory updated successfully.", "success")
    return redirect(url_for("laboratories.list_laboratories"))


@laboratories_bp.post("/<int:laboratory_id>/status")
@permissao_requerida(can_manage_laboratories)
def update_laboratory_status(laboratory_id: int):
    """Soft-deletes or reactivates a laboratory by changing its active flag."""
    inventory_service = InventoryService()
    laboratory = _get_laboratory_or_404(inventory_service, laboratory_id)
    inventory_service.set_laboratory_status(laboratory, request.form.get("active") == "true")
    flash("Laboratory status updated successfully.", "success")
    return redirect(url_for("laboratories.list_laboratories"))


@laboratories_bp.get("/<int:laboratory_id>/map")
@permissao_requerida(can_view_laboratories)
def internal_laboratory_map(laboratory_id: int):
    """Internal map placeholder that will receive workstation details later."""
    inventory_service = InventoryService()
    laboratory = _get_laboratory_or_404(inventory_service, laboratory_id)
    return render_template("laboratories/map.html", laboratory=laboratory)


def _get_laboratory_or_404(inventory_service: InventoryService, laboratory_id: int):
    try:
        return inventory_service.get_laboratory(laboratory_id)
    except LookupError:
        abort(404)
