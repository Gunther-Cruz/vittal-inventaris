from app.domain.models import Workstation
from app.extensions import db


class WorkstationRepository:
    """Database access for fixed workstation positions."""

    def find_by_id(self, workstation_id: int) -> Workstation | None:
        return db.session.get(Workstation, workstation_id)

    def find_by_code_in_laboratory(self, laboratory_id: int, code: str) -> Workstation | None:
        return Workstation.query.filter_by(
            laboratory_id=laboratory_id,
            code=code.strip().upper(),
        ).first()

    def list_by_laboratory(self, laboratory_id: int) -> list[Workstation]:
        return list(
            Workstation.query.filter_by(laboratory_id=laboratory_id)
            .order_by(Workstation.code.asc())
            .all()
        )

    def list_active_by_laboratory(self, laboratory_id: int) -> list[Workstation]:
        return list(
            Workstation.query.filter_by(laboratory_id=laboratory_id, active=True)
            .order_by(Workstation.code.asc())
            .all()
        )

    def save(self, workstation: Workstation) -> Workstation:
        db.session.add(workstation)
        return self.commit(workstation)

    def commit(self, workstation: Workstation | None = None):
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return workstation
