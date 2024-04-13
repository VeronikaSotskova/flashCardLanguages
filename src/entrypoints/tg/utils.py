from aiogram import types, html
from aiogram.types import FSInputFile, URLInputFile

from src.models import User, Card


def get_card_audio(card: 'Card') -> FSInputFile | str | None:
    if not card.audio:
        return None
    if card.audio.tg_id:
        return card.audio.tg_id
    return FSInputFile(path=f"../..{card.audio.path}")


def get_card_image_url(card: 'Card') -> URLInputFile | str | None:
    if not card.image:
        return None
    if card.image.tg_id:
        return card.image.tg_id
    return URLInputFile(card.image.path)


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


async def get_card(card: Card, message: types.Message, current_user: User, keyboard=None):
    audio = card.audio
    image_from_url = card.image.path if card and card.image else None
    card_text = get_card_display(
        {"translation": card.translation, "text": card.text, "example": card.example},
        current_user
    )
    img_id = None
    audio_id = None
    messages = []
    if image_from_url is not None and audio is not None:
        image_result = await message.answer_photo(get_card_image_url(card), caption=card_text, parse_mode="HTML", reply_markup=keyboard)
        img_id = image_result.photo[0].file_id
        audio_result = await message.answer_audio(get_card_audio(card), title=card.text)
        audio_id = audio_result.audio.file_id
        messages.extend([image_result, audio_result])
    elif image_from_url is not None:
        image_result = await message.answer_photo(get_card_image_url(card), caption=card_text, parse_mode="HTML", reply_markup=keyboard)
        img_id = image_result.photo[0].file_id
        messages.append(image_result)
    elif audio is not None:
        audio_result = await message.answer_audio(
            get_card_audio(card),
            title=card.text,
            caption=card_text,
            parse_mode="HTML",
            reply_markup=keyboard
        )
        audio_id = audio_result.audio.file_id
        messages.append(audio_result)
    else:
        await message.answer(text=card_text, parse_mode="HTML", reply_markup=keyboard)
    return img_id, audio_id, messages
