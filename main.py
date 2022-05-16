import os
from telegram import (
    Update, # Благодаря этому происходит обновление текста, который пишет бот. Используется для отправки сообшений пользователю.
    ForceReply,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    CallbackContext, # Хранит информацию.
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    Filters,
    MessageHandler,
    PicklePersistence,
    Updater,
)
from typing import Dict
import requests


API_URL = 'http://127.0.0.1:8000/api'

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3) # Три состояния диалога.

reply_keyboard = [
    ['Фамилия', 'Имя'],
    ['Группа', 'Дисциплина'],
    ['Готово'],
]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True) # Кнопки из меню сообщений.


def facts_to_str(user_data: Dict[str, str]) -> str:
    """Определяем формат информации о пользователе."""
    facts = [f'{key} - {value}' for key, value in user_data.items()]
    return "\n".join(facts).join(['\n', '\n'])


def start(update: Update, context: CallbackContext) -> int:
    """Start the conversation and ask user for input."""
    update.message.reply_text(
        "Заполните каждый пункт о себе, поочерёдно нажимая кнопки.",
        reply_markup=markup,
    )
    return CHOOSING # Возвращает одно из состояний диалога.


# def enter_name(update: Update, context: CallbackContext) -> int:
#     """Ask the user for info about the selected predefined choice."""
#     text = update.message.text
#     context.user_data['choice'] = text
#     # update.message.reply_text(f'Your {text.lower()}? Yes, I would love to hear about that!')
#     update.message.reply_text('Введите Ваше имя:')
#     return TYPING_REPLY

# def regular_choice(update: Update, context: CallbackContext) -> int:
#     """Ask the user for info about the selected predefined choice."""
#     text = update.message.text
#     context.user_data['choice'] = text
#     # update.message.reply_text(f'Your {text.lower()}? Yes, I would love to hear about that!')
#     update.message.reply_text('Имя?')
#     return TYPING_REPLY


def custom_choice(update: Update, context: CallbackContext) -> int:
    """Функция записывает информация пользователя в зависимости от нажатой кнопки."""
    text = update.message.text
    update.message.reply_text(f'Введите поле "{text}":')
    context.user_data['choice'] = text # Запоминем, что ввёл пользователь.
    # update.message.reply_text(
    #     'Alright, please send me the category first, for example "Most impressive skill"'
    # )
    return TYPING_REPLY


def done(update: Update, context: CallbackContext) -> int:
    """Итоговое сообщение по нажатию кнопки "Готово"."""
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']

    update.message.reply_text(
        "Ваши итоговые данные:"
        f"{facts_to_str(user_data)}"
        "Если захотите поменять данные, введите команду /start",
        reply_markup=ReplyKeyboardRemove(), # Удаляем клавиатуру.
    )

    main_page(update, context)

    return ConversationHandler.END


def received_information(update: Update, context: CallbackContext) -> int:
    """Тут происходит запоминание записанного пользователем."""
    user_data = context.user_data
    text = update.message.text # То, что сейчас вводит пользователь.
    category = user_data['choice']
    user_data[category] = text # 'Игнатий' будет относиться к 'Имя'
    del user_data['choice'] # Бот забывает ненужную часть информации о пользователе (Фамилия|Имя|Группа|Дисциплина).

    update.message.reply_text(
        "Ваши данные:"
        f"{facts_to_str(user_data)}"
        'Если Вы всё заполнили, нажмите кнопку "Готово"',
        reply_markup=markup,
    )

    return CHOOSING


def main_page(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Верхний блок навигации", callback_data='navigation')],
        [InlineKeyboardButton("На страницу обращений", callback_data='1')],
        [InlineKeyboardButton("На страницу общих материалов", callback_data='2')],
        [InlineKeyboardButton("На страницу курсов", callback_data='courses')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    user = update.effective_user # Telegram-nickname пользователя.
    user_data = context.user_data # То, что пользователь ввёл в поле "Имя".
    # Умная система здоровается с пользователем по тому, что он ввёл в имя или по его Telegram-никнейму, если не введено первое.
    update.message.reply_markdown_v2(
        fr'''Привет, {user_data.get('Имя', user.mention_markdown_v2())}\!
Главная страница
        ''',
        reply_markup=reply_markup,
    )


def navigation_markup():
    keyboard = [
        [InlineKeyboardButton("Главная страница", callback_data='0')],
        [InlineKeyboardButton("Таблица баллов", callback_data='1')],
        [InlineKeyboardButton("Настройка курсов", callback_data='2')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def navigation(update: Update, context: CallbackContext):
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'''Hi {user.mention_markdown_v2()}\!
Страница навигации
        ''',
        reply_markup=navigation_markup(),
    )


def courses_markup(context: CallbackContext):
    user_data = context.user_data

    r = requests.get(f'{API_URL}/course/')
    r = r.json()

    keyboard = []
    for c in r:
        common = c["common_part"]
        groups = set()
        for g in c["course_groups"]:
            groups.add(g["name"])

        # Только в случаях, если общий для всех курс, если пользователь не ввёл группу, или если в списке курса есть группа пользователя, то выводим соответствующие курсы.
        if common or user_data.get("Группа", "") == "" or user_data.get("Группа", "") in groups:
            keyboard.append([InlineKeyboardButton(c['name'], callback_data='course-'+str(c['id']))])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def courses(update: Update, context: CallbackContext):
    user_data = context.user_data
    # print("Data: ", user_data)
    if "Группа" in user_data:
        msg = f'Курсы для группы {user_data["Группа"]}:'
    else:
        msg = 'Все курсы:' # Если пользователь не ввёл группу, то показываются все курсы.
    update.message.reply_markdown_v2(
        msg,
        reply_markup=courses_markup(context),
    )


def course_markup(id):
    r = requests.get(f'{API_URL}/course/{id}').json()
    keyboard = []
    for c in r:
        keyboard.append([InlineKeyboardButton(c['name'], callback_data='0')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def course(update: Update, context: CallbackContext):
    user_data = context.user_data
    update.message.reply_markdown_v2(
        'Курс ...',
        reply_markup=course_markup(),
    )


def button(update: Update, context: CallbackContext):
    query = update.callback_query

    query.answer()

    if query.data == "navigation":
        query.edit_message_text(text="Верхний блок навигации", reply_markup=navigation_markup())

    if query.data == "courses":
        query.edit_message_text(text="Страница курсов", reply_markup=courses_markup(context))


    if query.data.startswith('course-'):
        id = query.data.split('-')[1]
        r = requests.get(f'{API_URL}/course/{id}').json()
        t = requests.get(r['teacher']).json()
        message = f'''{r["name"]}

Преподаватель: {t["name"]} (@{t["telegram_nickname"]}) [{t["table_link"]}]

Группы: '''

        groups = []
        for g in r['course_groups']:
            groups.append(g['name'])

        message += ', '.join(groups)

        message += f'\n\nПравила: {r["rules"]}'

        labs = []
        for lab in r['course_labs']:
            labs.append(lab['number'])
            message += f'{lab["number"]} с дедлайном {lab["deadline"]}, ссылки:\n'
            for link in lab.get('links', []):
                message += link['link'] + "\n"

        query.edit_message_text(text=message)



def main():
    persistence = PicklePersistence(filename='conversationbot')
    updater = Updater(
        os.environ.get('TOKEN', ''),
        persistence=persistence,
    )

    dispatcher = updater.dispatcher

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(
                    Filters.regex("^(Фамилия|Имя|Группа|Дисциплина)$"),
                    # Регулярное выражение для запуска функции custon_choice
                    custom_choice
                ),
            ], # Состояние диалога, когда идёт выбор, что вводить.

            TYPING_CHOICE: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Готово$')),
                    # Происходит, если не Telegram-команды (через "/") и не кнопка "Готово"
                    custom_choice
                )
            ], # Состояние диалога, когда идёт печать того, что мы хотим дать боту.

            TYPING_REPLY: [
                MessageHandler(
                    Filters.text & ~(Filters.command | Filters.regex('^Готово$')),
                    received_information,
                )
            ], # Состояние диалога, когда бот уже получил какую-либо информацию.
        },
        fallbacks=[MessageHandler(Filters.regex("^Готово$"), done)], # Что будет, если введётся слово "Готово"
        name="info", # Это имя носит объект диалога.
        persistent=True, # Чтобы другие функции имели доступ к тому, что введено в этом диалоге.
    )
    dispatcher.add_handler(conv_handler) 

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("main", main_page)) # Для вызова через /
    dispatcher.add_handler(CommandHandler("navigation", navigation))
    dispatcher.add_handler(CommandHandler("courses", courses))
    dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling() # Ожидаем действий от пользователя

    updater.idle() # Чтобы работал Ctrl+C


if __name__ == '__main__':
    main()
