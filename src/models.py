from datetime import datetime
from enum import Enum

from sqlalchemy import CheckConstraint, ForeignKey, DateTime, SmallInteger, String
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.db import BaseWithId, str_256


class Card(BaseWithId):
    __tablename__ = "card"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    text: Mapped[str]
    translation: Mapped[str]
    example: Mapped[str | None]
    group: Mapped[int] = mapped_column(SmallInteger, server_default="0")
    last_show: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    text_language_id: Mapped[int] = mapped_column(ForeignKey("language.id", ondelete="CASCADE"))
    translation_language_id: Mapped[int] = mapped_column(ForeignKey("language.id", ondelete="CASCADE"))
    audio_id: Mapped[int | None] = mapped_column(ForeignKey("file.id", ondelete="SET NULL"), nullable=True)
    image_id: Mapped[int | None] = mapped_column(ForeignKey("file.id", ondelete="SET NULL"), nullable=True)

    user: Mapped["User"] = relationship(
        back_populates="cards"
    )
    text_language: Mapped["Language"] = relationship(
        back_populates="cards", foreign_keys=[text_language_id]
    )
    translation_language: Mapped["Language"] = relationship(
        back_populates="translation_cards", foreign_keys=[translation_language_id]
    )
    audio: Mapped["File"] = relationship(
        back_populates="cards_audio", foreign_keys=[audio_id]
    )
    image: Mapped["File"] = relationship(
        back_populates="cards_image", foreign_keys=[image_id]
    )

    __table_args__ = (
        CheckConstraint(group >= 0, name="check_group_positive"),
    )


class FileType(Enum):
    audio = 'audio'
    image = 'image'
    video = 'video'


class File(BaseWithId):
    __tablename__ = "file"

    file_type: Mapped[FileType]
    path: Mapped[str]
    tg_id: Mapped[str | None]
    main_tag: Mapped[str]

    cards_audio: Mapped[list[Card]] = relationship(
        back_populates="audio", foreign_keys=[Card.audio_id]
    )
    cards_image: Mapped[list[Card]] = relationship(
        back_populates="image", foreign_keys=[Card.image_id]
    )

class User(BaseWithId):
    __tablename__ = "user"

    tg_id: Mapped[int] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    language_id: Mapped[int | None] = mapped_column(ForeignKey("language.id", ondelete="SET NULL"), nullable=True)
    language_to_learn_id: Mapped[int | None] = mapped_column(ForeignKey("language.id", ondelete="SET NULL"), nullable=True)
    last_session: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    cards: Mapped[list['Card']] = relationship(
        back_populates="user"
    )
    language: Mapped['Language'] = relationship(
        back_populates="users", foreign_keys=[language_id]
    )
    language_to_learn: Mapped['Language'] = relationship(
        back_populates="user_learners", foreign_keys=[language_to_learn_id]
    )


class Language(BaseWithId):
    __tablename__ = "language"

    name: Mapped[str_256]
    code: Mapped[str] = mapped_column(String(4), unique=True)
    nat_name: Mapped[str_256]

    cards: Mapped[list['Card']] = relationship(
        back_populates="text_language", foreign_keys=[Card.text_language_id]
    )
    translation_cards: Mapped[list['Card']] = relationship(
        back_populates="translation_language", foreign_keys=[Card.translation_language_id]
    )
    users: Mapped[list['User']] = relationship(
        back_populates="language", foreign_keys=[User.language_id]
    )
    user_learners: Mapped[list['User']] = relationship(
        back_populates="language_to_learn", foreign_keys=[User.language_to_learn_id]
    )



