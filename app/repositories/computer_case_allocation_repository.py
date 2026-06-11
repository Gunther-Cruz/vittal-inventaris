from app.domain.models import ComputerCaseAllocation
from app.extensions import db


class ComputerCaseAllocationRepository:
    """Database access for computer case allocation history."""

    def find_active_by_computer_case(self, computer_case_id: int) -> ComputerCaseAllocation | None:
        return ComputerCaseAllocation.query.filter_by(
            computer_case_id=computer_case_id,
            end_at=None,
        ).first()

    def find_active_by_workstation(self, workstation_id: int) -> ComputerCaseAllocation | None:
        return ComputerCaseAllocation.query.filter_by(
            workstation_id=workstation_id,
            end_at=None,
        ).first()

    def list_active_computer_case_ids(self) -> set[int]:
        rows = (
            db.session.query(ComputerCaseAllocation.computer_case_id)
            .filter(ComputerCaseAllocation.end_at.is_(None))
            .all()
        )
        return {computer_case_id for (computer_case_id,) in rows}

    def list_by_computer_case(self, computer_case_id: int) -> list[ComputerCaseAllocation]:
        return list(
            ComputerCaseAllocation.query.filter_by(computer_case_id=computer_case_id)
            .order_by(ComputerCaseAllocation.start_at.desc())
            .all()
        )

    def list_by_workstation(self, workstation_id: int) -> list[ComputerCaseAllocation]:
        return list(
            ComputerCaseAllocation.query.filter_by(workstation_id=workstation_id)
            .order_by(ComputerCaseAllocation.start_at.desc())
            .all()
        )

    def save(self, allocation: ComputerCaseAllocation) -> ComputerCaseAllocation:
        db.session.add(allocation)
        return self.commit(allocation)

    def commit(self, allocation: ComputerCaseAllocation | None = None):
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return allocation
