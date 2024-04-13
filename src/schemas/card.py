from pydantic import BaseModel


class CardCreateSchema(BaseModel):
    text: str | None = None
    translation: str | None = None
    example: str | None = None
    img: str | None = None
