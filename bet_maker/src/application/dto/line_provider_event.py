from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class LineProviderEventDTO(BaseModel):
    event_id: str
    coefficient: Decimal
    deadline: datetime
    state: str
    created_at: datetime

    def is_available_for_betting(self, now: datetime) -> bool:
        return self.state == "new" and now < self.deadline
