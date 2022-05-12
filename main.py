import os
from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
import requests


API_URL = 'http://127.0.0.1:8000/api'


def main_page(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Верхний блок навигации", callback_data='navigation')],
        [InlineKeyboardButton("На страницу обращений", callback_data='1')],
        [InlineKeyboardButton("На страницу общих материалов", callback_data='2')],
        [InlineKeyboardButton("На страницу курсов", callback_data='courses')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'''Hi {user.mention_markdown_v2()}\!
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


def courses_markup():
    r = requests.get(f'{API_URL}/course/')
    r = r.json()
    keyboard = []
    for c in r:
        keyboard.append([InlineKeyboardButton(c['name'], callback_data='course-'+str(c['id']))])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def courses(update: Update, context: CallbackContext):
    update.message.reply_markdown_v2(
        'Страница курсов',
        reply_markup=courses_markup(),
    )


def course_markup(id):
    r = requests.get(f'{API_URL}/course/{id}').json()
    keyboard = []
    for c in r:
        keyboard.append([InlineKeyboardButton(c['name'], callback_data='0')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def course(update: Update, context: CallbackContext):
    update.message.reply_markdown_v2(
        'Страница курсов',
        reply_markup=courses_markup(),
    )


def button(update: Update, context: CallbackContext):
    query = update.callback_query

    query.answer()

    if query.data == "navigation":
        query.edit_message_text(text="Верхний блок навигации", reply_markup=navigation_markup())

    if query.data == "courses":
        query.edit_message_text(text="Страница курсов", reply_markup=courses_markup())


    if query.data.startswith('course-'):
        id = query.data.split('-')[1]
        r = requests.get(f'{API_URL}/course/{id}').json()
        t = requests.get(r['teacher']).json()
        message = f'''{r["name"]}

Преподаватель: {t["name"]} (*telegram_nickname*) [{t["table_link"]}]

Группы: '''

        groups = []
        for g in r['course_groups']:
            groups.append(g['name'])

        message += ', '.join(groups)
        
        message += f'\n\nПравила: {r["rules"]}'

        message += f'\n\nОбязательно ли: {r[""]}'

        query.edit_message_text(text=message)


def main():
    updater = Updater(os.environ['TOKEN'])

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", main_page)) # Для вызова через /
    dispatcher.add_handler(CommandHandler("navigation", navigation))
    dispatcher.add_handler(CommandHandler("courses", courses))
    dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling() # Ожидаем действий от пользователя

    updater.idle() # Чтобы работал Ctrl+C


if __name__ == '__main__':
    main()