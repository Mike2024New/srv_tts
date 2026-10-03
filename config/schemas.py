from pydantic import BaseModel, ConfigDict, Field
from infrastructure_path_utils import get_root_dir_path
from pathlib import Path
from datetime import datetime

root_dir = get_root_dir_path()


class Settings(BaseModel):
    app_name: str = 'app'
    models_dir: str = 'resources/models'

    @property
    def models_dir_prop(self) -> Path:
        return get_root_dir_path() / self.models_dir


class SayRequest(BaseModel):
    text: str = Field(..., description='текст который должна произнести модель')
    speaker: str = Field(..., description='голосом которым модель должна произнести текст')
    add: bool = Field(default=False, description='текст добавляется к произносимому, или это прерывание и новый текст?')

    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'text': f'Привет! Я синтезатор, речи, введи текст а я его озвучу. Сегодня {datetime.now().strftime("%d.%m.%Y")}',
                    'speaker': 'xenia',
                    'add': False,
                }
            ]
        }
    )


class ApiStartParameters(BaseModel):
    samplerate: int = 48000
    blocksize: int = 2048
    models: list[str] = ['v5_5_ru.pt', 'v3_en.pt']
    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'samplerate': 48000,
                    'blocksize': 2048,
                    'models': ['v5_5_ru.pt', 'v3_en.pt'],
                }
            ]
        }
    )


class Parameters(BaseModel):
    samplerate: int = 48000
    blocksize: int = 2048
    model: str = 'v5_5_ru.pt'
    model_config = ConfigDict(
        json_schema_extra={
            'examples': [
                {
                    'samplerate': 48000,
                    'blocksize': 2048,
                    'model': 'v5_5_ru.pt',
                }
            ]
        }
    )
