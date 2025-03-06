import os
import httpx
import json
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler
from telegram.ext import CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from main import fetch_mentors, fetch_congratulations
from pydantic import ValidationError


def start(update, context):
    mentors = fetch_mentors()
    user_chat_id = update.message.chat_id
    for mentor in mentors.mentors:
        if user_chat_id == mentor.tg_id:
            keyboard = [
                [InlineKeyboardButton('Выбрать ментора',
                                      callback_data='show_mentors')],
                [InlineKeyboardButton('Завершить',
                                      callback_data='end')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(
                "Привет! Вижу вы ментор.\n"
                "Если вы хотите поздравить другого ментора, "
                "нажмите кнопку выбора *ментора*.\n"
                "Для завершения работы бота, нажмите кнопку *завершить*.",
                reply_markup=reply_markup,
                parse_mode='Markdown',
            )
            return
    else:
        keyboard = [
            [InlineKeyboardButton('Выбрать ментора',
                                  callback_data='show_mentors')],
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "Привет!\n"
        "Я ваш бот для поздравления менторов.\n"
        "Для того что бы выбрать ментора, "
        "нажмите кнопку выбора *ментора*.\n",
        reply_markup=reply_markup,
        parse_mode='Markdown',
    )


def show_mentors(query, context, page=0):
    buttons = []
    mentors_per_page = 10
    try:
        mentors_response = fetch_mentors()
        mentors = mentors_response.mentors

        if not mentors:
            query.edit_message_text(
                text='Список менторов пока пуст. Попробуйте позже')
            return

        start_index = page * mentors_per_page
        end_index = start_index + mentors_per_page
        mentors_to_show = mentors[start_index:end_index]

        for mentor in mentors_to_show:
            full_name = f"{mentor.first_name} {mentor.last_name}"
            username = mentor.user_name
            words = full_name.split()
            if len(words) > 2:
                first_two_words = ' '.join(words[:2])
                button_text = f'{first_two_words} ... - {username}'
            else:
                button_text = f'{full_name} - {username}'
            callback = f"mentor_{mentor.tg_id}"
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


def show_congratulations(query, context):
    try:
        congratulations_response = fetch_congratulations()
        congratulations = congratulations_response.congratulations
        buttons = []

        for index, congratulation in enumerate(congratulations):
            button_text = f'{congratulation}'
            callback = f'congratulation_{index}'
            buttons.append([InlineKeyboardButton(
                button_text,
                callback_data=callback
            )])

        reply_markup = InlineKeyboardMarkup(buttons)
        query.edit_message_text(
            text='Выберите поздравление:',
            reply_markup=reply_markup
        )

    except Exception as e:
        raise e


def button_handler(update, context):
    query = update.callback_query
    query.answer()

    if query.data == 'show_mentors':
        show_mentors(query, context)

    elif query.data == 'end':
        query.edit_message_text(text='Спасибо!'
                                'Я вас запомнил, ждите поздравлений 😇')
        return

    elif query.data.startswith('page_'):
        page = int(query.data.split('_')[1])
        show_mentors(query, context, page)

    elif query.data.startswith('mentor_'):
        mentor_id = int(query.data.split('_')[1])
        context.user_data['selected_mentor'] = mentor_id
        show_congratulations(query, context)

    elif query.data.startswith('congratulation_'):
        congratulation_index = int(query.data.split('_')[1])
        congratulations_response = fetch_congratulations()
        congratulations = congratulations_response.congratulations
        selected_congratulation = congratulations[congratulation_index]

        context.user_data['selected_congratulation'] = selected_congratulation
        confirm_selection(query, context)

    elif query.data == 'send':
        send_congratulation(query, context)


def get_mentor_name_by_id(tg_id):
    mentors_response = fetch_mentors()
    mentors = mentors_response.mentors

    for mentor in mentors:
        if mentor.tg_id == tg_id:
            first_name = mentor.first_name
            last_name = mentor.last_name
            return first_name, last_name


def confirm_selection(query, context):
    selected_congratulation = context.user_data.get('selected_congratulation')
    mentor_id = context.user_data.get('selected_mentor')
    first_name, last_name = get_mentor_name_by_id(mentor_id)

    text = (
        f'*Вы выбрали ментора*: {first_name} {last_name}\n'
        f'*Поздравление*: {selected_congratulation}\n'
        'Для отправки поздравления нажмите кнопку *отправить*'
    )
    keyboard = [[InlineKeyboardButton('Отправить', callback_data='send')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(
        text=text,
        reply_markup=reply_markup,
        parse_mode='Markdown',
        )


def send_congratulation(query, context):
    chat_id = context.user_data.get('selected_mentor')
    selected_congratulation = context.user_data.get('selected_congratulation')

    context.bot.send_message(chat_id=chat_id, text=selected_congratulation)

    keyboard = [
        [InlineKeyboardButton(
            'Поздравить другого ментора',
            callback_data='show_mentors'
            )]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(
        text="""Поздравление успешно отправлено! 🎉
Хотите поздравить ещё одного ментора?""",
        reply_markup=reply_markup,
        parse_mode='Markdown',
    )


def error_handler(update, context):
    error = context.error

    if isinstance(error, httpx.ConnectError):
        print('Ошибка соединения: не удалось подключиться к серверу. ', error)
        text = """Ошибка соединения: не удалось подключиться к серверу.
        Попробуйте позже."""

    elif isinstance(error, httpx.HTTPError):
        print('Произошла ошибка при выполнении запроса. ', error)
        text = """Произошла ошибка при выполнении запроса.
        Попробуйте позже."""

    elif isinstance(error, ValidationError):
        print('Ошибка формата данных ', error)
        text = "Что-то пошло не так. Попробуйте позже."

    elif isinstance(error, json.JSONDecodeError):
        print('Ошибка формата JSON. Сервер вернул некорректные данные. ',
              error)
        text = "Что-то пошло не так. Попробуйте позже."

    elif isinstance(error, BadRequest):
        if 'Chat not found' in str(error):
            print('Выбранный пользователь не взаимодействовал с ботом. ',
                  error)
            text = (
                'Пользователь ещё не взаимодействовал с ботом. '
                'Попробуйте позже.'
            )

            keyboard = [
                [InlineKeyboardButton(
                    "Выбрать другого ментора",
                    callback_data='show_mentors'
                    )]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            if update and update.callback_query:
                update.callback_query.message.reply_text(
                    text,
                    reply_markup=reply_markup
                    )
            else:
                update.message.reply_text(text, reply_markup=reply_markup)

            return 
    else:
        print('Произошла непредвиденная ошибка. ', error)
        text = "Произошла непредвиденная ошибка. Попробуйте позже."

    if update and update.message:
        update.message.reply_text(text)

    elif update and update.callback_query:
        update.callback_query.message.reply_text(text)


def main():
    load_dotenv()

    TOKEN = os.environ['TG_BOT_TOKEN']

    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(button_handler))
    dp.add_error_handler(error_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
