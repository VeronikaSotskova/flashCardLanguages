from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.schemas import PagedResponseSchema
from src.utils.uow import BaseUnitOfWork


async def language_keyboard(uow: BaseUnitOfWork, action_callback: str) -> types.InlineKeyboardMarkup:
    langs = await uow.languages.find_all()
    buttons = [
        [types.InlineKeyboardButton(text=lang.name, callback_data=f"{action_callback}:{lang.code}") for lang in langs]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def create_card_actions_keyboard(current_method: str = '') -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    actions = (
        ('write_translation', 'Ввести перевод'),
        ('write_text', 'Ввести текст для изучения'),
        ('write_example', 'Добавить пример'),
        ('create_card', 'Сохранить'),
    )
    for act in actions:
        if current_method != act[0]:
            builder.button(text=act[1], callback_data=act[0])
        builder.adjust(2, 3)
    return builder.as_markup()


def create_pagination_keyboard(data: PagedResponseSchema):
    builder = InlineKeyboardBuilder()
    if data.has_prev:
        builder.button(text='<-- Назад', callback_data=f'card_page:{data.page-1}')
    builder.button(text=f'{data.page}/{data.page_count}', callback_data=f'card_page:{data.page}')
    if data.has_next:
        builder.button(text='Вперед -->', callback_data=f'card_page:{data.page+1}')
    return builder.as_markup()
