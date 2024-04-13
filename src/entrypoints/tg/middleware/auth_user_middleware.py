from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from src.utils.uow import SqlAlchemyUnitOfWork


class GetUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        uow = SqlAlchemyUnitOfWork()
        async with uow:
            user = await uow.users.get_tg_user(event.from_user.id)
            if user:
                data["current_user"] = user
                data["uow"] = uow
                return await handler(event, data)
            await event.answer(
                "Ваш профиль не сохранен, воспользуйтесь командой /start",
                show_alert=True
            )
