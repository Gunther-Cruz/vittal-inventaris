from app.domain.models import MonitorAllocation
from app.extensions import db


class MonitorAllocationRepository:
    """Database access for monitor allocation history."""

    def find_active_by_monitor(self, monitor_id: int) -> MonitorAllocation | None:
        return MonitorAllocation.query.filter_by(
            monitor_id=monitor_id,
            end_at=None,
        ).first()

    def find_active_by_workstation(self, workstation_id: int) -> MonitorAllocation | None:
        return MonitorAllocation.query.filter_by(
            workstation_id=workstation_id,
            end_at=None,
        ).first()

    def list_active_monitor_ids(self) -> set[int]:
        rows = (
            db.session.query(MonitorAllocation.monitor_id)
            .filter(MonitorAllocation.end_at.is_(None))
            .all()
        )
        return {monitor_id for (monitor_id,) in rows}

    def list_by_monitor(self, monitor_id: int) -> list[MonitorAllocation]:
        return list(
            MonitorAllocation.query.filter_by(monitor_id=monitor_id)
            .order_by(MonitorAllocation.start_at.desc())
            .all()
        )

    def list_by_workstation(self, workstation_id: int) -> list[MonitorAllocation]:
        return list(
            MonitorAllocation.query.filter_by(workstation_id=workstation_id)
            .order_by(MonitorAllocation.start_at.desc())
            .all()
        )

    def save(self, allocation: MonitorAllocation) -> MonitorAllocation:
        db.session.add(allocation)
        return self.commit(allocation)

    def commit(self, allocation: MonitorAllocation | None = None):
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return allocation
