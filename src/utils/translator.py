import abc

from deep_translator import GoogleTranslator as GT

from src.exceptions.services_exception import TextLanguageDoesntMatch


class BaseTranslator(abc.ABC):
    def __init__(self, text: str, to_lang: str, from_lang: str | None = None):
        self.text = text
        self.to_lang = to_lang
        self.from_lang = from_lang

    def check_text_language(self) -> bool:
        return True

    @abc.abstractmethod
    def get_from_lang(self) -> str:
        ...

    @abc.abstractmethod
    def get_translation(self) -> str:
        ...

    def translate(self) -> str:
        if self.check_text_language():
            return self.get_translation()
        raise TextLanguageDoesntMatch()


class GoogleTranslator(BaseTranslator):
    def get_from_lang(self) -> str:
        return 'auto' if not self.from_lang else self.from_lang

    def get_translation(self) -> str:
        return GT(source=self.get_from_lang(), target=self.to_lang).translate(self.text)
