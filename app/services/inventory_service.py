from collections.abc import Mapping

from app.domain.models import Laboratory, Workstation
from app.repositories.laboratory_repository import LaboratoryRepository
from app.repositories.workstation_repository import WorkstationRepository


class InventoryService:
    """Use cases for physical structure, inventory, movements, and asset lifecycle."""

    def __init__(
        self,
        laboratory_repository: LaboratoryRepository | None = None,
        workstation_repository: WorkstationRepository | None = None,
    ) -> None:
        self.laboratory_repository = laboratory_repository or LaboratoryRepository()
        self.workstation_repository = workstation_repository or WorkstationRepository()

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

    def create_workstation(self, laboratory: Laboratory, data: Mapping[str, object]) -> Workstation:
        workstation = self._build_workstation(laboratory, data)
        if self.workstation_repository.find_by_code_in_laboratory(laboratory.id, workstation.code):
            raise ValueError("Workstation code already exists in this laboratory.")

        return self.workstation_repository.save(workstation)

    def update_workstation(self, workstation: Workstation, data: Mapping[str, object]) -> Workstation:
        code = self._normalize_required_text(data.get("code", ""), "Code is required.").upper()
        existing = self.workstation_repository.find_by_code_in_laboratory(
            workstation.laboratory_id,
            code,
        )
        if existing is not None and existing.id != workstation.id:
            raise ValueError("Workstation code already exists in this laboratory.")

        workstation.code = code
        workstation.map_position_x = self._normalize_optional_int(data.get("map_position_x", ""))
        workstation.map_position_y = self._normalize_optional_int(data.get("map_position_y", ""))
        workstation.notes = self._normalize_optional_text(data.get("notes", ""))
        return self.workstation_repository.commit(workstation)

    def set_workstation_status(self, workstation: Workstation, active: bool) -> Workstation:
        workstation.active = bool(active)
        return self.workstation_repository.commit(workstation)

    def list_workstations_by_laboratory(self, laboratory: Laboratory) -> list[Workstation]:
        return self.workstation_repository.list_by_laboratory(laboratory.id)

    def list_public_workstations_by_laboratory(self, laboratory: Laboratory) -> list[Workstation]:
        if not laboratory.active:
            return []

        return self.workstation_repository.list_active_by_laboratory(laboratory.id)

    def get_workstation(self, workstation_id: int) -> Workstation:
        workstation = self.workstation_repository.find_by_id(workstation_id)
        if workstation is None:
            raise LookupError("Workstation not found.")

        return workstation

    def _build_workstation(self, laboratory: Laboratory, data: Mapping[str, object]) -> Workstation:
        return Workstation(
            laboratory_id=laboratory.id,
            code=self._normalize_required_text(data.get("code", ""), "Code is required.").upper(),
            map_position_x=self._normalize_optional_int(data.get("map_position_x", "")),
            map_position_y=self._normalize_optional_int(data.get("map_position_y", "")),
            active=True,
            notes=self._normalize_optional_text(data.get("notes", "")),
        )

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

    @staticmethod
    def _normalize_optional_int(value: object) -> int | None:
        normalized = str(value).strip()
        if not normalized:
            return None

        try:
            return int(normalized)
        except ValueError as exc:
            raise ValueError("Map positions must be integers.") from exc
