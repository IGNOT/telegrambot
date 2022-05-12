from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CallbackContext

def auth_main():

    LOGIN = 0
    PASSWORD = 1

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('auth', authorization)],
        states={
            LOGIN: [
                CallbackQueryHandler(one, pattern='^' + str(ONE) + '$'),
                CallbackQueryHandler(two, pattern='^' + str(TWO) + '$'),
            ],
            PASSWORD: [
                CallbackQueryHandler(start_over, pattern='^' + str(ONE) + '$'),
                CallbackQueryHandler(end, pattern='^' + str(TWO) + '$'),
            ],
        },
        fallbacks=[CommandHandler('start', start)],
    )
    return conv_handler


def authorization_markup():
    keyboard = [
        [InlineKeyboardButton("Войти", callback_data='0')],
        [InlineKeyboardButton("Зарегестрироваться", callback_data='1')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


def authorization(update: Update, context: CallbackContext):
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'''Hi {user.mention_markdown_v2()}\!
Страница авторизации
        ''',
        reply_markup=authorization_markup(),
    )


def enter():
