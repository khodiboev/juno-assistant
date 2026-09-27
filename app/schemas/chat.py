from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=500,
        examples=["What tech stack does Santa use?"],
    )

    @field_validator("question")
    @classmethod
    def not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("question must not be empty")
        return value


class SourceOut(BaseModel):
    source: str
    section: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceOut]
    used_context: bool
    latency_ms: int
