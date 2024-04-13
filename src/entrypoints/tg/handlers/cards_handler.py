from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from src.entrypoints.tg.keyboards import create_pagination_keyboard
from src.entrypoints.tg.middleware.auth_user_middleware import GetUserMiddleware
from src.entrypoints.tg.utils import get_card
from src.models import User
from src.schemas import PageParams
from src.utils.uow import BaseUnitOfWork

router = Router()
router.message.middleware(GetUserMiddleware())
router.callback_query.middleware(GetUserMiddleware())


@router.message(Command("list_cards"))
async def list_cards(
    message: types.Message,
    state: FSMContext,
    current_user: User,
    uow: BaseUnitOfWork
):
    paginate_qs = await uow.cards.paginate_cards(current_user, PageParams())
    if paginate_qs.page_count <= 0:
        await message.answer(
            f"Вы еще не добавили карточки, воспользуйтесь командой /init_card",
        )
    else:
        first_card = paginate_qs.results[0]

        reply_keyboard = create_pagination_keyboard(paginate_qs)
        img_id, audio_id, messages = await get_card(first_card, message, current_user, reply_keyboard)
        messages_id = [m.message_id for m in messages]
        await state.update_data(messages_id=messages_id)


@router.callback_query(F.data.startswith("card_page:"))
async def next_card(
    callback: types.CallbackQuery,
    state: FSMContext,
    current_user: User,
    uow: BaseUnitOfWork
):
    from src.entrypoints.telegram import bot
    page = int(callback.data.split(":")[1])
    paginate_qs = await uow.cards.paginate_cards(current_user, PageParams(page=page))
    user_data = await state.get_data()
    messages_id = user_data.get('messages_id')
    await bot.delete_messages(chat_id=callback.message.chat.id, message_ids=messages_id)

    first_card = paginate_qs.results[0]
    reply_keyboard = create_pagination_keyboard(paginate_qs)
    img_id, audio_id, messages = await get_card(first_card, callback.message, current_user, reply_keyboard)
    messages_id = [m.message_id for m in messages]
    await state.update_data(messages_id=messages_id)
