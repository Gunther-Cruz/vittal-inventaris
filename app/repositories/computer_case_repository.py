from app.domain.models import ComputerCase
from app.extensions import db


class ComputerCaseRepository:
    """Database access for physical computer cases."""

    def find_by_id(self, computer_case_id: int) -> ComputerCase | None:
        return db.session.get(ComputerCase, computer_case_id)

    def find_by_asset_tag(self, asset_tag: str) -> ComputerCase | None:
        return ComputerCase.query.filter_by(asset_tag=asset_tag.strip().upper()).first()

    def find_by_serial_number(self, serial_number: str | None) -> ComputerCase | None:
        normalized = str(serial_number or "").strip().upper()
        if not normalized:
            return None

        return ComputerCase.query.filter_by(serial_number=normalized).first()

    def list_all(self) -> list[ComputerCase]:
        return list(ComputerCase.query.order_by(ComputerCase.asset_tag.asc()).all())

    def save(self, computer_case: ComputerCase) -> ComputerCase:
        db.session.add(computer_case)
        return self.commit(computer_case)

    def commit(self, computer_case: ComputerCase | None = None):
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return computer_case
