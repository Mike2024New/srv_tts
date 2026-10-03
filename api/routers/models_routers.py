from fastapi import APIRouter
from engine.main import Engine


def routers_factory(engine: Engine) -> APIRouter:
    _ = engine
    router = APIRouter(prefix='/models', tags=['models'])

    @router.get('/')
    async def available_models_list():
        """Получить список доступных моделей и голосов озвучки"""
        return engine.info()

    return router
