from sqlalchemy import select, ResultProxy, update, bindparam

from src.models import File, FileType
from src.repository import BaseRepository


class FileRepository(BaseRepository):
    model = File

    async def create_audio(self, path: str, tag: str):
        return await self.create(path=path, main_tag=tag.lower(), file_type=FileType.audio)

    async def create_video(self, path: str, tag: str):
        return await self.create(path=path, main_tag=tag.lower(), file_type=FileType.video)

    async def create_image(self, path: str, tag: str):
        return await self.create(path=path, main_tag=tag.lower(), file_type=FileType.image)

    async def find_similar_image(self, tag: str) -> File | None:
        query = select(
            File
        ).filter(
            (File.main_tag.like(f"%{tag.lower()}%"))
            & (File.file_type == FileType.image)
        )
        objects: ResultProxy = await self.session.execute(query)
        return objects.scalars().first()

    async def find_similar_audio(self, tag: str) -> File | None:
        query = select(
            File
        ).filter(
            (File.main_tag == tag.lower())
            & (File.file_type == FileType.audio)
        )
        objects: ResultProxy = await self.session.execute(query)
        return objects.scalars().first()

    async def update_card_files_tg_id(
        self,
        data: list[dict[str, int]]
    ):
        stmt = update(
            File
        ).where(
            File.id == bindparam("id")
        ).values(
            tg_id=bindparam("tg_id")
        )
        await self.session.execute(stmt, data)
