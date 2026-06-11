from app.domain.models.computer_case_allocation import ComputerCaseAllocation
from app.domain.models.computer_case import ComputerCase
from app.domain.models.it_asset import ITAssetMixin
from app.domain.models.laboratory import Laboratory
from app.domain.models.monitor import Monitor
from app.domain.models.monitor_allocation import MonitorAllocation
from app.domain.models.usuario import Usuario
from app.domain.models.workstation import Workstation

__all__ = [
    "ComputerCase",
    "ComputerCaseAllocation",
    "ITAssetMixin",
    "Laboratory",
    "Monitor",
    "MonitorAllocation",
    "Usuario",
    "Workstation",
]
