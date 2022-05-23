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

    message = f"Ваши итоговые данные:\n{facts_to_str(user_data)}"
    if not user_data:
        message = "Вы ничего не ввели.\n"

    update.message.reply_text(
        message + "\nЕсли захотите поменять данные, введите команду /start",
        reply_markup=ReplyKeyboardRemove(), # Удаляем клавиатуру.
    )

    courses(update, context)

    return ConversationHandler.END


def received_information(update: Update, context: CallbackContext) -> int:
    """Тут происходит запоминание записанного пользователем."""
    user_data = context.user_data
    text = update.message.text # То, что сейчас вводит пользователь.
    category = user_data['choice']
    user_data[category] = text # 'Игнатий' будет относиться к 'Имя'
    del user_data['choice'] # Бот забывает ненужную часть информации о пользователе (Фамилия|Имя|Группа|Дисциплина).

    update.message.reply_text(
        "Ваши данные:\n"
        f"{facts_to_str(user_data)}"
        '\nЕсли Вы всё заполнили, нажмите кнопку "Готово"',
        reply_markup=markup,
    )

    return CHOOSING


# def main_markup(update: Update, context: CallbackContext):
#     keyboard = [
#         # [InlineKeyboardButton("Верхний блок навигации", callback_data='navigation')],
#         [InlineKeyboardButton("Обращения", callback_data='1')],
#         # [InlineKeyboardButton("Общие материалы", callback_data='2')],
#         [InlineKeyboardButton("Курсы", callback_data='courses')],
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     user = update.effective_user # Telegram-nickname пользователя.
#     user_data = context.user_data # То, что пользователь ввёл в поле "Имя".
#     return {
#         "text": fr'''Привет, {user_data.get('Имя', user.mention_markdown_v2())}\!
# Главная страница
#         ''',
#         "reply_markup":reply_markup,
#     }


# def main_page(update: Update, context: CallbackContext):
#     # Умная система здоровается с пользователем по тому, что он ввёл в имя или по его Telegram-никнейму, если не введено первое.
#     update.message.reply_markdown_v2(**main_markup(update, context))


# def navigation_markup():
#     keyboard = [
#         [InlineKeyboardButton("Главная страница", callback_data='main')],
#         [InlineKeyboardButton("Настройка курсов", callback_data='1')],
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     return reply_markup


# def navigation(update: Update, context: CallbackContext):
#     user = update.effective_user
#     update.message.reply_markdown_v2(
#         fr'''Hi {user.mention_markdown_v2()}\!
# Страница навигации
#         ''',
#         reply_markup=navigation_markup(),
#     )


# Без markup - назначаем на команду Telegram со /
# С markup - формирование сообщения.
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
    # keyboard.append([InlineKeyboardButton("К главной странице", callback_data='main')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def courses(update: Update, context: CallbackContext):
    user_data = context.user_data # Для того, что пользователь ввёл в поле "Имя".
    user = update.effective_user # Telegram-nickname пользователя.
    # Умная система здоровается с пользователем по тому, что он ввёл в имя или по его Telegram-никнейму, если не введено первое.
    hello = fr"Привет, {user_data.get('Имя', user.mention_markdown_v2())}\!"
    if "Группа" in user_data:
        msg = hello + f'\nКурсы для группы {user_data["Группа"]}:'
    else:
        msg = hello + '\nВсе курсы:' # Если пользователь не ввёл группу, то показываются все курсы.
    update.message.reply_markdown_v2(
        msg,
        reply_markup=courses_markup(context),
    )


def course_description(course, teacher):

    message = f'''{course["name"]}

Преподаватель: {teacher["name"]} (@{teacher["telegram_nickname"]})\nТаблица баллов преподавателя:\n{teacher["table_link"]}

Группы: '''

    groups = []
    for g in course['course_groups']:
        groups.append(g['name'])

    message += ', '.join(groups)

    message += f'\n\nПравила:\n{course["rules"]}\n\n'

    message += "Материалы:\n\n"

    for m in course['course_materials']:
        message += f'{m["material_name"]}, ссылка: {m["link"]}\n'

    # message += "\nЛабораторные:\n\n"

    # labs = []
    # for lab in course['course_labs']:
    #     lab_info = requests.get(f'{API_URL}/lab/{lab["id"]}').json()
    #     message += f'{lab["number"]} с дедлайном {lab["deadline"]}.\nСсылки:\n'
    #     for link in lab_info.get('links', []):
    #         message += link['link'] + "\n"

    return message


def course_markup(id):
    keyboard = []
    r = requests.get(f'{API_URL}/course/{id}').json()
    t = requests.get(r['teacher']).json()

    message = course_description(r, t)

    for lab in r['course_labs']:
        keyboard.append([InlineKeyboardButton("Лабораторная " + lab['number'], callback_data='lab-'+str(lab['id']))])

    keyboard.append([InlineKeyboardButton("К списку курсов", callback_data='courses')])

    return {"text": message, "reply_markup": InlineKeyboardMarkup(keyboard)}


def lab_markup(id):
    keyboard = []
    lab = requests.get(f'{API_URL}/lab/{id}').json()

    course_id = lab["course"].strip("/").split("/")[-1]

    course = requests.get(f'{API_URL}/course/{course_id}').json()
    teacher = requests.get(course['teacher']).json()

    message = course_description(course, teacher) + "\n"

    message += f"Лабораторная {lab['number']}:\n\n"

    message += f"Дедлайн: {lab['deadline']}\n\n"

    message += "Ссылки:\n"

    for link in lab.get('links', []):
        message += link['link'] + "\n"

    keyboard.append([InlineKeyboardButton("Написать преподавателю", url=f"tg://resolve?domain={teacher['telegram_nickname']}")])
    # keyboard.append([InlineKeyboardButton("Попросить продлить дедлайн", url=f"tg://msg?text=Mi_mensaje&to=@{teacher['telegram_nickname']}")]) # Только для iOS.
    keyboard.append([InlineKeyboardButton("К списку лабораторных", callback_data=f'course-{course_id}')])

    return {"text": message, "reply_markup": InlineKeyboardMarkup(keyboard)}


# Обработка нажатия любой кнопки.
def button(update: Update, context: CallbackContext):
    query = update.callback_query

    query.answer()

    # if query.data == "navigation":
    #     query.edit_message_text(text="Верхний блок навигации", reply_markup=navigation_markup())

    if query.data == "courses":
        query.edit_message_text(text="Страница курсов", reply_markup=courses_markup(context))

    # if query.data == "main":
    #     query.edit_message_text(**main_markup(update, context))

    if query.data.startswith('course-'):
        id = query.data.split('-')[1]
        query.edit_message_text(**course_markup(id))

    if query.data.startswith('lab-'):
        id = query.data.split('-')[1]
        query.edit_message_text(**lab_markup(id))


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
    # dispatcher.add_handler(CommandHandler("main", main_page)) # Для вызова через /
    # dispatcher.add_handler(CommandHandler("navigation", navigation))
    dispatcher.add_handler(CommandHandler("courses", courses))
    dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling() # Ожидаем действий от пользователя

    updater.idle() # Чтобы работал Ctrl+C


if __name__ == '__main__':
    main()
