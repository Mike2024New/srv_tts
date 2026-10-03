from typing import Literal

from utils.text_normalizers.eng.main import normalize as eng_normalize
from utils.text_normalizers.ru.main import normalize as ru_normalize

__all__ = ['normalizer']


def normalizer(lang: Literal['ru', 'en'], text: str) -> str:
    """
    lang : выбор языка нормализатора (если нет такого то просто вернёт оригинальный не нормализованный текст)
    text : оригинальный текст
    Если произойдет ошибка, то вернется просто оригинальный текст
    """
    try:
        if lang == 'ru':
            current_library_words = {}

            # ru_normalizer не очень корректно обрабатывает числа если они стоят в начале, например 3.14 сотых он
            # назовет как "три точка четырнадцать сотых", необходимо присадочное слово спереди, для этого и добавлен
            # префикс
            special_prefix = '~ нормализатор '
            is_prefix = False
            if text[0].isdigit():
                is_prefix = True
                text = special_prefix + text

            text = ru_normalize(text=text, library_words=current_library_words)

            if is_prefix:
                text = text[len(special_prefix):]

        elif lang == 'en':
            current_library_words = {}
            text = eng_normalize(text=text, library_words=current_library_words)
    except Exception as err:
        print(err)
    return text


if __name__ == '__main__':
    from datetime import datetime

    data = datetime.now().strftime('%d.%m.%Y, %H: часов %M минут')
    res = normalizer(lang='ru', text=data)
    print(res)
