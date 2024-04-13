from src.models import Language
from src.repository import BaseRepository


class LanguageRepository(BaseRepository):
    model = Language
