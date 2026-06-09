from collections.abc import Mapping
from datetime import date
from decimal import Decimal, InvalidOperation

from app.domain.enums import DisplayConnection, OperationalStatus
from app.domain.models import ComputerCase, Laboratory, Monitor, Workstation
from app.repositories.computer_case_repository import ComputerCaseRepository
from app.repositories.laboratory_repository import LaboratoryRepository
from app.repositories.monitor_repository import MonitorRepository
from app.repositories.workstation_repository import WorkstationRepository


class InventoryService:
    """Use cases for physical structure, inventory, movements, and asset lifecycle."""

    def __init__(
        self,
        laboratory_repository: LaboratoryRepository | None = None,
        workstation_repository: WorkstationRepository | None = None,
        computer_case_repository: ComputerCaseRepository | None = None,
        monitor_repository: MonitorRepository | None = None,
    ) -> None:
        self.laboratory_repository = laboratory_repository or LaboratoryRepository()
        self.workstation_repository = workstation_repository or WorkstationRepository()
        self.computer_case_repository = computer_case_repository or ComputerCaseRepository()
        self.monitor_repository = monitor_repository or MonitorRepository()

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

    def create_computer_case(self, data: Mapping[str, object]) -> ComputerCase:
        computer_case = self._build_computer_case(data)
        self._ensure_unique_computer_case_identifiers(computer_case)
        return self.computer_case_repository.save(computer_case)

    def update_computer_case(
        self,
        computer_case: ComputerCase,
        data: Mapping[str, object],
    ) -> ComputerCase:
        self._apply_computer_case_data(computer_case, data)
        self._ensure_unique_computer_case_identifiers(computer_case)
        return self.computer_case_repository.commit(computer_case)

    def set_computer_case_status(
        self,
        computer_case: ComputerCase,
        operational_status: object,
    ) -> ComputerCase:
        computer_case.operational_status = self._normalize_operational_status(operational_status)
        return self.computer_case_repository.commit(computer_case)

    def list_computer_cases(self) -> list[ComputerCase]:
        return self.computer_case_repository.list_all()

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
        computer_case.operational_status = self._normalize_operational_status(
            data.get("operational_status", OperationalStatus.EM_FUNCIONAMENTO.value),
        )
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
        monitor = self._build_monitor(data)
        self._ensure_unique_monitor_identifiers(monitor)
        return self.monitor_repository.save(monitor)

    def update_monitor(self, monitor: Monitor, data: Mapping[str, object]) -> Monitor:
        self._apply_monitor_data(monitor, data)
        self._ensure_unique_monitor_identifiers(monitor)
        return self.monitor_repository.commit(monitor)

    def set_monitor_status(self, monitor: Monitor, operational_status: object) -> Monitor:
        monitor.operational_status = self._normalize_operational_status(operational_status)
        return self.monitor_repository.commit(monitor)

    def list_monitors(self) -> list[Monitor]:
        return self.monitor_repository.list_all()

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
        monitor.operational_status = self._normalize_operational_status(
            data.get("operational_status", OperationalStatus.EM_FUNCIONAMENTO.value),
        )
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
    def _normalize_display_connection(value: object) -> DisplayConnection | None:
        normalized = str(value).strip().upper()
        if not normalized:
            return None

        try:
            return DisplayConnection(normalized)
        except ValueError as exc:
            raise ValueError("Invalid display connection.") from exc
