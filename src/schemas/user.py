from pydantic import BaseModel


class UserCreateSchema(BaseModel):
    username: str
    language_code: str
    language_to_learn_code: str
    tg_id: int
