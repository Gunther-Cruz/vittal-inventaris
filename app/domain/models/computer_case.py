from app.extensions import db
from app.domain.models.it_asset import ITAssetMixin


class ComputerCase(ITAssetMixin, db.Model):
    """Physical computer case registered in VITTAL inventory."""

    __tablename__ = "gabinete"

    id = db.Column("id_gabinete", db.Integer, primary_key=True)
    batch = db.Column("lote", db.String(120), nullable=True)
    processor_model = db.Column("processador_modelo", db.String(160), nullable=True)
    processor_frequency_ghz = db.Column("processador_frequencia_ghz", db.Numeric(6, 2), nullable=True)
    motherboard_model = db.Column("placa_mae_modelo", db.String(160), nullable=True)
    installed_memory_gb = db.Column("memoria_instalada_gb", db.Numeric(6, 2), nullable=True)
    memory_technology = db.Column("memoria_tecnologia", db.String(80), nullable=True)
    memory_speed_mhz = db.Column("memoria_velocidade_mhz", db.Integer, nullable=True)
    memory_slots_total = db.Column("memoria_slots_total", db.Integer, nullable=True)
    memory_slots_usage = db.Column("memoria_slots_ocupacao", db.String(120), nullable=True)
    storage_description = db.Column("armazenamento_descricao", db.String(255), nullable=True)
    power_supply_description = db.Column("fonte_descricao", db.String(255), nullable=True)
    operating_system = db.Column("sistema_operacional", db.String(160), nullable=True)

    allocations = db.relationship("ComputerCaseAllocation", back_populates="computer_case")

    def __repr__(self) -> str:
        return (
            f"<ComputerCase id={self.id!r} asset_tag={self.asset_tag!r} "
            f"serial_number={self.serial_number!r} operational_status={self.operational_status!r}>"
        )
