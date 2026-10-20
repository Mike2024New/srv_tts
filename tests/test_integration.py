import asyncio, subprocess, aiohttp, sys, uuid
from pathlib import Path

import pytest
from infrastructure_http_clients import ServerProbe
from infrastructure_path_utils import get_root_dir_path
from infrastructure_process_utils import find_free_port
from config import settings

ROOT_DIR = get_root_dir_path()
PORT = find_free_port(start_port=8000)
REQUEST_ID = f"test_{str(uuid.uuid4())[:4]}"


async def run_server() -> subprocess.Popen:
    # 1.запустить сервер
    cmd = [sys.executable, 'cli.py', 'run-server', '--port', str(PORT), '--log-level', 'info']
    process = subprocess.Popen(cmd, cwd=Path.cwd())

    # 2. Ожидание запуска сервера (пока сервер не станет отвечать на /health/, например torch загружается долго)
    print(f'Ожидание запуска сервера')
    ServerProbe.wait_for_server_up(
        url=f'http://127.0.0.1:{PORT}/health/',
        timeout=30,
        expected_status=200,
    )

    # 3. Запуск engine, с переданными параметрами модели
    async with aiohttp.ClientSession() as session:
        parameters = {'samplerate': 48000, 'blocksize': 2048, 'models': ['v5_5_ru.pt', 'v3_en.pt']}
        print(f'Запуск engine сервера')
        async with session.post(
                url=f'http://127.0.0.1:{PORT}/start/',
                json=parameters,
                params={'request_id': REQUEST_ID}
        ) as resp:
            answer = await resp.json()
            print(answer)
            assert resp.status == 200, f'Engine сервера  не был запущен.'
    return process


async def example():
    """Воспроизведение фразы, через /execute/"""
    # чтобы не испугать разработчика во время тестов (неожиданно звук из колонок), просто пустые строки
    parameters = [
        {'text': ' ', 'speaker': 'xenia', 'add': True},
        {'text': ' ', 'speaker': 'en_0', 'add': True},
    ]
    for parameter in parameters:
        async with aiohttp.ClientSession() as session:
            async with session.post(url=f'http://127.0.0.1:{PORT}/execute/', json=parameter):
                pass
        await asyncio.sleep(2)  # дать модели выговориться


async def graceful_shutdown(process: subprocess.Popen):
    """Аккуратная остановка сервера"""
    async with aiohttp.ClientSession() as session:
        # 1. остановить engine сервера (высвобождение памяти)
        print(f'Остановка engine сервера')
        async with session.get(url=f'http://127.0.0.1:{PORT}/stop/') as resp:
            assert resp.status == 200, f'Engine сервера не был остановлен.'
        # 2. остановить сервер
        print(f'Остановка сервера')
        async with session.get(url=f'http://127.0.0.1:{PORT}/shutdown/') as resp:
            assert resp.status == 200, f'Сервер не был остановлен.'

    # 3. Убедиться что процесс завершился
    process.wait(timeout=10)


async def test_integration():
    # потом поправить, убрать жесткую привязку к конкретным файлам
    ru_v5_model = settings.models_dir_prop / 'v5_5_ru.pt'
    en_v3_model = settings.models_dir_prop / 'v3_en.pt'
    if not ru_v5_model.exists():
        pytest.skip("Отсутствует модель `v5_5_ru.pt`, тест интеграции пропущен")
    if not en_v3_model.exists():
        pytest.skip("Отсутствует модель `v3_en.pt`, тест интеграции пропущен")

    process = await run_server()  # запуск сервера и движка
    await example()  # пример взаимодействия с сервером (получение распознанного текста реал-тайм)
    await graceful_shutdown(process=process)  # аккуратная остановка сервера
