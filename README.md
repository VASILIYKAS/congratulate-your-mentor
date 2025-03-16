# Бот для поздравления менторов
Скрипт предназначен для отправки поздравления менторам, бот определяет являетесь вы ментором или нет, после чего предлогает поздравить ментора или завершить работу. Бот позволяет выбрать определённого ментора из списка и открытку с поздравлением.


## Оглавление
- [Требования](#требования)
- [Установка](#установка)
    - [Переменные окружения](#переменные-окружения)
- [Структура проекта](#структура-проекта)
    - [Папка `libs`](#папка-libs)
    - [Папка `tests`](#папка-tests)
    - [Файлы в корневом каталоге](#файлы-в-корневом-каталоге)
    - [Как работает проект](#как-работает-проект)
- [Использование](#использование)
- [Тестовый сервер и тестовые запуски](#тестовый-сервер-и-тестовые-запуски)
    - [Доступные сценарии и команды](#Доступные-сценарии-и-команды)
- [Цель проекта](#цель-проекта)


## Требования
- Python 3.12.6
- `httpx` library
- `pydantic` library
- `python-telegram-bot` library
- `urllib3` library


## Установка
- Скачайте код
- Установите зависимости командой `pip install -r requirements.txt`


### Переменные окружения
Проект использует файл `.env` для хранения конфиденциальных данных, таких как токен Telegram-бота. В репозитории уже есть шаблон `example.env`, который нужно настроить:
1. Переименуйте в ручную `example.env` в `.env` или с помощью команды:
```bash
ren example.env .env
```
2. Откройте файл `.env` в текстовом редакторе.
3. Укажите значение переменной `TG_BOT_TOKEN` после знака `=`:
```python
TG_BOT_TOKEN=your_telegram_bot_token
```
Получить токен можно здесь [BotFather](https://telegram.me/BotFather).


## Структура проекта

### Папка `libs`
Содержит скрипт для выполнения запросов к серверу. Этот скрипт используется для взаимодействия с API сервера и получения данных.
Так же содержит модели Pydantic для валидации данных:
- `Name` — модель, представляющая имя, состоящее из двух частей: first и second.

- `Mentor` — модель данных ментора, содержащая следующие поля:
    - `id`: Уникальный идентификатор ментора (тип: целое число).
    - `name`: Объект `Name`, представляющий имя ментора.
    - `tg_username`: Имя пользователя ментора в Telegram (тип: строка).
    - `tg_chat_id`: Идентификатор чата ментора в Telegram (тип: целое число).
    - `bday`: Дата рождения ментора (тип: строка, необязательное поле).

- `MentorsResponse` — модель ответа, содержащая список менторов. Содержит одно поле:
    - `mentors`: Список объектов `Mentor`.

- `Postcard` — модель для хранения информации о поздравительных открытках. Содержит следующие поля:
    - `id`: Уникальный идентификатор открытки (тип: целое число).
    - `holidayId`: Идентификатор праздника (тип: строка).
    - `name_ru`: Название открытки на русском языке (тип: строка).
    - `body`: Содержимое открытки, которое может быть строкой или списком строк.

- `PostcardsResponse` — модель ответа, содержащая список поздравительных открыток. Содержит одно поле:
    - `postcards`: Список объектов `Postcard`.


### Папка `tests`
Содержит инструменты и данные для проведения тестов:
- Папка `test_data`\
Хранит тестовые данные с различными сценариями для проверки поведения бота и сервера.
- `test_server.py`\
Тестовый сервер, используемый для эмуляции API во время тестирования. Заменяет продакшн URL на тестовые, которые указаны в файле `test_urls.py`.
- `test_urls.py`\
Содержит тестовые ссылки, используемые тестовым сервером.


### Файлы в корневом каталоге
- **`bot.py`**\
Основной файл с логикой работы Telegram-бота:
    - Обработка команд и callback-запросов.
    - Запрашивает данные с сервера через `api_client.py`.
    - Отображает списки менторов и поздравлений с поддержкой пагинации.
    - Обрабатывает ошибки и уведомляет пользователя о проблемах (например, недоступность сервера).
    - Использует `PicklePersistence` для сохранения состояния пользователя.

- **`.env`**  
  Файл с переменными окружения, хранит конфиденциальные данные, такие как `TG_BOT_TOKEN`. Создается на основе `example.env`.

- **`requirements.txt`**  
  Список зависимостей проекта для установки через `pip install -r requirements.txt`.

- **`.gitignore`**  
  Указывает файлы и папки (например, `.env`, `data.pickle`), которые не должны попадать в репозиторий Git.

- **`data.pickle`**  
  Файл, создаваемый `PicklePersistence` для сохранения состояния бота (например, текущего шага пользователя). Генерируется автоматически при работе бота.

### Как работает проект
 **Бот** (`bot.py`)\
Бот взаимодействует с сервером через функцию `get_mentors_or_congratulations` из файла `api_client.py`, применяя модели валидации. Он предоставляет пользователю удобный интерфейс для выбора ментора, темы и открытки. Благодаря `PicklePersistence` бот запоминает последний шаг пользователя и, в случае внезапного отключения сервера, восстанавливает работу с того же места, где пользователь остановился.


## Использование
Для запуска выполните команду:
```bash
python bot.py
```
Если вы не указывали другие параметры запуска, то бот будет использовать продакшн сервер.
После запуска бота:
1. Напишите команду `/start` в чате с ботом или выберите её из `Меню`.
2. Бот отправит приветственное сообщение и определит, являетесь ли вы ментором.
3. Выберите ментора из списка.
4. Выберите тематику поздравления.
5. Выберите подходящее поздравление.
6. Бот покажет выбранного ментора и поздравление, а также предложит отправить поздравление.
7. После подтверждения вы получите сообщение об успешной/неуспешной отправке поздравления.


## Тестовый сервер и тестовые запуски
Проект включает тестовый сервер `test_server.py` для эмуляции API с различными сценариями. Для его запуска выполните:

```bash
python python tests/test_server.py
```
Сервер будет доступен по адресу http://127.0.0.1:8000.\
Для запуска определенного тестового сценария, нужно указать аргумент --server. \
Команда:

```bash
python python bot.py --server <название_сценария>
```


### Доступные сценарии и команды
- `empty`
```bash
python bot.py --server empty
```
Тестовый сервер возвращает пустые списки менторов и открыток. Используется для проверки поведения бота при отсутствии данных.

- `invalid`
```bash
python bot.py --server invalid
```
Сервер возвращает некорректный JSON. Проверяет обработку ошибок формата данных.

- `missing_fields`
```bash
python bot.py --server missing_fields
```
Данные с пропущенными обязательными полями. Тестирует валидацию Pydantic.

- `extra_fields`
```bash
python bot.py --server extra_fields
```
Данные с лишними полями. Проверяет, как бот игнорирует неиспользуемые поля.
- `extra_collection`
```bash
python bot.py --server extra_collection
```

Возвращает дополнительные коллекции данных. Тестирует обработку избыточных данных.
- `file_not_found`
```bash
python bot.py --server file_not_found
```

Сервер имитирует отсутствие файлов данных (404).
- `i_am_mentor`
```bash
python bot.py --server i_am_mentor
```
Сценарий, где пользователь — ментор. Бот предлагает поздравить другого ментора или завершить работу.

- `long_name_postcard`
```bash
python bot.py --server long_name_postcard
```
Открытки с длинным именем и длинным поздравлением. Тестирует отображение текста в кнопках.

- `many_mentors_postcards`
```bash
python bot.py --server many_mentors_postcards
```
Большое количество менторов и открыток. Проверяет пагинацию и работу с большими списками.

- `template_name`
```bash
python bot.py --server template_name
```
Открытки с шаблонными именами например, `#name`. Тестирует подстановку имени ментора.

- `wrong_types`
```bash
python bot.py --server wrong_types
```
Данные с неверными типами полей. Проверяет валидацию Pydantic.

- `3_mentors_5_postcards`
```bash
python bot.py --server 3_mentors_5_postcards
```
Ограниченный набор: 3 ментора и 5 открыток. Тестирует базовую функциональность с небольшим количеством данных.\
**Примечание**\
Перед запуском бота с тестовым сервером убедитесь, что test_server.py запущен в отдельном терминале.


## Цель проекта
Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).


