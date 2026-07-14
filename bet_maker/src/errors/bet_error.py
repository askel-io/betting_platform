from bet_maker.src.errors.domain_error import DomainError


class InvalidAmountError(DomainError):
    pass


class BetAlreadyFinishedError(DomainError):
    pass


class BetNotFoundError(DomainError):
    def __init__(self, bet_id: str) -> None:
        self.bet_id = bet_id
        super().__init__(f"Bet not found: {bet_id}")


class EventNotFoundError(DomainError):
    def __init__(self, event_id: str) -> None:
        self.event_id = event_id
        super().__init__(f"Event not found: {event_id}")


class EventNotAvailableError(DomainError):
    def __init__(self, event_id: str) -> None:
        self.event_id = event_id
        super().__init__(f"Event is not available for betting: {event_id}")
