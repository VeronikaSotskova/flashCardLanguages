from sqlalchemy import select, ResultProxy
from sqlalchemy.orm import joinedload, aliased

from src.models import User, Language
from src.repository import BaseRepository


class UserRepository(BaseRepository):
    model = User

    async def get_tg_user(self, tg_id: int) -> User | None:
        query = select(
            User
        ).where(
            User.tg_id == tg_id
        ).options(
            joinedload(User.language),
            joinedload(User.language_to_learn)
        )
        objects: ResultProxy = await self.session.execute(query)
        return objects.scalars().first()

