import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from src.config import settings
from src.entrypoints.tg.handlers import cards_handler, start_handler, user_settings_handler, create_card_handler

logging.basicConfig(level=logging.INFO)
bot = Bot(token=settings.TELEGRAM_KEY)
dp = Dispatcher()

bot_commands = [
    BotCommand(command="/start", description="Создать профиль"),
    BotCommand(command="/init_card", description="Создать карточку"),
    BotCommand(command="/list_cards", description="Список карточек"),
    BotCommand(command="/switch_language", description="Изменить язык"),
    BotCommand(command="/switch_learn_language", description="Изменить язык для изучения"),
]


async def main():
    dp.include_routers(
        start_handler.router,
        user_settings_handler.router,
        cards_handler.router,
        create_card_handler.router
    )

    await bot.set_my_commands(bot_commands)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
