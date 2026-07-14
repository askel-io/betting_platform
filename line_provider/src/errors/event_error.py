from line_provider.src.errors.domain_error import DomainError


class InvalidCoefficientError(DomainError):
    pass

class InvalidDeadlineError(DomainError):
    pass

class EventAlreadyFinishedError(DomainError):
    pass
