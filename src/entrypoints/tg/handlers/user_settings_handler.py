from aiogram import Router, types, F
from aiogram.filters import Command

from src.entrypoints.tg.keyboards import language_keyboard
from src.entrypoints.tg.middleware.auth_user_middleware import GetUserMiddleware
from src.entrypoints.tg.middleware.common import UowMiddleWare
from src.utils.uow import BaseUnitOfWork

router = Router()
router.message.middleware(GetUserMiddleware())
router.callback_query.middleware(GetUserMiddleware())
router.message.middleware(UowMiddleWare())
router.callback_query.middleware(UowMiddleWare())


@router.message(Command("switch_learn_language"))
async def switch_lang(message: types.Message, uow: BaseUnitOfWork):
    async with uow:
        await message.answer(
            "Выберите язык для изучения:",
            reply_markup=await language_keyboard(uow, 'choose_learn_lang'),
        )


@router.message(Command("switch_language"))
async def switch_lang(message: types.Message, uow: BaseUnitOfWork):
    async with uow:
        await message.answer(
            "Выберите ваш язык:",
            reply_markup=await language_keyboard(uow, 'choose_lang'),
        )


@router.callback_query(F.data.startswith('choose_learn_lang:'))
async def choose_learn_lang(callback: types.CallbackQuery, uow: BaseUnitOfWork):
    async with uow:
        learn_lang = await uow.languages.find_one_or_none(code=callback.data.split(":")[-1])

        user = await uow.users.get_tg_user(callback.from_user.id)
        if user:
            async with uow:
                await uow.users.update_one(user.id, {'language_to_learn_id': learn_lang.id})
                await uow.commit()
            await callback.message.answer(
                f"Язык успешно изменился на {learn_lang.name}",
            )
            await callback.message.delete()
            await callback.answer()
        else:
            await callback.message.answer(
                f"Ваш профиль не сохранен, воспользуйтесь командой /start",
            )
            await callback.answer()


@router.callback_query(F.data.startswith("choose_lang:"))
async def choose_lang(callback: types.CallbackQuery, uow: BaseUnitOfWork):
    async with uow:
        lang = await uow.languages.find_one_or_none(code=callback.data.split(":")[-1])
        user = await uow.users.get_tg_user(callback.from_user.id)
        if user:
            async with uow:
                await uow.users.update_one(user.id, {'language_id': lang.id})
                await uow.commit()
            await callback.message.answer(
                f"Язык успешно изменился на {lang.name}",
            )
            await callback.message.delete()
            await callback.answer()
        else:
            await callback.message.answer(
                f"Ваш профиль не сохранен, воспользуйтесь командой /start",
            )
            await callback.answer()
