from typing import Iterable

from sqlalchemy import select, ResultProxy, insert, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import BaseWithId


class BaseRepository:
    model: BaseWithId = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, model_id: int) -> BaseWithId | None:
        return await self.find_one_or_none(id=model_id)

    async def find_one_or_none(self, **filter_by) -> BaseWithId | None:
        query = select(self.model).filter_by(**filter_by)
        objects: ResultProxy = await self.session.execute(query)
        return objects.scalar_one_or_none()

    async def find_all(self, **filter_by) -> Iterable[BaseWithId]:
        query = select(self.model).filter_by(**filter_by)
        objects: ResultProxy = await self.session.execute(query)
        return objects.scalars().all()

    async def create(self, **data) -> BaseWithId:
        stmt = insert(self.model).values(**data).returning(self.model)
        new_object = await self.session.execute(stmt)
        return new_object.scalar()

    async def delete(self, **filter_by) -> int:
        stmt = delete(self.model).filter_by(**filter_by).returning(self.model.id)
        res: ResultProxy = await self.session.execute(stmt)
        return res.scalar()

    async def filter(self, condition) -> Iterable[BaseWithId]:
        query = select(self.model).filter(condition)
        objects: ResultProxy = await self.session.execute(query)
        return objects.scalars().all()

    async def update_one(self, obj_id: int, data: dict) -> int:
        stmt = update(self.model).values(**data).filter_by(id=obj_id).returning(self.model.id)
        res = await self.session.execute(stmt)
        return res.scalar_one()
