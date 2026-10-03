import asyncio, subprocess, aiohttp, sys
from pathlib import Path
from infrastructure_http_clients import ServerProbe

"""
Простой пример запуска, выполнения полезной нагрузки и остановки сервиса. Может быть использован как тест кейс, 
для проверки работоспособности компонента после клонирования с git. 
"""

port = 8000


async def run_server() -> subprocess.Popen:
    # 1.запустить сервер
    cmd = [sys.executable, 'cli.py', 'run-server', '--port', str(port), '--log-level', 'info']
    process = subprocess.Popen(cmd, cwd=Path.cwd())

    # 2. Ожидание запуска сервера (пока сервер не станет отвечать на /health/, например torch загружается долго)
    print(f'Ожидание запуска сервера')
    ServerProbe.wait_for_server_up(
        url=f'http://127.0.0.1:{port}/health/',
        timeout=30,
        expected_status=200,
    )

    # 3. Запуск engine, с переданными параметрами модели
    async with aiohttp.ClientSession() as session:
        parameters = {'samplerate': 48000, 'blocksize': 2048, 'models': ['v5_5_ru.pt', 'v3_en.pt']}
        print(f'Запуск engine сервера')
        async with session.post(url=f'http://127.0.0.1:{port}/start/', json=parameters) as resp:
            answer = await resp.json()
            print(answer)
            assert resp.status == 200, f'Engine сервера  не был запущен.'
    return process


async def example():
    """Воспроизведение фразы, через /execute/"""
    parameters = [
        {'text': 'Проверка компонента успешна', 'speaker': 'xenia', 'add': True},
        {'text': 'component check successful', 'speaker': 'en_0', 'add': True},
    ]
    for parameter in parameters:
        async with aiohttp.ClientSession() as session:
            async with session.post(url=f'http://127.0.0.1:{port}/execute/', json=parameter):
                pass
        await asyncio.sleep(2)  # дать модели выговориться


async def graceful_shutdown(process: subprocess.Popen):
    """Аккуратная остановка сервера"""
    async with aiohttp.ClientSession() as session:
        # 1. остановить engine сервера (высвобождение памяти)
        print(f'Остановка engine сервера')
        async with session.get(url=f'http://127.0.0.1:{port}/stop/') as resp:
            assert resp.status == 200, f'Engine сервера не был остановлен.'
        # 2. остановить сервер
        print(f'Остановка сервера')
        async with session.get(url=f'http://127.0.0.1:{port}/shutdown/') as resp:
            assert resp.status == 200, f'Сервер не был остановлен.'

    # 3. Убедиться что процесс завершился
    process.wait(timeout=10)


async def main():
    process = await run_server()  # запуск сервера и движка
    await example()  # пример взаимодействия с сервером (получение распознанного текста реал-тайм)
    await graceful_shutdown(process=process)  # аккуратная остановка сервера


if __name__ == '__main__':
    asyncio.run(main())
