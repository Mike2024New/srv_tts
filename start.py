import asyncio, sys, subprocess

"""
Скрипт установки и сборки проекта.
Требуется виртуальное окружение в папке .venv

Все шаги (простая установка после клонирования с git):     python start.py all
По отдельности:
  sync        - установить зависимости
  dwn         - скачать материалы
  build       - собрать .exe/bin
"""
args = sys.argv


async def start():
    if 'sync' in args or 'all' in args:
        if 'all' in args:
            print(f'Установка uv и зависимостей', flush=True)
        cmd = [sys.executable, '-m', 'pip', 'install', 'uv']
        subprocess.run(cmd, shell=False)

        cmd = [sys.executable, '-m', 'uv', 'sync']
        subprocess.run(cmd, shell=False)

    if 'dwn' in args or 'all' in args:
        if 'all' in args:
            print(f'Загрузка дополнительных материалов', flush=True)
        from infrastructure_http_clients import file_downloader, DownloadFileType
        from config import settings

        models_dir = settings.models_dir_prop  # путь брать из property (дорисовка абсолютного к относительному)

        download_list = [
            DownloadFileType(
                url_list=[
                    'https://models.silero.ai/models/tts/ru/v5_5_ru.pt',
                ],
                target_dir=models_dir,
                filename='v5_5_ru.pt',
                replace=False,
            ),
            DownloadFileType(
                url_list=[
                    'https://models.silero.ai/models/tts/en/v3_en.pt',
                ],
                target_dir=models_dir,
                filename='v3_en.pt',
                replace=False,
            ),
        ]
        await file_downloader(download_list=download_list, console_progress_bar=True)

    if 'build' in args or 'all' in args:
        if 'all' in args:
            print(f'Сборка .exe/bin', flush=True)
        from build import build, parameters
        build(parameters=parameters)


if __name__ == '__main__':
    asyncio.run(start())
