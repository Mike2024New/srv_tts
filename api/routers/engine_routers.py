import json
from fastapi import APIRouter, status
from config import SayRequest, ApiStartParameters, settings
from engine.main import Engine
from functools import lru_cache
from utils.text_normalizers import normalizer


@lru_cache(maxsize=1)
def get_models_info():
    """Получение информации о моделях и спикерах"""
    models_info_json = settings.models_dir_prop / 'models_info.json'
    try:
        with open(models_info_json, mode='r') as f:
            models_info = json.loads(f.read())
            return models_info
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def select_language(speaker) -> None | str:
    """Определение языка модели (просто смотрится спикер, есть ли он в словаре с en, ru)"""
    models_info = get_models_info()
    for model in models_info:
        if speaker in models_info[model]:
            if '_en.' in model:
                return 'en'
            elif '_ru.' in model:
                return 'ru'
    return None


def routers_factory(engine: Engine) -> APIRouter:
    router = APIRouter()

    @router.get('/parameters/')
    def parameters():
        """Получить параметры модели. Узнать запущен ли движок."""
        return {
            'running': engine.is_running(),
            'parameters': engine.get_parameters(),
        }

    @router.post('/start/', status_code=status.HTTP_200_OK)
    async def start(input_parameters: ApiStartParameters):
        """Запуск движка с передачей параметров"""
        engine.start(parameters=input_parameters)
        return {'result': 'Engine запущен'}

    @router.post('/execute/', status_code=status.HTTP_200_OK)
    async def execute(say_request: SayRequest):
        """Воспроизведение аудио через http."""
        # вставка нормализатора
        lang = select_language(speaker=say_request.speaker)
        text = normalizer(lang=lang, text=say_request.text) if lang is not None else say_request.text  # noqa
        # вставка нормализатора
        await engine.say(text=text, speaker=say_request.speaker, add=say_request.add)
        return {'result': 'Текст воспроизводится'}

    @router.get('/interrupt/', status_code=status.HTTP_200_OK)
    async def interrupt():
        await engine.interrupt()
        return {'result': 'Воспроизведение текста остановлено'}

    @router.get('/stop/', status_code=status.HTTP_200_OK)
    async def stop():
        engine.stop()
        return {'result': 'Engine остановлен'}

    return router
