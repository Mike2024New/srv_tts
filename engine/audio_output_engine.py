import asyncio
import sounddevice as sd
import numpy as np
from collections import deque
from config import Parameters


class Engine:
    def __init__(self, parameters: Parameters):
        self._buffer = deque()  # чанки int16
        self._ring = np.zeros(0, dtype=np.int16)  # кольцевой буфер
        self._stream = None
        self._stop_requested = False
        self._parameters = parameters

    def is_running(self):
        """Проверка что стрим запущен"""
        return self._stream is not None

    def _callback(self, outdata, frames, _time, _status):
        if self._stop_requested:
            outdata.fill(0)
            raise sd.CallbackAbort  # мгновенная остановка

        # набор из deque достаточно сэмплов
        while len(self._ring) < frames:
            if not self._buffer:
                break
            chunk = self._buffer.popleft()
            self._ring = np.concatenate([self._ring, chunk])

        if len(self._ring) < frames:
            # данных не хватает — добить тишиной
            outdata[:len(self._ring)] = self._ring.reshape(-1, 1)
            outdata[len(self._ring):] = 0
            self._ring = np.zeros(0, dtype=np.int16)
        else:
            # добавление чанков в буфер
            outdata[:] = self._ring[:frames].reshape(-1, 1)
            self._ring = self._ring[frames:]

    def start(self):
        self._stream = None
        self._stop_requested = False
        self._stream = sd.OutputStream(
            samplerate=self._parameters.samplerate,
            channels=1,
            dtype='int16',
            blocksize=self._parameters.blocksize,
            callback=self._callback,
        )
        self._stream.start()

    def put(self, chunk: np.ndarray):
        """Добавить чанк int16 в очередь воспроизведения"""
        self._buffer.append(chunk)

    def clear_buffer(self):
        # сбросить буфер
        self._buffer.clear()
        self._ring = np.zeros(0, dtype=np.int16)

    def stop(self):
        self._stop_requested = True
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
            # сбросить буфер
            self._buffer = deque()
            self._ring = np.zeros(0, dtype=np.int16)


async def main():
    engine = Engine(parameters=Parameters())
    engine.start()

    # # демонстрация воспроизведения звука (что динамики работают)
    for _ in range(200):
        t = np.linspace(0, 0.2, int(48000 * 0.2), endpoint=False)
        test_fragment = (0.5 * np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
        engine.put(test_fragment)
    await asyncio.sleep(2)
    engine.stop()
    await asyncio.to_thread(lambda: input('...'))

    engine.start()
    for _ in range(200):
        t = np.linspace(0, 0.2, int(48000 * 0.2), endpoint=False)
        test_fragment = (0.5 * np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
        engine.put(test_fragment)
    await asyncio.sleep(2)

    await asyncio.to_thread(lambda: input('...'))
    engine.stop()


if __name__ == '__main__':
    asyncio.run(main())
