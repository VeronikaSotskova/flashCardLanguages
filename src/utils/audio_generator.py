import abc

import gtts

from src.exceptions.services_exception import TextLanguageDoesntMatch


class BaseAudioGenerator(abc.ABC):
    def __init__(self, text: str, lang: str):
        self.text = text
        self.lang = lang

    def get_filename(self) -> str:
        return f"/media/cards/audio/{self.lang}/{self.text}.mp3"

    def check_text_language(self) -> bool:
        return True

    def get_file(self):
        ...

    def save_file(self) -> str:
        ...

    def create_audio(self) -> str:
        if self.check_text_language():
            return self.save_file()
        raise TextLanguageDoesntMatch


class GttsAudioGenerator(BaseAudioGenerator):
    def get_file(self):
        return gtts.gTTS(self.text, lang=self.lang)

    def save_file(self) -> str:
        filename = self.get_filename()
        self.get_file().save(f"../..{filename}")
        return filename
