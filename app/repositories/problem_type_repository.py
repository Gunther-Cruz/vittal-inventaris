from app.domain.enums import ProblemScope
from app.domain.models import ProblemType
from app.extensions import db


class ProblemTypeRepository:
    """Database access for technical maintenance problem classifications."""

    def find_by_id(self, problem_type_id: int) -> ProblemType | None:
        return db.session.get(ProblemType, problem_type_id)

    def find_by_code(self, code: int) -> ProblemType | None:
        return ProblemType.query.filter_by(code=code).first()

    def list_all(self, filters: dict | None = None) -> list[ProblemType]:
        query = ProblemType.query.order_by(ProblemType.code.asc())
        filters = filters or {}

        scope = filters.get("scope")
        if scope is not None:
            query = query.filter_by(scope=scope)

        active = filters.get("active")
        if active is not None:
            query = query.filter_by(active=active)

        return list(query.all())

    def list_active_by_scope(self, scope: ProblemScope) -> list[ProblemType]:
        return list(
            ProblemType.query.filter_by(scope=scope, active=True)
            .order_by(ProblemType.code.asc())
            .all()
        )

    def save(self, problem_type: ProblemType) -> ProblemType:
        db.session.add(problem_type)
        return self.commit(problem_type)

    def commit(self, problem_type: ProblemType | None = None):
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return problem_type
