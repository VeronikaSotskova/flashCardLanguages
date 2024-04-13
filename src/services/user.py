from src.models import User
from src.schemas.user import UserCreateSchema
from src.utils.uow import BaseUnitOfWork


class UserService:
    @classmethod
    async def create_tg_user(
        cls,
        uow: BaseUnitOfWork,
        user_data: UserCreateSchema,
    ) -> (User, bool):
        learn_lang = await uow.languages.find_one_or_none(code=user_data.language_code)
        language = await uow.languages.find_one_or_none(code=user_data.language_to_learn_code)
        user = await uow.users.get_tg_user(user_data.tg_id)
        if user:
            return user, False
        else:
            user = await uow.users.create(
                username=user_data.username,
                language_id=language.id,
                language_to_learn_id=learn_lang.id,
                tg_id=user_data.tg_id
            )
            await uow.commit()
            user.language = language
            user.language_to_learn = learn_lang
            return user, True

