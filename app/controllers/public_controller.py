from flask import Blueprint, abort, render_template

from app.services.inventory_service import InventoryService

public_bp = Blueprint("public", __name__)


@public_bp.get("/")
def home():
    """Public entry point for users who will locate a lab before opening a ticket."""
    return _render_public_laboratories()


@public_bp.get("/public/laboratories")
def public_laboratories():
    """Semantic public route for the laboratory map/list."""
    return _render_public_laboratories()


@public_bp.get("/public/laboratories/<int:laboratory_id>/workstations")
def public_workstations(laboratory_id: int):
    """Public workstation selection step for a chosen active laboratory."""
    inventory_service = InventoryService()
    laboratory = _get_laboratory_or_404(inventory_service, laboratory_id)
    if not laboratory.active:
        abort(404)

    return render_template(
        "public/workstations.html",
        laboratory=laboratory,
        workstations=inventory_service.list_public_workstations_by_laboratory(laboratory),
    )


def _render_public_laboratories():
    inventory_service = InventoryService()
    return render_template(
        "public/laboratories.html",
        laboratories=inventory_service.list_public_laboratories(),
    )


def _get_laboratory_or_404(inventory_service: InventoryService, laboratory_id: int):
    try:
        return inventory_service.get_laboratory(laboratory_id)
    except LookupError:
        abort(404)
