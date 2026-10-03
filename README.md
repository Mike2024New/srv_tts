# 🎙️ TTS SILERO OFFLINE

**Оффлайн озвучка текста в реальном времени**

> Обёртка для работы с моделями [silero](https://silero.ai/).
> Если ни фига не понятно, то отправьте этот текст в ваш любимый ИИ, ставлю 5 шерифов 🤠🤠🤠🤠🤠 из 5, что он разберется и
> скажет что делать.

## Содержание

- [Примечание о безопасности (дисклеймер)](#примечание-о-безопасности-дисклеймер)
- [О проекте](#о-проекте)
- [Системные требования](#системные-требования)
- [Быстрый старт](#быстрый-старт)
- [Связанные репозитории](#связанные-репозитории)
- [Лицензии](#лицензии)
- [Примечания](#примечания)

---

## Примечание о безопасности (Дисклеймер)

Проекты srv-стандарта построены на базе экосистемы Open Source и используют компоненты из разных публичных источников:
библиотеки из репозитория [PyPI](https://pypi.org/), языковые модели с [HuggingFace](https://huggingface.co/), голосовые
движки [Silero](https://silero.ai/), [Vosk](https://alphacephei.com/vosk/) и другие.

Большинство из них распространяются под открытыми лицензиями (MIT, Apache 2.0), но важно учитывать специфику
современного ПО: любой компонент тянет за собой длинную цепочку вложенных зависимостей. Проверить каждый сторонний байт,
модель или скрипт до последнего символа физически невозможно — это классический эффект «черного ящика», характерный для
большинства ИТ-продуктов в мире.

Это не означает, что перечисленные инструменты опасны. Это означает, что **абсолютная гарантия безопасности невозможна**
для любого проекта, использующего внешние библиотеки.

Устанавливая данное приложение, вы принимаете стандартные риски использования Open Source решений. В целях
информационной гигиены любые экспериментальные локальные ИИ-системы рекомендуется запускать в изолированных окружениях
или на рабочих машинах, отдельно от критически важных личных кабинетов и онлайн-банкинга.

---

## О проекте

Микросервис для оффлайн озвучки текста. Может быть интегрирован с другими сервисами.

- **Потоковая озвучка в реальном времени** — речь начинается мгновенно, не нужно ждать генерации целого аудиофайла. Чанк
  за чанком, как живой разговор
- **REST API** — встраивай в свои проекты на Python, Go, JavaScript, C# — на любом языке
- **Готовый .exe** — для тех, кто не пишет код. Запустил и работает (после сборки, либо скачивания лаунчером).
- **Кроссплатформа** — Windows, Linux. Везде одинаково
- **Решена проблема нормализации чисели англицизмов**

---

## Системные требования

- Версия python 3.12.

**Для Windows:**
Может потребоваться пакет **Microsoft Visual C++ Redistributable**. Скачать можно
с [официального сайта Microsoft](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170).

**Для Linux:**
Может потребоваться установка аудио-библиотек:

```bash
sudo apt install libportaudio2 portaudio19-dev libasound-dev -y
```

---

## Быстрый старт

> В примерах ниже упоминается подключение к `8000 порту`, порт может быть и любым другим.

### 1. Клонирование

```bash
git clone git@github.com:Mike2024New/srv_tts.git srv_tts
cd srv_tts
```

### 2. Создать виртуальное окружение

> Важно! Папка с виртуальным окружением должна называться `.venv`

```bash
# Windows
python -m venv .venv && .venv\Scripts\activate

# Linux
python3 -m venv .venv && source .venv/bin/activate
```

### 3. Установить зависимости

`python start.py` # автоматически подхватятся все зависимости с которыми работает пакет, а также скачаются модели
silero ['v3_en.pt', 'v5_5_ru.pt'], скачать дополнительные модели можно [здесь](https://silero.ai/), за тем положить их
по пути: `<корень проекта>/resources/models`

### 4. Запустить сервер

`python cli.py run-server -p 8000` - запустится на 8000 порту.

### 5. Запустить движок

<details>
<summary>См. подробный пример.</summary>

```python
import requests

# запуск engine сервиса с передачей параметров. (Метод идемпотентен)
# поддерживается мультизагрузка нескольких моделей речи одновременно, может быть полезно для переводчиков
requests.post(
    url=f'http://localhost:8000/start/',
    json={
        'samplerate': 48000,  # частота замеров в секунду звуковой волны (дискретизация в ГЦ)
        'blocksize': 2048,  # размер одного блока данных
        'models': ['v5_5_ru.pt', 'v3_en.pt'],  # модели silero (ru - русскоязычная модель, en - англоязычная)
    },
)

# Опционально: проверка что engine запущен
response = requests.get(url='http://localhost:8000/parameters/')
assert response.status_code == 200
parameters = response.json()
assert parameters.get('parameters', {})
assert parameters.get('running') is True

```

</details>
> Модель синтеза речи загружена в память.

Дополнительные модели можно скачать на https://models.silero.ai/models/tts/ , положить их в папку
resources/models.

### 6. Просмотр списка доступных моделей

<details>
<summary>См. подробный пример.</summary>

```python

import requests

url = 'http://localhost:8000/models/'

response = requests.get(url)
assert response.json()  # например {'v5_5_ru.pt': ['aidar', 'baya', 'kseniya', 'eugene', 'xenia']}

```

</details>

### 7. Использовать api /execute/, для воспроизведения текста.

<details>

<summary>Пример 1. Воспроизведение текста с продолжением.</summary>

Пример воспроизведения текста с продолжением. Актуально для тех ситуаций когда текст во внешнем приложении есть весь не
сразу. Например llm генерирует токены, оркестратор собирает их в предложение и отправляет сюда на воспроизведение.

```python

import requests
from time import sleep

# воспроизведение предложения, текста
requests.post(
    url=f'http://localhost:8000/execute/',
    json={
        'text': 'Начинаю говорить текст,',
        'speaker': 'xenia',  # чьим голосом произносить текст, см список голосов и моделей в /models/
    }
)

# допустим модель сгенерировала еще одно предложение, нужно его добавить к воспроизведению
requests.post(
    url=f'http://localhost:8000/execute/',
    json={
        'text': 'продолжаю говорить текст.',
        'speaker': 'xenia',  # чьим голосом произносить текст, см список голосов и моделей в /models/
        # здесь add=True, означает что добавить этот текст в очередь и воспроизвести после предыдущего http запроса
        'add': True,
    }
)

# прерывание текста (опционально если требуется - перебить модель)
sleep(1.5)
requests.get(url='http://localhost:8000/interrupt/')

```

</details>

<details>

<summary>Пример 2. Воспроизведение текста с прерыванием новым текстом.</summary>

```python
import requests
from time import sleep

# воспроизведение предложения, текста
requests.post(
    url=f'http://localhost:8000/execute/',
    json={
        'text': 'Начинаю говорить текст,',
        'speaker': 'aidar',  # чьим голосом произносить текст, см список голосов и моделей в /models/
    }
)

sleep(0.8)

# перебивание модели и воспроизведение нового текста
requests.post(
    url=f'http://localhost:8000/execute/',
    json={
        'text': 'Другой голос мгновенно говорит другой текст.',
        'speaker': 'xenia',  # чьим голосом произносить текст, см список голосов и моделей в /models/
        # здесь 'add': False, означает что если с предыдущего запроса воспроизводится голос, то он будет прерван и начнется новый текст
        'add': False,
    }
)

```

</details>

### 8. Остановка сервиса.

#### Остановить сервис можно двумя вариантами:

- нажав ctrl+c в терминале (нужно немного подождать, для корректного завершения процессов).
- выполнив get запрос `http://localhost:8000/shutdown/`

> Произойдет полная остановка текущего сервиса, и запущенного внутри стриминга, память будет высвобождена.

### 9. Собрать exe/bin из лаунчера (если планируется работать не из кода)

`python cli.py build -oe` - oe соберет приложение одним файлом. Путь покажет в консольном выводе.

> см. подробнее справку в `python cli.py --help`

### 10. Полный рабочий пример с запуском, полезной нагрузкой и остановкой движка

Продублирован в  [example.py](example.py), чтобы запустить его выполнить `python example.py`

<details>
<summary>См. пример.</summary>

```python

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



```

</details>

---

## Связанные репозитории

- [infrastructure2](https://github.com/Mike2024New/infrastructure2) — набор утилит (сервер, логи, сборка)

---

## Лицензии

* Этот проект распространяется под лицензией MIT. Подробнее в файле [LICENSE](LICENSE).
* Модели **Silero** (.pt файлы) распространяются под лицензией CC BY-NC-SA 4.0.
  См. [источник](https://silero.ai/).

---

## Примечания

- Список моделей можно расширить: нужно скачать [модели](https://models.silero.ai/models/tts/), и разместить их
  по пути - <корневая папка приложения>/resources/models
- Сервисы, построенные на базе этого шаблона предназначены для desktop приложений (не web), но можно например
  скомпилировав .bin развернуть приложение на сервере и управлять им дергая его через api локальной сети через внешний
  оркестратор.
- Проект использует утилиты из репозитория [infrastructure2](https://github.com/Mike2024New/infrastructure2).

> Если ни фига не понятно, то отправьте этот текст в ваш любимый ИИ, ставлю 5 шерифов 🤠🤠🤠🤠🤠 из 5, что он разберется и
> скажет что делать.
> Не силен в грамматике, мог забыть где-то поставить запятые, поэтому ставлю их здесь (,,,,,,,,,,,,,,,,,,,,,,,), с
> запасом.