import time
from dataclasses import dataclass, field
from typing import Any, Dict

from src.backend.governance.risk_tiering import ActionTier


@dataclass
class ApprovalTicket:
    ticket_id: str
    action: str
    resource: str
    risk_tier: ActionTier
    impact: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    status: str = "PENDING"
    created_at: float = field(default_factory=time.time)


class ApprovalRouter:
    def __init__(self) -> None:
        self._inbox: Dict[str, ApprovalTicket] = {}

    def enqueue(self, ticket: ApprovalTicket) -> None:
        self._inbox[ticket.ticket_id] = ticket

    def get_inbox(self) -> list[ApprovalTicket]:
        return sorted(self._inbox.values(), key=lambda t: t.created_at, reverse=True)

    def decide(self, ticket_id: str, decision: str) -> bool:
        ticket = self._inbox.get(ticket_id)
        if ticket is None:
            return False
        ticket.status = "APPROVED" if decision.upper() == "APPROVED" else "REJECTED"
        return ticket.status == "APPROVED"
