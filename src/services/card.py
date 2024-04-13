from src.models import Card, User
from src.schemas.card import CardCreateSchema
from src.utils.uow import BaseUnitOfWork
from src.utils.audio_generator import GttsAudioGenerator
from src.utils.image_search import UnsplashClient, ImageSearcher
from src.utils.translator import GoogleTranslator


class CardService:
    @classmethod
    async def create_card(
        cls,
        uow: BaseUnitOfWork,
        card_data: CardCreateSchema,
        user: 'User',
    ) -> 'Card':
        image = None
        if not card_data.translation:
            card_data.translation = GoogleTranslator(
                card_data.text,
                to_lang=user.language.code,
                from_lang=user.language_to_learn.code
            ).translate()
        elif not card_data.text:
            card_data.text = GoogleTranslator(
                card_data.translation,
                to_lang=user.language_to_learn.code,
                from_lang=user.language.code
            ).translate()
        image_id = None
        similar_image = await uow.files.find_similar_image(card_data.text)
        if similar_image:
            image = similar_image
            image_id = similar_image.id
        if not image_id:
            image = await ImageSearcher(UnsplashClient()).find(uow, card_data.text, user.language_to_learn.code)
            image_id = image.id if image else None

        audio = await uow.files.find_similar_audio(card_data.text)
        audio_id = audio.id if audio else None
        if not audio_id:
            audio_path = GttsAudioGenerator(card_data.text, user.language_to_learn.code).create_audio()
            audio = await uow.files.create_audio(audio_path, card_data.text)
            audio_id = audio.id

        card = await uow.cards.create(
            user_id=user.id,
            text=card_data.text,
            translation=card_data.translation,
            example=card_data.example,
            text_language_id=user.language_to_learn_id,
            translation_language_id=user.language_id,
            audio_id=audio_id,
            image_id=image_id
        )
        card.image = image
        card.audio = audio
        return card
