from app.domain.models import TicketHistory
from app.extensions import db


class TicketHistoryRepository:
    """Database access for ticket lifecycle events."""

    def list_by_ticket(self, ticket_id: int) -> list[TicketHistory]:
        return list(
            TicketHistory.query.filter_by(ticket_id=ticket_id)
            .order_by(TicketHistory.created_at.asc(), TicketHistory.id.asc())
            .all()
        )

    def save(self, history: TicketHistory) -> TicketHistory:
        db.session.add(history)
        return self.commit(history)

    def commit(self, history: TicketHistory | None = None):
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return history
