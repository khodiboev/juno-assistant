from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=500,
        examples=["What tech stack does Santa use?"],
    )
    previous_question: str | None = Field(default=None, max_length=500)

    @field_validator("question")
    @classmethod
    def not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("question must not be empty")
        return value

    @field_validator("previous_question")
    @classmethod
    def blank_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or None


class SourceOut(BaseModel):
    source: str
    section: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceOut]
    used_context: bool
    latency_ms: int
