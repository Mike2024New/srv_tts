from config.main import settings, settings_manager, logger
from config.schemas import Parameters, SayRequest, ApiStartParameters

__all__ = [
    'settings', 'settings_manager', 'logger',
    'Parameters', 'SayRequest', 'ApiStartParameters',
]

# создать необходимый каталог
settings.models_dir_prop.mkdir(exist_ok=True, parents=True)
