from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from src.utils.uow import SqlAlchemyUnitOfWork


class FunctionDepelopingMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        await event.answer(
            "Функционал еще в разработке👩🏻‍💻 Sorry💔😢😭",
            show_alert=True
        )


class UowMiddleWare(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        uow = SqlAlchemyUnitOfWork()
        data["uow"] = uow
        return await handler(event, data)
