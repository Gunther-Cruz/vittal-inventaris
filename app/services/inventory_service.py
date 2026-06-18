from collections.abc import Mapping
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation

from app.domain.enums import DisplayConnection, OperationalStatus
from app.domain.models import (
    ComputerCase,
    ComputerCaseAllocation,
    Laboratory,
    Monitor,
    MonitorAllocation,
    Usuario,
    Workstation,
)
from app.extensions import db
from app.repositories.computer_case_allocation_repository import ComputerCaseAllocationRepository
from app.repositories.computer_case_repository import ComputerCaseRepository
from app.repositories.laboratory_repository import LaboratoryRepository
from app.repositories.monitor_allocation_repository import MonitorAllocationRepository
from app.repositories.monitor_repository import MonitorRepository
from app.repositories.workstation_repository import WorkstationRepository


class InventoryService:
    """Use cases for physical structure, inventory, movements, and asset lifecycle."""

    ASSIGNED_STATUS_CHANGE_MESSAGE = (
        "Assigned assets must have their status changed through unassignment or service order."
    )
    MANUAL_STATUS_CHANGE_MESSAGE = (
        "Asset status must be changed through assignment, unassignment, or service order."
    )
    WORKSTATION_MAP_COLUMNS = 4

    def __init__(
        self,
        laboratory_repository: LaboratoryRepository | None = None,
        workstation_repository: WorkstationRepository | None = None,
        computer_case_repository: ComputerCaseRepository | None = None,
        monitor_repository: MonitorRepository | None = None,
        computer_case_allocation_repository: ComputerCaseAllocationRepository | None = None,
        monitor_allocation_repository: MonitorAllocationRepository | None = None,
    ) -> None:
        self.laboratory_repository = laboratory_repository or LaboratoryRepository()
        self.workstation_repository = workstation_repository or WorkstationRepository()
        self.computer_case_repository = computer_case_repository or ComputerCaseRepository()
        self.monitor_repository = monitor_repository or MonitorRepository()
        self.computer_case_allocation_repository = (
            computer_case_allocation_repository or ComputerCaseAllocationRepository()
        )
        self.monitor_allocation_repository = monitor_allocation_repository or MonitorAllocationRepository()

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
        map_position_x, map_position_y = self._calculate_next_workstation_position(laboratory)
        return Workstation(
            laboratory_id=laboratory.id,
            code=self._normalize_required_text(data.get("code", ""), "Code is required.").upper(),
            map_position_x=map_position_x,
            map_position_y=map_position_y,
            active=True,
            notes=self._normalize_optional_text(data.get("notes", "")),
        )

    def _calculate_next_workstation_position(self, laboratory: Laboratory) -> tuple[int, int]:
        workstations = self.workstation_repository.list_by_laboratory(laboratory.id)
        next_index = len(workstations)
        x = (next_index % self.WORKSTATION_MAP_COLUMNS) + 1
        y = (next_index // self.WORKSTATION_MAP_COLUMNS) + 1
        return x, y

    # -------------------------------------------------------------------------
    # Computer cases
    # -------------------------------------------------------------------------

    def create_computer_case(self, data: Mapping[str, object]) -> ComputerCase:
        self._reject_manual_operational_status(data)
        computer_case = self._build_computer_case(data)
        self._ensure_unique_computer_case_identifiers(computer_case)
        return self.computer_case_repository.save(computer_case)

    def update_computer_case(
        self,
        computer_case: ComputerCase,
        data: Mapping[str, object],
    ) -> ComputerCase:
        self._reject_manual_operational_status(data)
        self._apply_computer_case_data(computer_case, data)
        self._ensure_unique_computer_case_identifiers(computer_case)
        return self.computer_case_repository.commit(computer_case)

    def set_computer_case_status(
        self,
        computer_case: ComputerCase,
        operational_status: object,
    ) -> ComputerCase:
        raise ValueError(self.MANUAL_STATUS_CHANGE_MESSAGE)

    def list_computer_cases(self) -> list[ComputerCase]:
        return self.computer_case_repository.list_all()

    def list_available_computer_cases(self) -> list[ComputerCase]:
        return [
            computer_case
            for computer_case in self.computer_case_repository.list_all()
            if computer_case.operational_status == OperationalStatus.FUNCIONAL_DESALOCADO
            and self.computer_case_allocation_repository.find_active_by_computer_case(computer_case.id) is None
        ]

    def list_assigned_computer_case_ids(self) -> set[int]:
        return self.computer_case_allocation_repository.list_active_computer_case_ids()

    def get_computer_case(self, computer_case_id: int) -> ComputerCase:
        computer_case = self.computer_case_repository.find_by_id(computer_case_id)
        if computer_case is None:
            raise LookupError("Computer case not found.")

        return computer_case

    def _build_computer_case(self, data: Mapping[str, object]) -> ComputerCase:
        computer_case = ComputerCase()
        self._apply_computer_case_data(computer_case, data)
        return computer_case

    def _apply_computer_case_data(
        self,
        computer_case: ComputerCase,
        data: Mapping[str, object],
    ) -> None:
        computer_case.asset_tag = self._normalize_required_text(
            data.get("asset_tag", ""),
            "Asset tag is required.",
        ).upper()
        computer_case.serial_number = self._normalize_optional_text(
            data.get("serial_number", ""),
            uppercase=True,
        )
        computer_case.manufacturer = self._normalize_required_text(
            data.get("manufacturer", ""),
            "Manufacturer is required.",
        )
        computer_case.model = self._normalize_required_text(data.get("model", ""), "Model is required.")
        computer_case.batch = self._normalize_optional_text(data.get("batch", ""))
        computer_case.purchase_date = self._normalize_optional_date(data.get("purchase_date", ""))
        computer_case.processor_model = self._normalize_optional_text(data.get("processor_model", ""))
        computer_case.processor_frequency_ghz = self._normalize_optional_decimal(
            data.get("processor_frequency_ghz", ""),
            "Processor frequency must be a valid decimal number.",
        )
        computer_case.motherboard_model = self._normalize_optional_text(data.get("motherboard_model", ""))
        computer_case.installed_memory_gb = self._normalize_optional_decimal(
            data.get("installed_memory_gb", ""),
            "Installed memory must be a valid decimal number.",
        )
        computer_case.memory_technology = self._normalize_optional_text(data.get("memory_technology", ""))
        computer_case.memory_speed_mhz = self._normalize_optional_int(
            data.get("memory_speed_mhz", ""),
            "Memory speed must be an integer.",
        )
        computer_case.memory_slots_total = self._normalize_optional_int(
            data.get("memory_slots_total", ""),
            "Memory slot total must be an integer.",
        )
        computer_case.memory_slots_usage = self._normalize_optional_text(data.get("memory_slots_usage", ""))
        computer_case.storage_description = self._normalize_optional_text(data.get("storage_description", ""))
        computer_case.power_supply_description = self._normalize_optional_text(
            data.get("power_supply_description", ""),
        )
        computer_case.operating_system = self._normalize_optional_text(data.get("operating_system", ""))
        if computer_case.operational_status is None:
            computer_case.operational_status = OperationalStatus.FUNCIONAL_DESALOCADO
        computer_case.notes = self._normalize_optional_text(data.get("notes", ""))

    def _ensure_unique_computer_case_identifiers(self, computer_case: ComputerCase) -> None:
        existing_asset = self.computer_case_repository.find_by_asset_tag(computer_case.asset_tag)
        if existing_asset is not None and existing_asset.id != computer_case.id:
            raise ValueError("Asset tag already exists.")

        existing_serial = self.computer_case_repository.find_by_serial_number(computer_case.serial_number)
        if existing_serial is not None and existing_serial.id != computer_case.id:
            raise ValueError("Serial number already exists.")

    # -------------------------------------------------------------------------
    # Monitors
    # -------------------------------------------------------------------------

    def create_monitor(self, data: Mapping[str, object]) -> Monitor:
        self._reject_manual_operational_status(data)
        monitor = self._build_monitor(data)
        self._ensure_unique_monitor_identifiers(monitor)
        return self.monitor_repository.save(monitor)

    def update_monitor(self, monitor: Monitor, data: Mapping[str, object]) -> Monitor:
        self._reject_manual_operational_status(data)
        self._apply_monitor_data(monitor, data)
        self._ensure_unique_monitor_identifiers(monitor)
        return self.monitor_repository.commit(monitor)

    def set_monitor_status(self, monitor: Monitor, operational_status: object) -> Monitor:
        raise ValueError(self.MANUAL_STATUS_CHANGE_MESSAGE)

    def list_monitors(self) -> list[Monitor]:
        return self.monitor_repository.list_all()

    def list_available_monitors(self) -> list[Monitor]:
        return [
            monitor
            for monitor in self.monitor_repository.list_all()
            if monitor.operational_status == OperationalStatus.FUNCIONAL_DESALOCADO
            and self.monitor_allocation_repository.find_active_by_monitor(monitor.id) is None
        ]

    def list_assigned_monitor_ids(self) -> set[int]:
        return self.monitor_allocation_repository.list_active_monitor_ids()

    def get_monitor(self, monitor_id: int) -> Monitor:
        monitor = self.monitor_repository.find_by_id(monitor_id)
        if monitor is None:
            raise LookupError("Monitor not found.")

        return monitor

    def _build_monitor(self, data: Mapping[str, object]) -> Monitor:
        monitor = Monitor()
        self._apply_monitor_data(monitor, data)
        return monitor

    def _apply_monitor_data(self, monitor: Monitor, data: Mapping[str, object]) -> None:
        monitor.asset_tag = self._normalize_required_text(
            data.get("asset_tag", ""),
            "Asset tag is required.",
        ).upper()
        monitor.serial_number = self._normalize_optional_text(
            data.get("serial_number", ""),
            uppercase=True,
        )
        monitor.manufacturer = self._normalize_required_text(
            data.get("manufacturer", ""),
            "Manufacturer is required.",
        )
        monitor.model = self._normalize_required_text(data.get("model", ""), "Model is required.")
        monitor.purchase_date = self._normalize_optional_date(data.get("purchase_date", ""))
        monitor.screen_size_inches = self._normalize_optional_decimal(
            data.get("screen_size_inches", ""),
            "Screen size must be a valid decimal number.",
        )
        monitor.display_connection = self._normalize_display_connection(data.get("display_connection", ""))
        if monitor.operational_status is None:
            monitor.operational_status = OperationalStatus.FUNCIONAL_DESALOCADO
        monitor.notes = self._normalize_optional_text(data.get("notes", ""))

    def _ensure_unique_monitor_identifiers(self, monitor: Monitor) -> None:
        existing_asset = self.monitor_repository.find_by_asset_tag(monitor.asset_tag)
        if existing_asset is not None and existing_asset.id != monitor.id:
            raise ValueError("Asset tag already exists.")

        existing_serial = self.monitor_repository.find_by_serial_number(monitor.serial_number)
        if existing_serial is not None and existing_serial.id != monitor.id:
            raise ValueError("Serial number already exists.")

    # -------------------------------------------------------------------------
    # Current bindings and movements
    # -------------------------------------------------------------------------

    def assign_computer_case_to_workstation(
        self,
        computer_case: ComputerCase,
        workstation: Workstation,
        technician: Usuario,
        data: Mapping[str, object],
    ) -> ComputerCaseAllocation:
        self._ensure_can_assign_asset_to_workstation(workstation, computer_case, "computer case")
        if workstation.current_computer_case_id is not None:
            raise ValueError("Workstation already has a computer case.")
        if self.computer_case_allocation_repository.find_active_by_computer_case(computer_case.id):
            raise ValueError("Computer case already has an active allocation.")

        allocation = ComputerCaseAllocation(
            computer_case_id=computer_case.id,
            workstation_id=workstation.id,
            technician_id=technician.id,
            movement_reason=self._normalize_required_text(
                data.get("movement_reason", ""),
                "Movement reason is required.",
            ),
            notes=self._normalize_optional_text(data.get("notes", "")),
        )
        workstation.current_computer_case = computer_case
        computer_case.operational_status = OperationalStatus.EM_FUNCIONAMENTO
        db.session.add(allocation)
        return self.computer_case_allocation_repository.commit(allocation)

    def unassign_computer_case_from_workstation(
        self,
        workstation: Workstation,
        technician: Usuario,
        data: Mapping[str, object],
    ) -> ComputerCaseAllocation:
        if workstation.current_computer_case_id is None or workstation.current_computer_case is None:
            raise ValueError("Workstation has no computer case.")

        allocation = self.computer_case_allocation_repository.find_active_by_workstation(workstation.id)
        if allocation is None or allocation.computer_case_id != workstation.current_computer_case_id:
            raise ValueError("Active computer case allocation not found.")

        new_status = self._normalize_unassignment_status(data.get("operational_status", ""))
        allocation.end_at = datetime.now(timezone.utc)
        allocation.movement_reason = self._normalize_required_text(
            data.get("movement_reason", ""),
            "Movement reason is required.",
        )
        allocation.notes = self._normalize_optional_text(data.get("notes", ""))
        workstation.current_computer_case.operational_status = new_status
        workstation.current_computer_case = None
        return self.computer_case_allocation_repository.commit(allocation)

    def assign_monitor_to_workstation(
        self,
        monitor: Monitor,
        workstation: Workstation,
        technician: Usuario,
        data: Mapping[str, object],
    ) -> MonitorAllocation:
        self._ensure_can_assign_asset_to_workstation(workstation, monitor, "monitor")
        if workstation.current_monitor_id is not None:
            raise ValueError("Workstation already has a monitor.")
        if self.monitor_allocation_repository.find_active_by_monitor(monitor.id):
            raise ValueError("Monitor already has an active allocation.")

        allocation = MonitorAllocation(
            monitor_id=monitor.id,
            workstation_id=workstation.id,
            technician_id=technician.id,
            movement_reason=self._normalize_required_text(
                data.get("movement_reason", ""),
                "Movement reason is required.",
            ),
            notes=self._normalize_optional_text(data.get("notes", "")),
        )
        workstation.current_monitor = monitor
        monitor.operational_status = OperationalStatus.EM_FUNCIONAMENTO
        db.session.add(allocation)
        return self.monitor_allocation_repository.commit(allocation)

    def unassign_monitor_from_workstation(
        self,
        workstation: Workstation,
        technician: Usuario,
        data: Mapping[str, object],
    ) -> MonitorAllocation:
        if workstation.current_monitor_id is None or workstation.current_monitor is None:
            raise ValueError("Workstation has no monitor.")

        allocation = self.monitor_allocation_repository.find_active_by_workstation(workstation.id)
        if allocation is None or allocation.monitor_id != workstation.current_monitor_id:
            raise ValueError("Active monitor allocation not found.")

        new_status = self._normalize_unassignment_status(data.get("operational_status", ""))
        allocation.end_at = datetime.now(timezone.utc)
        allocation.movement_reason = self._normalize_required_text(
            data.get("movement_reason", ""),
            "Movement reason is required.",
        )
        allocation.notes = self._normalize_optional_text(data.get("notes", ""))
        workstation.current_monitor.operational_status = new_status
        workstation.current_monitor = None
        return self.monitor_allocation_repository.commit(allocation)

    def list_computer_case_allocations(self, computer_case: ComputerCase) -> list[ComputerCaseAllocation]:
        return self.computer_case_allocation_repository.list_by_computer_case(computer_case.id)

    def list_monitor_allocations(self, monitor: Monitor) -> list[MonitorAllocation]:
        return self.monitor_allocation_repository.list_by_monitor(monitor.id)

    def list_workstation_computer_case_allocations(
        self,
        workstation: Workstation,
    ) -> list[ComputerCaseAllocation]:
        return self.computer_case_allocation_repository.list_by_workstation(workstation.id)

    def list_workstation_monitor_allocations(self, workstation: Workstation) -> list[MonitorAllocation]:
        return self.monitor_allocation_repository.list_by_workstation(workstation.id)

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
    def _normalize_optional_text(value: object, uppercase: bool = False) -> str | None:
        normalized = str(value).strip()
        if uppercase:
            normalized = normalized.upper()

        return normalized or None

    @staticmethod
    def _normalize_optional_int(value: object, message: str = "Map positions must be integers.") -> int | None:
        normalized = str(value).strip()
        if not normalized:
            return None

        try:
            return int(normalized)
        except ValueError as exc:
            raise ValueError(message) from exc

    @staticmethod
    def _normalize_optional_decimal(value: object, message: str) -> Decimal | None:
        normalized = str(value).strip().replace(",", ".")
        if not normalized:
            return None

        try:
            return Decimal(normalized)
        except InvalidOperation as exc:
            raise ValueError(message) from exc

    @staticmethod
    def _normalize_optional_date(value: object) -> date | None:
        normalized = str(value).strip()
        if not normalized:
            return None

        try:
            return date.fromisoformat(normalized)
        except ValueError as exc:
            raise ValueError("Purchase date must use YYYY-MM-DD.") from exc

    @staticmethod
    def _normalize_operational_status(value: object) -> OperationalStatus:
        normalized = str(value).strip().upper()
        try:
            return OperationalStatus(normalized)
        except ValueError as exc:
            raise ValueError("Invalid operational status.") from exc

    @staticmethod
    def _normalize_unassignment_status(value: object) -> OperationalStatus:
        status = InventoryService._normalize_operational_status(value)
        if status not in (
            OperationalStatus.FUNCIONAL_DESALOCADO,
            OperationalStatus.EM_MANUTENCAO,
            OperationalStatus.DESATIVADO,
        ):
            raise ValueError("Invalid unassignment status.")

        return status

    @staticmethod
    def _ensure_unassigned_asset_status(status: OperationalStatus) -> None:
        if status == OperationalStatus.EM_FUNCIONAMENTO:
            raise ValueError("Unassigned assets cannot be in operation.")

    def _reject_manual_operational_status(self, data: Mapping[str, object]) -> None:
        if "operational_status" in data:
            raise ValueError(self.MANUAL_STATUS_CHANGE_MESSAGE)

    def _ensure_computer_case_status_is_consistent(self, computer_case: ComputerCase) -> None:
        active_allocation = self.computer_case_allocation_repository.find_active_by_computer_case(computer_case.id)
        if computer_case.operational_status == OperationalStatus.EM_FUNCIONAMENTO and active_allocation is None:
            raise ValueError("Computer case in operation must be assigned to a workstation.")

    def _ensure_monitor_status_is_consistent(self, monitor: Monitor) -> None:
        active_allocation = self.monitor_allocation_repository.find_active_by_monitor(monitor.id)
        if monitor.operational_status == OperationalStatus.EM_FUNCIONAMENTO and active_allocation is None:
            raise ValueError("Monitor in operation must be assigned to a workstation.")

    def _ensure_computer_case_status_change_is_allowed(
        self,
        computer_case: ComputerCase,
        requested_status: OperationalStatus,
    ) -> None:
        has_active_allocation = self._computer_case_has_active_allocation(computer_case)
        if has_active_allocation and requested_status != computer_case.operational_status:
            raise ValueError(self.ASSIGNED_STATUS_CHANGE_MESSAGE)

        if not has_active_allocation:
            self._ensure_unassigned_asset_status(requested_status)

    def _ensure_monitor_status_change_is_allowed(
        self,
        monitor: Monitor,
        requested_status: OperationalStatus,
    ) -> None:
        has_active_allocation = self._monitor_has_active_allocation(monitor)
        if has_active_allocation and requested_status != monitor.operational_status:
            raise ValueError(self.ASSIGNED_STATUS_CHANGE_MESSAGE)

        if not has_active_allocation:
            self._ensure_unassigned_asset_status(requested_status)

    def _computer_case_has_active_allocation(self, computer_case: ComputerCase) -> bool:
        if computer_case.id is None:
            return False

        return self.computer_case_allocation_repository.find_active_by_computer_case(computer_case.id) is not None

    def _monitor_has_active_allocation(self, monitor: Monitor) -> bool:
        if monitor.id is None:
            return False

        return self.monitor_allocation_repository.find_active_by_monitor(monitor.id) is not None

    def _ensure_can_assign_asset_to_workstation(
        self,
        workstation: Workstation,
        asset: ComputerCase | Monitor,
        asset_label: str,
    ) -> None:
        if not workstation.active:
            raise ValueError("Inactive workstations cannot receive assets.")
        if asset.operational_status != OperationalStatus.FUNCIONAL_DESALOCADO:
            raise ValueError(f"Only unassigned functional {asset_label}s can be assigned.")

    @staticmethod
    def _normalize_display_connection(value: object) -> DisplayConnection | None:
        normalized = str(value).strip().upper()
        if not normalized:
            return None

        try:
            return DisplayConnection(normalized)
        except ValueError as exc:
            raise ValueError("Invalid display connection.") from exc
