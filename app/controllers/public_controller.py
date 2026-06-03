from flask import Blueprint, render_template

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


def _render_public_laboratories():
    inventory_service = InventoryService()
    return render_template(
        "public/laboratories.html",
        laboratories=inventory_service.list_public_laboratories(),
    )
