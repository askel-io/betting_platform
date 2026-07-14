from line_provider.src.errors.domain_error import DomainError


class InvalidCoefficientError(DomainError):
    pass


class InvalidDeadlineError(DomainError):
    pass


class EventAlreadyFinishedError(DomainError):
    pass


class EventNotEditableError(DomainError):
    def __init__(self, event_id: str) -> None:
        self.event_id = event_id
        super().__init__(f"Event is not editable: {event_id}")


class EventNotFoundError(DomainError):
    def __init__(self, event_id: str) -> None:
        self.event_id = event_id
        super().__init__(f"Event not found: {event_id}")
