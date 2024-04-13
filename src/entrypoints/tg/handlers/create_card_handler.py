# 1. create card
# 2. write text - check that lang of text equals to user.lang_to_learn
# 3. write orig text if need
# 4. write example if need
# 5. send img if need
# 6. create card to bd
from aiogram import Router, types, html, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from src.entrypoints.telegram import bot
from src.entrypoints.tg.keyboards import create_card_actions_keyboard
from src.entrypoints.tg.middleware.auth_user_middleware import GetUserMiddleware
from src.entrypoints.tg.utils import get_card
from src.models import User
from src.schemas.card import CardCreateSchema
from src.services.card import CardService
from src.utils.uow import BaseUnitOfWork

router = Router()
router.message.middleware(GetUserMiddleware())
router.callback_query.middleware(GetUserMiddleware())


class CreateCardState(StatesGroup):
    write_text = State()

    choose_params = State()

    write_translation = State()
    write_example = State()
    # todo send image
    create_card = State()


def get_card_display(state: dict[str, str | None] | None, user: User) -> str:
    lang_to = user.language_to_learn.name.capitalize()
    lang_from = user.language.name.capitalize()

    translation = state.get("translation")
    text = state.get("text")
    example = state.get("example")
    if translation or text or example:
        result = []
        if translation:
            result.append(f"{html.bold(lang_from)}: {translation}")
        if text:
            result.append(f"{html.bold(lang_to)}: {text}")
        if example:
            result.append(f"{html.bold('Пример/описание')}: {html.italic(example)}")
        return "\n".join(result)
    return "Введите что-то для создания карточки"


@router.message(Command("init_card"))
async def init_card(
    message: types.Message,
    state: FSMContext,
    current_user: User
):
    user_data = await state.get_data()
    await state.set_state(CreateCardState.choose_params)
    await message.answer(
        get_card_display(user_data, current_user),
        parse_mode="HTML",
        reply_markup=create_card_actions_keyboard()
    )


@router.callback_query(F.data == 'write_text')
async def write_text(
    callback: types.CallbackQuery,
    state: FSMContext,
    current_user: User
):
    user_data = await state.get_data()
    translation = user_data.get('translation')
    text = f"Введи перевод {html.bold(translation)}" if translation else "Введи текст"
    await callback.message.delete()
    message = await callback.message.answer(
        f"{text}, используя {html.bold(current_user.language_to_learn.name.lower())} язык",
        parse_mode="HTML"
    )
    await state.update_data(msg_id__text=message.message_id)
    await state.set_state(CreateCardState.write_text)


@router.message(CreateCardState.write_text)
async def write_text_message(
    message: types.Message,
    state: FSMContext,
    current_user: User
):
    user_data = await state.get_data()
    if user_data.get('msg_id__text'):
        await bot.delete_message(chat_id=message.chat.id, message_id=user_data['msg_id__text'])
    await message.delete()
    await state.update_data(text=message.text)
    await message.answer(
        get_card_display(await state.get_data(), current_user),
        parse_mode="HTML",
        reply_markup=create_card_actions_keyboard()
    )


@router.callback_query(F.data == "write_translation")
async def write_translation(
    callback: types.CallbackQuery,
    state: FSMContext,
    current_user: User
):
    user_data = await state.get_data()
    transl = user_data.get('text')
    text = f"Введи перевод {html.bold(transl)}" if transl else "Введи текст"
    await callback.message.delete()
    message = await callback.message.answer(
        f"{text}, используя {html.bold(current_user.language.name.lower())} язык",
        parse_mode="HTML"
    )
    await state.update_data(msg_id__translation=message.message_id)
    await state.set_state(CreateCardState.write_translation)


@router.message(CreateCardState.write_translation)
async def write_translation_message(
    message: types.Message,
    state: FSMContext,
    current_user: User
):
    user_data = await state.get_data()
    if user_data.get('msg_id__translation'):
        await bot.delete_message(chat_id=message.chat.id, message_id=user_data['msg_id__translation'])
    await message.delete()
    await state.update_data(translation=message.text)
    await message.answer(
        get_card_display(await state.get_data(), current_user),
        parse_mode="HTML",
        reply_markup=create_card_actions_keyboard()
    )


@router.callback_query(F.data == "write_example")
async def write_example(
    callback: types.CallbackQuery,
    state: FSMContext
):
    await callback.message.delete()
    message = await callback.message.answer(
        f"Введите пример/описание",
        parse_mode="HTML"
    )
    await state.update_data(msg_id__example=message.message_id)
    await state.set_state(CreateCardState.write_example)


@router.message(CreateCardState.write_example)
async def write_example_message(
    message: types.Message,
    state: FSMContext,
    current_user: User
):
    user_data = await state.get_data()
    if user_data.get('msg_id__example'):
        await bot.delete_message(chat_id=message.chat.id, message_id=user_data['msg_id__example'])
    await message.delete()
    await state.update_data(example=message.text)
    await message.answer(
        get_card_display(await state.get_data(), current_user),
        parse_mode="HTML",
        reply_markup=create_card_actions_keyboard()
    )


@router.callback_query(F.data == "create_card")
async def create_card(
    callback: types.CallbackQuery,
    state: FSMContext,
    current_user: User,
    uow: BaseUnitOfWork
):
    user_data = await state.get_data()
    if not user_data.get('text') and not user_data.get('translation'):
        await callback.message.delete()
        await state.set_state(CreateCardState.choose_params)
        await callback.message.answer(
            f"Вы не ввели текст, используя {current_user.language_to_learn.name.capitalize()} язык и перевод {current_user.language.name.capitalize()}. "
            f"Введите что-то.",
            parse_mode="HTML",
            reply_markup=create_card_actions_keyboard()
        )
    else:
        input_data = CardCreateSchema(
            **user_data
        )
        card = await CardService.create_card(
            uow,
            input_data,
            current_user
        )
        await uow.commit()
        await callback.message.delete()
        await callback.answer(
            f"Ваша карточка сохранена"
        )

        img_id, audio_id, messages = await get_card(card, callback.message, current_user)
        if img_id or audio_id:
            if card.image and not card.image.tg_id:
                card.image.tg_id = img_id
            if card.audio and not card.audio.tg_id:
                card.audio.tg_id = audio_id
            await uow.commit()
        await state.clear()


@router.callback_query(CreateCardState.choose_params)
async def choose_params(
    callback: types.CallbackQuery,
):
    await callback.answer(
        "Продолжить",
        reply_markup=create_card_actions_keyboard()
    )
