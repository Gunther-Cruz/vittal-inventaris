from enum import Enum


class PerfilUsuario(Enum):
    PROFESSOR = "PROFESSOR"
    TECNICO = "TECNICO"
    COORDENADOR = "COORDENADOR"


class OperationalStatus(Enum):
    EM_FUNCIONAMENTO = "EM_FUNCIONAMENTO"
    EM_MANUTENCAO = "EM_MANUTENCAO"
    DESATIVADO = "DESATIVADO"
    FUNCIONAL_DESALOCADO = "FUNCIONAL_DESALOCADO"


class DisplayConnection(Enum):
    HDMI = "HDMI"
    VGA = "VGA"
    DISPLAYPORT = "DISPLAYPORT"
    DVI = "DVI"
    USB_C = "USB_C"
    OUTRA = "OUTRA"
