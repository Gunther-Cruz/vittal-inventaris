from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from app.domain.enums import ProblemScope
from app.security.decorators import permissao_requerida
from app.security.permissions import can_manage_problem_types, can_view_problem_types
from app.services.problem_type_service import ProblemTypeService

problem_types_bp = Blueprint("problem_types", __name__, url_prefix="/problem-types")


@problem_types_bp.get("")
@permissao_requerida(can_view_problem_types)
def list_problem_types():
    """Lists the internal technical problem taxonomy used by future maintenance flows."""
    problem_type_service = ProblemTypeService()
    filters = {
        "scope": request.args.get("scope", ""),
        "active": request.args.get("active", ""),
    }
    return render_template(
        "problem_types/list.html",
        problem_types=problem_type_service.list_problem_types(filters),
        scopes=ProblemScope,
        selected_scope=filters["scope"],
        selected_active=filters["active"],
    )


@problem_types_bp.get("/new")
@permissao_requerida(can_manage_problem_types)
def new_problem_type():
    """Shows the creation form for a stable maintenance classification."""
    return render_template("problem_types/new.html", scopes=ProblemScope)


@problem_types_bp.post("/new")
@permissao_requerida(can_manage_problem_types)
def create_problem_type():
    """Creates a problem type while validating code range and scope consistency."""
    problem_type_service = ProblemTypeService()
    try:
        problem_type = problem_type_service.create_problem_type(request.form)
    except ValueError as exc:
        flash(str(exc), "error")
        return (
            render_template(
                "problem_types/new.html",
                scopes=ProblemScope,
                form_data=request.form,
            ),
            400,
        )

    flash(f"Problem type created successfully: {problem_type.code}", "success")
    return redirect(url_for("problem_types.list_problem_types"))


@problem_types_bp.get("/<int:problem_type_id>/edit")
@permissao_requerida(can_manage_problem_types)
def edit_problem_type(problem_type_id: int):
    """Shows the edit form. Code and scope stay read-only to preserve statistics."""
    problem_type_service = ProblemTypeService()
    problem_type = _get_problem_type_or_404(problem_type_service, problem_type_id)
    return render_template("problem_types/edit.html", problem_type=problem_type)


@problem_types_bp.post("/<int:problem_type_id>/edit")
@permissao_requerida(can_manage_problem_types)
def update_problem_type(problem_type_id: int):
    """Updates only name and description; code and scope are immutable by design."""
    problem_type_service = ProblemTypeService()
    problem_type = _get_problem_type_or_404(problem_type_service, problem_type_id)
    try:
        problem_type_service.update_problem_type(problem_type, request.form)
    except ValueError as exc:
        flash(str(exc), "error")
        return (
            render_template(
                "problem_types/edit.html",
                problem_type=problem_type,
                form_data=request.form,
            ),
            400,
        )

    flash("Problem type updated successfully.", "success")
    return redirect(url_for("problem_types.list_problem_types"))


@problem_types_bp.post("/<int:problem_type_id>/status")
@permissao_requerida(can_manage_problem_types)
def update_problem_type_status(problem_type_id: int):
    """Soft-disables or reactivates a classification without deleting historical meaning."""
    problem_type_service = ProblemTypeService()
    problem_type = _get_problem_type_or_404(problem_type_service, problem_type_id)
    problem_type_service.set_problem_type_status(problem_type, request.form.get("active") == "true")
    flash("Problem type status updated successfully.", "success")
    return redirect(url_for("problem_types.list_problem_types"))


def _get_problem_type_or_404(problem_type_service: ProblemTypeService, problem_type_id: int):
    try:
        return problem_type_service.get_problem_type(problem_type_id)
    except LookupError:
        abort(404)
