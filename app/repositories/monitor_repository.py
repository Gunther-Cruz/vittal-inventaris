from app.domain.models import Monitor
from app.extensions import db


class MonitorRepository:
    """Database access for physical monitors."""

    def find_by_id(self, monitor_id: int) -> Monitor | None:
        return db.session.get(Monitor, monitor_id)

    def find_by_asset_tag(self, asset_tag: str) -> Monitor | None:
        return Monitor.query.filter_by(asset_tag=asset_tag.strip().upper()).first()

    def find_by_serial_number(self, serial_number: str | None) -> Monitor | None:
        normalized = str(serial_number or "").strip().upper()
        if not normalized:
            return None

        return Monitor.query.filter_by(serial_number=normalized).first()

    def list_all(self) -> list[Monitor]:
        return list(Monitor.query.order_by(Monitor.asset_tag.asc()).all())

    def save(self, monitor: Monitor) -> Monitor:
        db.session.add(monitor)
        return self.commit(monitor)

    def commit(self, monitor: Monitor | None = None):
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return monitor
