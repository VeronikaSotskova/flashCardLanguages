from sqlalchemy import ResultProxy, select, func
from sqlalchemy.orm import joinedload

from src.models import Card, User
from src.repository import BaseRepository
from src.schemas import PageParams, PagedResponseSchema


class CardRepository(BaseRepository):
    model = Card

    async def paginate_cards(
        self,
        user: User,
        page_params: PageParams
    ) -> PagedResponseSchema:
        count_query = select(
            func.count(Card.id)
        ).filter(
            Card.user_id == user.id,
            Card.text_language_id == user.language_to_learn_id,
            Card.translation_language_id == user.language_id
        )
        count: ResultProxy = await self.session.execute(count_query)
        count = count.scalar()
        objects = []
        if count:
            query = select(
                Card
            ).options(
                joinedload(Card.audio),
                joinedload(Card.image),
            ).filter(
                Card.user_id == user.id,
                Card.text_language_id == user.language_to_learn_id,
                Card.translation_language_id == user.language_id
            ).order_by(
                Card.text, Card.id
            ).offset(
                (page_params.page - 1) * page_params.size
            ).limit(page_params.size)
            cards: ResultProxy = await self.session.execute(query)
            objects = cards.scalars().all()
        page_count = count // page_params.size + int(count % page_params.size != 0)
        return PagedResponseSchema(
            page_count=page_count,
            page=page_params.page,
            size=page_params.size,
            results=[o for o in objects],
            has_next=page_params.page < page_count,
            has_prev=page_params.page > 1
        )



