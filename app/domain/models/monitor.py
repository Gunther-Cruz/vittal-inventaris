from app.domain.enums import DisplayConnection
from app.domain.models.it_asset import ITAssetMixin
from app.extensions import db


class Monitor(ITAssetMixin, db.Model):
    """Physical monitor registered as a standalone IT asset."""

    __tablename__ = "monitor"

    id = db.Column("id_monitor", db.Integer, primary_key=True)
    screen_size_inches = db.Column("polegadas", db.Numeric(5, 2), nullable=True)
    display_connection = db.Column(
        "tipo_conexao",
        db.Enum(DisplayConnection, name="tipo_conexao_monitor", native_enum=False, length=40),
        nullable=True,
    )

    def __repr__(self) -> str:
        return (
            f"<Monitor id={self.id!r} asset_tag={self.asset_tag!r} "
            f"serial_number={self.serial_number!r} operational_status={self.operational_status!r}>"
        )
