from pydantic import BaseModel


class EventFinishedMessage(BaseModel):
    event_id: str
    state: str

    def to_json(self) -> bytes:
        return self.model_dump_json().encode()

    @classmethod
    def from_json(cls, payload: bytes) -> "EventFinishedMessage":
        return cls.model_validate_json(payload)
