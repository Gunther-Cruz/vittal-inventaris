from collections.abc import Mapping

from app.domain.models import Laboratory
from app.repositories.laboratory_repository import LaboratoryRepository


class InventoryService:
    """Use cases for physical structure, inventory, movements, and asset lifecycle."""

    def __init__(self, laboratory_repository: LaboratoryRepository | None = None) -> None:
        self.laboratory_repository = laboratory_repository or LaboratoryRepository()

    # -------------------------------------------------------------------------
    # Laboratories
    # -------------------------------------------------------------------------

    def create_laboratory(self, data: Mapping[str, object]) -> Laboratory:
        laboratory = self._build_laboratory(data)
        if self.laboratory_repository.find_by_code(laboratory.code) is not None:
            raise ValueError("Laboratory code already exists.")

        return self.laboratory_repository.save(laboratory)

    def update_laboratory(self, laboratory: Laboratory, data: Mapping[str, object]) -> Laboratory:
        code = self._normalize_required_text(data.get("code", ""), "Code is required.").upper()
        existing = self.laboratory_repository.find_by_code(code)
        if existing is not None and existing.id != laboratory.id:
            raise ValueError("Laboratory code already exists.")

        laboratory.code = code
        laboratory.name = self._normalize_required_text(data.get("name", ""), "Name is required.")
        laboratory.pavilion = self._normalize_required_text(
            data.get("pavilion", ""),
            "Pavilion is required.",
        )
        laboratory.notes = self._normalize_optional_text(data.get("notes", ""))
        return self.laboratory_repository.commit(laboratory)

    def set_laboratory_status(self, laboratory: Laboratory, active: bool) -> Laboratory:
        laboratory.active = bool(active)
        return self.laboratory_repository.commit(laboratory)

    def list_laboratories(self) -> list[Laboratory]:
        return self.laboratory_repository.list_all()

    def list_public_laboratories(self) -> list[Laboratory]:
        return self.laboratory_repository.list_active()

    def get_laboratory(self, laboratory_id: int) -> Laboratory:
        laboratory = self.laboratory_repository.find_by_id(laboratory_id)
        if laboratory is None:
            raise LookupError("Laboratory not found.")

        return laboratory

    def _build_laboratory(self, data: Mapping[str, object]) -> Laboratory:
        return Laboratory(
            code=self._normalize_required_text(data.get("code", ""), "Code is required.").upper(),
            name=self._normalize_required_text(data.get("name", ""), "Name is required."),
            pavilion=self._normalize_required_text(
                data.get("pavilion", ""),
                "Pavilion is required.",
            ),
            active=True,
            notes=self._normalize_optional_text(data.get("notes", "")),
        )

    # -------------------------------------------------------------------------
    # Workstations
    # -------------------------------------------------------------------------

    # Workstation use cases will be added after the laboratory module is closed.

    # -------------------------------------------------------------------------
    # Computer cases
    # -------------------------------------------------------------------------

    # Computer case use cases must follow the DER and the class diagram.

    # -------------------------------------------------------------------------
    # Monitors
    # -------------------------------------------------------------------------

    # Monitor use cases will be implemented as a separate asset flow.

    # -------------------------------------------------------------------------
    # Current bindings and movements
    # -------------------------------------------------------------------------

    # Movement use cases will preserve historical allocation records.

    # -------------------------------------------------------------------------
    # Upgrades and disposal
    # -------------------------------------------------------------------------

    # Asset lifecycle use cases will keep traceability by responsible technician.

    # -------------------------------------------------------------------------
    # Inventory queries
    # -------------------------------------------------------------------------

    # Analytical inventory queries must consume VITTAL PostgreSQL data.

    @staticmethod
    def _normalize_required_text(value: object, message: str) -> str:
        normalized = str(value).strip()
        if not normalized:
            raise ValueError(message)

        return normalized

    @staticmethod
    def _normalize_optional_text(value: object) -> str | None:
        normalized = str(value).strip()
        return normalized or None
