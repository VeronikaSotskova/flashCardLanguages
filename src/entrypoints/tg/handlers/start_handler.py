from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from src.entrypoints.tg.keyboards import language_keyboard
from src.entrypoints.tg.middleware.common import UowMiddleWare
from src.schemas.user import UserCreateSchema
from src.services.user import UserService
from src.utils.uow import BaseUnitOfWork

router = Router()
router.message.middleware(UowMiddleWare())
router.callback_query.middleware(UowMiddleWare())


class StartState(StatesGroup):
    choose_lang = State()
    choose_learn_lang = State()


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext, uow: BaseUnitOfWork):
    async with uow:
        user = await uow.users.get_tg_user(message.from_user.id)
        if user:
            await message.answer(f"Ваш профиль уже существует с данными настройками.\n\n"
                                 f"<b>Ваш язык:</b> {user.language.name}\n"
                                 f"<b>Язык для изучения:</b> {user.language_to_learn.name}", parse_mode="HTML")
        else:
            await message.answer(
                "Выберите свой язык:",
                reply_markup=await language_keyboard(uow, 'set_lang'),
            )
            await state.set_state(StartState.choose_lang)


@router.callback_query(StartState.choose_lang)
async def choose_lang(callback: types.CallbackQuery, state: FSMContext, uow: BaseUnitOfWork):
    await state.update_data(language=callback.data.split(":")[-1])
    async with uow:
        await callback.message.answer(
            "Выберите язык, который хотите учить:",
            reply_markup=await language_keyboard(uow, 'set_learn_lang'),
        )
        await callback.answer()
        await state.set_state(StartState.choose_learn_lang)
        await callback.message.delete()


@router.callback_query(StartState.choose_learn_lang)
async def choose_learn_lang(callback: types.CallbackQuery, state: FSMContext, uow: BaseUnitOfWork):
    user_data = await state.get_data()
    user_data = UserCreateSchema(
        username=callback.from_user.username,
        language_code=callback.data.split(":")[-1],
        language_to_learn_code=user_data.get('language'),
        tg_id=callback.from_user.id
    )
    async with uow:
        user, created = await UserService.create_tg_user(uow, user_data)
        if created:
            msg = f"Готово, Ваш профиль сохранен!\n\n" \
                    f"<b>Ваш язык:</b> {user.language.name}\n" \
                    f"<b>Язык для изучения:</b> {user.language_to_learn.name}"
        else:
            msg = f"Ваш профиль уже существует с данными настройками.\n\n" \
                    f"<b>Ваш язык:</b> {user.language.name}\n" \
                    f"<b>Язык для изучения:</b> {user.language_to_learn.name}"
    await callback.message.answer(
        msg, parse_mode="HTML"
    )
    await callback.message.delete()
    await callback.answer()
    await state.clear()
