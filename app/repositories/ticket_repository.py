from app.domain.enums import TicketScope, TicketStatus
from app.domain.models import Ticket
from app.extensions import db


class TicketRepository:
    """Database access for help requests without business decisions."""

    def find_by_id(self, ticket_id: int) -> Ticket | None:
        return db.session.get(Ticket, ticket_id)

    def find_by_protocol(self, protocol: str) -> Ticket | None:
        return Ticket.query.filter_by(protocol=protocol.strip().upper()).first()

    def list_all(self, filters: dict | None = None) -> list[Ticket]:
        query = Ticket.query.order_by(Ticket.created_at.desc())
        filters = filters or {}

        status = filters.get("status")
        if isinstance(status, TicketStatus):
            query = query.filter_by(status=status)

        scope = filters.get("scope")
        if isinstance(scope, TicketScope):
            query = query.filter_by(scope=scope)

        assigned_to_user_id = filters.get("assigned_to_user_id")
        if assigned_to_user_id:
            query = query.filter_by(assigned_to_user_id=assigned_to_user_id)

        return list(query.all())

    def save(self, ticket: Ticket) -> Ticket:
        db.session.add(ticket)
        return self.commit(ticket)

    def commit(self, ticket: Ticket | None = None):
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return ticket
