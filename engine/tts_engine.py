import asyncio

import numpy, warnings
from config import settings, Parameters
from infrastructure_path_utils import FlatJsonManager

# отключение предупреждений pytorch при загрузке silero (там есть свои внутренние ошибки, типа лишних `\` в регулярках
warnings.filterwarnings('ignore', category=SyntaxWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)


class Engine:
    def __init__(self):
        self._model = None
        self._parameters: Parameters | None = None
        self._json_info = FlatJsonManager(json_file_path=settings.models_dir_prop / 'models_info.json')
        self._torch_package_importer = None
        self._torch_device = None
        self._torch_no_grad = None

    def start(self, parameters: Parameters):
        from torch.package import PackageImporter
        from torch import device, no_grad

        self._torch_package_importer = PackageImporter
        self._torch_device = device
        self._torch_no_grad = no_grad

        self._parameters = parameters
        self._check_new_models()  # проверка появились ли новые модели
        model_path = settings.models_dir_prop / self._parameters.model
        self._model = self._torch_package_importer(str(model_path)).load_pickle("tts_models", "model")
        self._model.to(
            device=self._torch_device('cpu'))  # пока на cpu, позже можно будет попробовать cuda (нужен cublas)

    async def generate(self, text, callback, speaker='xenia'):
        """Генерация аудио, преобразует текст в pcm (длина текста ограничивается внешними сущностями)"""
        try:
            # процесс генерации аудио
            with self._torch_no_grad():
                audio_tensor = self._model.apply_tts(text=text, speaker=speaker)
                audio = audio_tensor.numpy()
                # нормализация аудио
                max_val = numpy.max(numpy.abs(audio))
                if max_val > 0:
                    audio = audio / max_val
                audio_int16 = (audio * 32767).astype(numpy.int16)  # это прямо целый и длинный единый блок pcm?
                callback(audio_int16)

        except ValueError:
            # Если ошибка распознавания, то вернуть пустой массив из нулей
            audio_int16 = numpy.zeros(self._parameters.blocksize, dtype=numpy.int16)
            callback(audio_int16)

    def stop(self):
        """Высвобождение памяти"""
        if self._model is not None:
            del self._model
            self._model = None

    def _check_new_models(self):
        """Проверка не появились ли новые модели в models_dir. Для обновления информации о них в api"""
        data = self.info()
        for file in settings.models_dir_prop.iterdir():
            if file == self._json_info._json_file_path:  # noqa
                continue
            if data.get(file.name) is not None:  # модель уже есть
                continue
            model = self._torch_package_importer(str(file)).load_pickle("tts_models", "model")
            voices = model.speakers if model.speakers else []
            self._json_info.add(key=file.name, value=voices)

    def info(self):
        """Получить список доступных моделей"""
        return self._json_info.data()


async def main():
    engine = Engine()
    # print(engine.info())
    engine.start(parameters=Parameters())
    await engine.generate(text='Скажи что нибудь мне нужно тебя услышать', speaker='xenia', callback=lambda x: print(x))
    await engine.generate(text='Новый текст для примера сейчас', speaker='xenia', callback=lambda x: print(x))


if __name__ == '__main__':
    asyncio.run(main())
