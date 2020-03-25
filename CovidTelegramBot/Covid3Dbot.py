import requests
import telebot
from telegram import InlineQueryResultArticle, ParseMode, \
    InputTextMessageContent
from telegram.ext import Updater, InlineQueryHandler, CommandHandler
from telegram.utils.helpers import escape_markdown
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
import logging
import json
from uuid import uuid4
from FileManager import *

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

TOKEN = "1126502323:AAGrh6ef31YrNbUjG5pXVptJJd0ymdVTTFc"

TIPOUSUARIO, CIUDAD, CAPACTUAL = range(3)


def start(update, context):
    reply_keyboard = [['Maker', 'Solicitante', 'Otro']]
    user = update.message.from_user
    update.message.reply_text(
        'Hola, este bot tiene como objetivo facilitar la distribución de viseras creadas por los makers extremeños en la lucha contra el COVID-19. '
        'Envía /cancel si no quieres continuar el proceso. Si quieres continuar, indica a continuación si eres Maker o Solicitante.\n\n'
        'Eres Maker o Solicitante?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    datasession = load_datasession(user)

    return TIPOUSUARIO


def tipousuario(update, context):
    # reply_keyboard = [['Cáceres', 'Badajoz', 'Valverde de Leganés', 'Merida', 'Zafra', 'Montijo', 'Miajadas', 'Logrosan', 'Plasencia', 'Almendralejo', 'Montanchez','Don Benito, Villanueva de la Serena', 'Sierra de Gata-Moraleja', 'Other']]
    user = update.message.from_user
    datasession = load_datasession(user)
    datasession[str(user.id)]["Tipousuario"] = update.message.text
    write_session(user.username, datasession)
    logger.info("Tipo de usuario %s: %s", user.first_name, update.message.text)
    update.message.reply_text('Genial, indica la ciudad donde realizas la producción ')
    return CIUDAD


def Ciudad(update, context):
    user = update.message.from_user
    datasession = load_datasession(user)
    # reply_keyboard = [['Cáceres', 'Badajoz', 'Valverde de Leganés', 'Merida', 'Zafra', 'Montijo', 'Miajadas', 'Logrosan', 'Plasencia', 'Almendralejo', 'Montanchez','Don Benito, Villanueva de la Serena', 'Sierra de Gata-Moraleja', 'Other']]
    logger.info("Ciudad: %s", update.message.text)
    datasession[str(user.id)]["Localidad"] = update.message.text
    write_session(user.username, datasession)
    update.message.reply_text('A continuación, indica la cantidad actual de productos fabricados: ')
    return CAPACTUAL


def Capactual(update, context):
    user = update.message.from_user
    text = update.message.text
    datasession = load_datasession(user)
    if "+" in text:
        datasession[str(user.id)]["cantidad actual"] += int(text.replace("+", ""))
    elif "-" in text:
        datasession[str(user.id)]["cantidad actual"] -= int(text.replace("-", ""))
    else:
        datasession[str(user.id)]["cantidad actual"] = int(text)
    logger.info("Capacidad : %s", "hola")
    update.message.reply_text('Muchas gracias, su capacidad actual ha sido actualizada')
    write_session(user.username, datasession)
    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info(f"User {user.first_name} (@{user.username}) canceled the conversation.")
    update.message.reply_text('Operación canceladda. ¡Seguimos en contacto!', reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def add_masks(update, context):
    user = update.message.from_user
    text = update.message.text
    datasession = load_datasession(user)
    if " " in text:
        text = text.split(" ")
        logger.info("Capacidad : %s", text[1])
        Produccionactual = text[1]
        if "+" in Produccionactual:
            datasession[str(user.id)]["cantidad actual"] += int(Produccionactual.replace("+", ""))
        elif "-" in text:
            datasession[str(user.id)]["cantidad actual"] -= int(Produccionactual.replace("-", ""))
        else:
            datasession[str(user.id)]["cantidad actual"] += int(Produccionactual)
        logger.info("Capacidad : %s", Produccionactual)
        update.message.reply_text('Muchas gracias, su capacidad actual ha sido actualizada')
        write_session(user.username, datasession)
        return ConversationHandler.END
    else:
        update.message.reply_text('A continuación, indica la cantidad actual de productos fabricados: ')
        return CAPACTUAL


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start), CommandHandler('stock', add_masks)],

        states={
            TIPOUSUARIO: [MessageHandler(Filters.regex('^(Maker|Solicitante|Other)$'), tipousuario)],

            CIUDAD: [MessageHandler(Filters.regex(
                '^(Cáceres|Badajoz|Valverde de Leganés|Merida|Zafra|Montijo|Miajadas|Logrosan|Plasencia|Almendralejo|Montanchez|Don Benito, Villanueva de la Serena|Sierra de Gata-Moraleja|Other)$'),
                Ciudad)],
            CAPACTUAL: [MessageHandler(Filters.text, Capactual)]

        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
