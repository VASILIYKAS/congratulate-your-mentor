import argparse
import json
import os
from textwrap import dedent

import httpx
from dotenv import load_dotenv
from pydantic import ValidationError
from telegram import (
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.error import BadRequest
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    PicklePersistence,
    Updater,
)

from libs.api_client import get_mentors_or_congratulations
from tests.test_urls import urls


MENTORS = '/mentors'
POSTCARDS = '/postcards'
BASE_URL = 'https://my-json-server.typicode.com/devmanorg/congrats-mentor'


def set_menu_commands(bot):
    commands = [
        BotCommand('start', 'Запустить бота'),
    ]
    bot.set_my_commands(commands)


def start(update, context):
    step = context.user_data.get('step')

    if step == 'mentor_chosen':
        update.message.reply_text('Вы остановились на выборе ментора.')

        show_greeting_themes(update, context)
        return

    elif step == 'theme_chosen':
        holiday_id = context.user_data.get('holiday_id')
        update.message.reply_text(
            'Вы остановились на выборе тематике поздравления.'
        )

        show_postcards(update, context, holiday_id)
        return

    elif step == 'mentor_and_postcard_chosen':
        update.message.reply_text(
            dedent("""\
                Вы остановились на выборе поздравления.
                Проверьте ваш выбор.
                    """)
        )

        confirm_selection(update, context)
        return

    else:
        base_url = context.bot_data.get('base_url', BASE_URL)
        mentors_response = get_mentors_or_congratulations(base_url, MENTORS)
        mentors = mentors_response.mentors
        user_chat_id = update.message.chat_id

        if not mentors:
            update.message.reply_text(
                text=dedent("""\
                    Список менторов пока пуст.
                    Попробуйте позже.
                """)
            )
            return

        for mentor in mentors:
            if user_chat_id == mentor.tg_chat_id:
                keyboard = [
                    [InlineKeyboardButton(
                        'Выбрать ментора',
                        callback_data='show_mentors')],
                    [InlineKeyboardButton(
                        'Завершить',
                        callback_data='end')],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                update.message.reply_text(
                    dedent("""\
                        Привет! Вижу вы ментор.
                        Если вы хотите поздравить другого ментора,
                        нажмите кнопку выбора *ментора*.
                        Для завершения работы бота, нажмите кнопку *завершить*.
                    """),
                    reply_markup=reply_markup,
                    parse_mode='Markdown',
                )
                return
        else:
            keyboard = [
                [InlineKeyboardButton(
                    'Выбрать ментора',
                    callback_data='show_mentors')],
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(
            dedent("""\
                Привет!
                Я ваш бот для поздравления менторов.
                Для того что бы выбрать ментора,
                нажмите кнопку выбора *ментора*.
            """),
            reply_markup=reply_markup,
            parse_mode='Markdown',
        )


def show_mentors(query, context, page=0):
    buttons = []
    mentors_per_page = 10
    base_url = context.bot_data.get('base_url', BASE_URL)
    try:
        mentors_response = get_mentors_or_congratulations(base_url, MENTORS)
        mentors = mentors_response.mentors

        start_index = page * mentors_per_page
        end_index = start_index + mentors_per_page
        paginated_mentors = mentors[start_index:end_index]

        for mentor in paginated_mentors:
            full_name = f'{mentor.name.first} {mentor.name.second}'
            username = mentor.tg_username
            words = full_name.split()
            if len(words) > 2:
                first_two_words = ' '.join(words[:2])
                button_text = f'{first_two_words} ... - {username}'
            else:
                button_text = f'{full_name} - {username}'
            callback = f'mentor_{mentor.tg_chat_id}'
            buttons.append([InlineKeyboardButton(button_text,
                                                 callback_data=callback)])

        navigation_buttons = []

        if page > 0:
            navigation_buttons.append(InlineKeyboardButton(
                '◀️',
                callback_data=f'page_{page - 1}')
            )
        if end_index < len(mentors):
            navigation_buttons.append(InlineKeyboardButton(
                '▶️',
                callback_data=f'page_{page + 1}')
            )

        if navigation_buttons:
            buttons.append(navigation_buttons)

        reply_markup = InlineKeyboardMarkup(buttons)
        query.edit_message_text(text='Выберите ментора:',
                                reply_markup=reply_markup)

    except Exception as e:
        raise e


def show_greeting_themes(update_or_query, context):
    if hasattr(update_or_query, 'message'):
        reply_func = update_or_query.message.reply_text
    else:
        reply_func = update_or_query.edit_message_text

    buttons = []
    same_names = set()
    base_url = context.bot_data.get('base_url', BASE_URL)

    try:
        postcards_response = get_mentors_or_congratulations(
            base_url,
            POSTCARDS
        )
        postcards = postcards_response.postcards

        for postcard in postcards:
            if postcard.name_ru not in same_names:
                same_names.add(postcard.name_ru)
                callback = f'theme_{postcard.holiday_id}'
                buttons.append([InlineKeyboardButton(
                    postcard.name_ru,
                    callback_data=callback
                )])

        text = 'Выберите тему поздравления'
        reply_markup = InlineKeyboardMarkup(buttons)

        reply_func(text=text, reply_markup=reply_markup)

    except Exception as e:
        raise e


def show_postcards(update_or_query, context, holiday_id, page=0):
    if hasattr(update_or_query, 'message'):
        reply_func = update_or_query.message.reply_text
    else:
        reply_func = update_or_query.edit_message_text

    buttons = []
    greetings_per_page = 3
    base_url = context.bot_data.get('base_url', BASE_URL)

    try:
        selected_mentor_id = context.user_data.get('selected_mentor')
        first_name, second_name = get_mentor_name_by_id(
            selected_mentor_id,
            base_url
        )
        postcards_response = get_mentors_or_congratulations(
            base_url,
            POSTCARDS
        )
        postcards = postcards_response.postcards

        if not postcards:
            update_or_query.edit_message_text(
                text='Список поздравлений пока пуст. Попробуйте позже')
            return

        filtered_postcards = [
            postcard
            for postcard in postcards
            if postcard.holiday_id in holiday_id
        ]

        if not filtered_postcards:
            update_or_query.edit_message_text(
                text='Нет доступных поздравлений для этой темы.')
            return

        start_index = page * greetings_per_page
        end_index = start_index + greetings_per_page
        postcards_to_show = filtered_postcards[start_index:end_index]

        for postcard in postcards_to_show:
            if isinstance(postcard.body, str):
                greeting = f'{postcard.body.replace('#name', first_name)}'
            elif isinstance(postcard.body, list):
                greeting = [
                    line.replace('#name', first_name) for line in postcard.body
                ]
                greeting = '\n'.join(greeting)

            words = greeting.split()
            if len(words) > 5:
                first_five_words = ' '.join(words[:5])
                button_text = f'{first_five_words} ...'
            else:
                button_text = f'{postcard.body}'

            callback = f'postcard_{postcard.id}'
            buttons.append([InlineKeyboardButton(
                button_text,
                callback_data=callback
            )])

        navigation_buttons = []

        if page > 0:
            navigation_buttons.append(InlineKeyboardButton(
                '◀️',
                callback_data=f'postcardpage_{holiday_id}_{page - 1}')
            )

        if end_index < len(filtered_postcards):
            navigation_buttons.append(InlineKeyboardButton(
                '▶️',
                callback_data=f'postcardpage_{holiday_id}_{page + 1}')
            )

        if navigation_buttons:
            buttons.append(navigation_buttons)

        reply_markup = InlineKeyboardMarkup(buttons)
        reply_func(
            text='Выберите поздравление:',
            reply_markup=reply_markup
        )

    except Exception as e:
        raise e


def handle_button_click(update, context):
    query = update.callback_query
    query.answer()

    if query.data == 'show_mentors':
        show_mentors(query, context)

    elif query.data == 'end':
        query.edit_message_text(text=dedent("""\
            Спасибо!
            Я вас запомнил, ждите поздравлений 😇
        """))
        return

    elif query.data.startswith('page_'):
        page = int(query.data.split('_')[1])
        show_mentors(query, context, page)

    elif query.data.startswith('mentor_'):
        context.user_data['step'] = 'mentor_chosen'
        mentor_id = int(query.data.split('_')[1])
        context.user_data['selected_mentor'] = mentor_id
        show_greeting_themes(query, context)

    elif query.data.startswith('postcard_'):
        postcard_id = int(query.data.split('_')[1])
        base_url = context.bot_data.get('base_url', BASE_URL)
        postcards_response = get_mentors_or_congratulations(
            base_url,
            POSTCARDS
        )
        postcards = postcards_response.postcards

        selected_postcard = None
        for postcard in postcards:
            if postcard.id == postcard_id:
                selected_postcard = postcard
                break

        if selected_postcard:
            context.user_data['step'] = 'mentor_and_postcard_chosen'
            context.user_data['selected_postcard'] = selected_postcard.body
            confirm_selection(query, context)

    elif query.data.startswith('theme_'):
        holiday_id = query.data.split('_')[1]
        context.user_data['step'] = 'theme_chosen'
        context.user_data['holiday_id'] = holiday_id
        show_postcards(query, context, holiday_id)

    elif query.data.startswith('postcardpage_'):
        parts = query.data.split('_')
        holiday_id = parts[1]
        page = int(parts[2])
        show_postcards(query, context, holiday_id, page)

    elif query.data == 'send':
        send_postcard(query, context)


def get_mentor_name_by_id(tg_id, base_url):
    mentors_response = get_mentors_or_congratulations(base_url, MENTORS)
    mentors = mentors_response.mentors

    for mentor in mentors:
        if mentor.tg_chat_id == tg_id:
            first_name = mentor.name.first
            second_name = mentor.name.second
            return first_name, second_name


def confirm_selection(update_or_query, context):
    if hasattr(update_or_query, 'message'):
        reply_func = update_or_query.message.reply_text
    else:
        reply_func = update_or_query.edit_message_text

    selected_postcard = context.user_data.get('selected_postcard')
    chat_id = context.user_data.get('selected_mentor')
    base_url = context.bot_data.get('base_url', BASE_URL)
    first_name, second_name = get_mentor_name_by_id(chat_id, base_url)

    if isinstance(selected_postcard, str):
        greeting_text = selected_postcard.replace('#name', first_name)
    elif isinstance(selected_postcard, list):
        greeting_text = ''.join(selected_postcard).replace('#name', first_name)

    text = dedent(f"""\
        *Вы выбрали ментора*: {first_name} {second_name}
        *Поздравление*: {greeting_text}
        Для отправки поздравления нажмите кнопку *отправить*
    """)
    keyboard = [[InlineKeyboardButton('Отправить', callback_data='send')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    reply_func(
        text=text,
        reply_markup=reply_markup,
        parse_mode='Markdown',
    )


def send_postcard(query, context):
    chat_id = context.user_data.get('selected_mentor')
    selected_postcard = context.user_data.get('selected_postcard')
    base_url = context.bot_data.get('base_url', BASE_URL)

    first_name, second_name = get_mentor_name_by_id(chat_id, base_url)

    if isinstance(selected_postcard, str):
        greeting_text = selected_postcard.replace('#name', first_name)
    elif isinstance(selected_postcard, list):
        greeting_lines = [
            line.replace('#name', first_name)
            for line in selected_postcard
            if isinstance(line, str)
        ]
        greeting_text = '\n'.join(greeting_lines)

    context.bot.send_message(chat_id=chat_id, text=greeting_text)

    keyboard = [
        [InlineKeyboardButton(
            'Поздравить другого ментора',
            callback_data='show_mentors'
        )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(
        text=(dedent("""\
            Поздравление успешно отправлено! 🎉
            Хотите поздравить ещё одного ментора?
        """)),
        reply_markup=reply_markup,
        parse_mode='Markdown',
    )

    context.user_data.clear()


def get_mentor_selection_button():
    keyboard = [
        [InlineKeyboardButton(
            'Выбрать другого ментора',
            callback_data='show_mentors'
        )]
    ]
    return InlineKeyboardMarkup(keyboard)


def handle_error(update, context):
    error = context.error

    if isinstance(error, ValidationError):
        print('Ошибка формата данных ', error)
        text = dedent("""\
            Что-то пошло не так.
            Попробуйте позже.
        """)

    elif isinstance(error, httpx.ConnectError):
        print('Ошибка соединения: не удалось подключиться к серверу. ', error)
        text = dedent("""\
            Ошибка соединения: не удалось подключиться к серверу.
            Попробуйте позже.
        """)

    elif isinstance(error, httpx.HTTPError):
        print('Произошла ошибка при выполнении запроса. ', error)
        text = dedent("""\
            Произошла ошибка при выполнении запроса.
            Попробуйте позже.
        """)

    elif isinstance(error, json.JSONDecodeError):
        print('Ошибка формата JSON. Сервер вернул некорректные данные. ',
              error)
        text = dedent("""\
            Что-то пошло не так.
            Попробуйте позже.
        """)

    elif isinstance(error, BadRequest):
        if 'Chat not found' in str(error):
            print('Выбранный пользователь не взаимодействовал с ботом.',
                  error)
            text = dedent("""\
                Пользователь ещё не взаимодействовал с ботом.
                Попробуйте позже.
            """)
            reply_markup = get_mentor_selection_button()
            context.user_data.clear()

        elif 'bot was blocked by the user' in str(error):
            print('Выбранный пользователь заблокировал бота.', error)
            text = dedent("""\
                Выбранный ментор добавил бота в бан 😢
                попробуйте убедить его разблокировать бота 😇
            """)
            reply_markup = get_mentor_selection_button()
            context.user_data.clear()

    else:
        print('Произошла непредвиденная ошибка. ', error)
        text = dedent("""\
            Произошла непредвиденная ошибка.
            Попробуйте позже.
        """)
        context.user_data.clear()

    if update and update.message:
        update.message.reply_text(text)
    elif update and update.callback_query:
        update.callback_query.message.reply_text(
            text,
            reply_markup=reply_markup
        )


def create_parser():
    parser = argparse.ArgumentParser(
        description='Запуск бота с тестовым или продакшн сервером.'
    )
    parser.add_argument('--test-case', choices=[
        'empty',
        'invalid',
        'missing_fields',
        'extra_fields',
        'extra_collection',
        'file_not_found',
        'i_am_mentor',
        'long_name_postcard',
        'many_mentors_postcards',
        'template_name',
        'wrong_types',
        '3_mentors_5_postcards'
    ],
        help=dedent("""
            Укажите название случая для тестового сервера.
            Например: --test-case empty
            По умолчанию используется продакшн сервер.
        """)
    )
    return parser


def get_url(test_case):
    return urls.get(test_case, BASE_URL)


def main():
    parser = create_parser()
    args = parser.parse_args()
    test_case = args.test_case
    load_dotenv()

    token = os.environ['TG_BOT_TOKEN']
    if not token:
        print(dedent("""
            Ошибка: Не указан TG_BOT_TOKEN.
            Убедитесь, что он задан в переменных окружения.
        """))
        return

    save_data = PicklePersistence(filename='data.pickle')
    updater = Updater(token, persistence=save_data, use_context=True)

    base_url = get_url(test_case)

    dispatcher = updater.dispatcher

    dispatcher.bot_data['base_url'] = base_url

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CallbackQueryHandler(handle_button_click))
    dispatcher.add_error_handler(handle_error)

    set_menu_commands(updater.bot)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
