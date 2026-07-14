from pydantic import BaseModel


class EventFinishedMessage(BaseModel):
    event_id: str
    state: str

    @classmethod
    def from_json(cls, payload: bytes) -> "EventFinishedMessage":
        return cls.model_validate_json(payload)
