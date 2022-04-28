from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

def main() -> None:
    updater = Updater("5378556002:AAEDfkaH8p0hzym5bkW0Qkgx0R3IDh3H0zc")

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling() # Ожидаем действий от пользователя

    updater.idle() # Чтобы работал Ctrl+C


def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Верхний блок навигации", callback_data='0')],
        [InlineKeyboardButton("На страницу обращений", callback_data='1')],
        [InlineKeyboardButton("На страницу общих материалов", callback_data='2')],
        [InlineKeyboardButton("На страницу курса/доделать", callback_data='3')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'''Hi {user.mention_markdown_v2()}\!
Главная страница
        ''',
        reply_markup=reply_markup,
    )


def navigation(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Верхний блок навигации", callback_data='0')],
        [InlineKeyboardButton("На страницу обращений", callback_data='1')],
        [InlineKeyboardButton("На страницу общих материалов", callback_data='2')],
        [InlineKeyboardButton("На страницу курса/доделать", callback_data='3')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'''Hi {user.mention_markdown_v2()}\!
Главная страница
        ''',
        reply_markup=reply_markup,
    )


def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query

    query.answer()

    query.edit_message_text(text=f"Selected option: {query.data}")


if __name__ == '__main__':
    main()