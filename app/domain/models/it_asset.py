from app.domain.enums import OperationalStatus
from app.extensions import db


class ITAssetMixin:
    """Abstract code-level implementation of AtivoTI shared by concrete assets.

    This mixin intentionally does not create an `ativo_ti` table. Each concrete
    asset keeps its own table from the DER while reusing the common domain
    attributes in Python.
    """

    asset_tag = db.Column("num_patrimonio", db.String(80), nullable=False, unique=True, index=True)
    serial_number = db.Column("numero_serie", db.String(120), nullable=True, unique=True, index=True)
    manufacturer = db.Column("fabricante", db.String(120), nullable=False)
    model = db.Column("modelo", db.String(120), nullable=False)
    purchase_date = db.Column("data_compra", db.Date, nullable=True)
    operational_status = db.Column(
        "situacao_operacional",
        db.Enum(OperationalStatus, name="situacao_operacional_ativo", native_enum=False, length=40),
        nullable=False,
    )
    notes = db.Column("observacao", db.Text, nullable=True)


