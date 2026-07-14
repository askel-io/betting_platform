from bet_maker.src.errors.domain_error import DomainError


class InvalidAmountError(DomainError):
    pass


class BetAlreadyFinishedError(DomainError):
    pass


class BetNotFoundError(DomainError):
    def __init__(self, bet_id: str) -> None:
        self.bet_id = bet_id
        super().__init__(f"Bet not found: {bet_id}")
