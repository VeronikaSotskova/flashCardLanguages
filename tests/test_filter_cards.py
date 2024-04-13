from src.models import Language, User

RU_LANG = Language(
    name='Русский',
    code='ru',
    nat_name='Русский'
)

EN_LANG = Language(
    name='Английский',
    code='en',
    nat_name='English'
)

FR_LANG = Language(
    name='Французский',
    code='fr',
    nat_name='Français'
)


# todo: rewrite

def test_create_cards():
    user_1 = User(
        username='user_1',
        language=RU_LANG,
        language_to_learn=EN_LANG
    )
    user_1.create_card(
        text_to_trans='Медведь',
        text_orig='Bear',
    )
    user_1.create_card(
        text_to_trans='Черепаха',
        text_orig='Turtle',
    )

    user_all_cards = user_1.get_all_cards()
    assert len(user_all_cards) == 2
    assert all([card.lang == user_1.language_to_learn for card in user_all_cards])


def test_switch_language():
    user_1 = User(
        username='user_1',
        language=RU_LANG,
        language_to_learn=EN_LANG
    )
    user_1.create_card(
        text_to_trans='Медведь',
        text_orig='Bear',
    )
    user_1.create_card(
        text_to_trans='Черепаха',
        text_orig='Turtle',
    )

    assert len(user_1.get_my_cards()) == 2

    user_1.switch_lang(FR_LANG)
    assert len(user_1.get_my_cards()) == 0
    assert len(user_1.get_all_cards()) == 2

    user_1.create_card(
        text_to_trans='Черепаха',
        text_orig='Tortue',
    )
    user_1.create_card(
        text_to_trans='Медведь',
        text_orig='Ours',
    )
    assert len(user_1.get_my_cards()) == 2
    assert len(user_1.get_all_cards()) == 4


def test_create_empty_card():
    user_1 = User(
        username='user_1',
        language=RU_LANG,
        language_to_learn=EN_LANG
    )
    card = user_1.create_card(
        text_to_trans='Медведь',
    )
    assert card.text_translate is not None
    assert card.audio is not None
    assert card.img is not None

def test_gt_card_with_other_type():
    user_1 = User(
        username='user_1',
        language=RU_LANG,
        language_to_learn=EN_LANG
    )
    user_1.create_card(
        text_to_trans='Черепаха',
        text_orig='Tortue',
    )


