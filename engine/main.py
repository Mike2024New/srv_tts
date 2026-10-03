import asyncio
import re
from engine.tts_engine import Engine as TTSEngine
from engine.audio_output_engine import Engine as AudioOutputEngine
from config import Parameters, ApiStartParameters


class Engine:
    def __init__(self):
        self._tts_engines: dict[str, TTSEngine] = {}
        self._tts_engine = TTSEngine()
        self._audio_output_engine: AudioOutputEngine | None = None
        self._parameters: ApiStartParameters | None = None
        self._running = False
        self._lock = asyncio.Lock()

    def info(self):
        return self._tts_engine.info()

    def is_running(self):
        return self._running

    def get_parameters(self):
        return self._parameters

    def start(self, parameters: ApiStartParameters):
        if not self._running:
            self._running = True
            self._parameters = parameters

            # инициализация микрофона
            self._audio_output_engine = AudioOutputEngine(
                parameters=Parameters(
                    blocksize=parameters.blocksize,
                    samplerate=parameters.samplerate,
                )
            )

            # запуск движков с переданными моделями, например ['v5_5_ru.pt', 'v3_en.pt']
            for model in parameters.models:
                engine = TTSEngine()
                engine.start(
                    parameters=Parameters(
                        blocksize=parameters.blocksize,
                        samplerate=parameters.samplerate,
                        model=model,
                    )
                )
                self._tts_engines[model] = engine

    async def say(self, text: str, speaker: str, add: bool = False):
        """
        Произносит речь из длинного текста, разбивая его на чанки (режим озвучки текстов).
        Прерывает предыдущую если add=False.
        """

        async with self._lock:
            if not self._audio_output_engine.is_running():  # запуск движка если не запущен
                self._audio_output_engine.start()

            models = self.info()
            engine = None
            for key in self._tts_engines:
                speakers = models.get(key, [])
                if speaker in speakers:
                    engine = self._tts_engines[key]
                    break

            if engine is None:
                raise RuntimeError(f'Не найден спикер {speaker}.')

            if not add:
                self._audio_output_engine.clear_buffer()  # сброс буфера

            # Разбиение предложения на подпредложения для оптимизации времени (чтобы tts уже начал выдавать чанки)
            # Не рекомендуется для real-time api кидать сюда большие тексты, лучше это делать на оркестраторе
            sentences = re.split(r'(?<=[.!?])\s+', text)

            for sentence in sentences:
                sentence = sentence.strip()
                if sentence:
                    await engine.generate(
                        text=sentence,
                        speaker=speaker,
                        callback=lambda chunk: self._audio_output_engine.put(chunk)
                    )

    async def interrupt(self):
        self._audio_output_engine.clear_buffer()

    def stop(self):
        # остановка всех движков
        for key in self._tts_engines:
            self._tts_engines[key].stop()

        if self._audio_output_engine:
            self._audio_output_engine.stop()
            self._audio_output_engine = None
        self._running = False


async def main():
    engine = Engine()
    engine.start(parameters=ApiStartParameters(
        samplerate=48000, blocksize=2048, models=['v5_5_ru.pt', 'v3_en.pt']
    ))
    await engine.say(text='Голос один, я говорю.', speaker='aidar')
    await asyncio.sleep(2)
    await engine.say(text='Voice two, I speaking.', add=True, speaker='en_0')
    await asyncio.sleep(2)
    engine.stop()


if __name__ == '__main__':
    asyncio.run(main())
