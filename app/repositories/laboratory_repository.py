from app.domain.models import Laboratory
from app.extensions import db


class LaboratoryRepository:
    """Database access for institutional laboratories."""

    def find_by_id(self, laboratory_id: int) -> Laboratory | None:
        return db.session.get(Laboratory, laboratory_id)

    def find_by_code(self, code: str) -> Laboratory | None:
        return Laboratory.query.filter_by(code=code.strip().upper()).first()

    def list_all(self) -> list[Laboratory]:
        return list(Laboratory.query.order_by(Laboratory.code.asc()).all())

    def list_active(self) -> list[Laboratory]:
        return list(
            Laboratory.query.filter_by(active=True)
            .order_by(Laboratory.code.asc())
            .all()
        )

    def save(self, laboratory: Laboratory) -> Laboratory:
        db.session.add(laboratory)
        return self.commit(laboratory)

    def commit(self, laboratory: Laboratory | None = None):
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return laboratory
