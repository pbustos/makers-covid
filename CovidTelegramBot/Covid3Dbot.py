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



logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

TOKEN="1126502323:AAGrh6ef31YrNbUjG5pXVptJJd0ymdVTTFc"


TIPOUSUARIO, CIUDAD, CAPACTUAL = range(3)

def start(update, context):
    reply_keyboard = [['Maker', 'Solicitante', 'Otro']]
    user = update.message.from_user
    update.message.reply_text(
        'Hola, este bot tiene como objetivo facilitar la distribución de viseras creadas por los makers extremeños en la lucha contra el COVID-19. '
        'Envía /cancel si no quieres continuar el proceso. Si quieres continuar, indica a continuación si eres Maker o Solicitante.\n\n'
        'Eres Maker o Solicitante?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    usuariotelegram = user.username
    json_bot={"Usuario Telegram":usuariotelegram}
    with open(usuariotelegram+'.json', 'w') as file:
        json.dump(json_bot, file, indent=4)

    return TIPOUSUARIO


def tipousuario(update, context):
    #reply_keyboard = [['Cáceres', 'Badajoz', 'Valverde de Leganés', 'Merida', 'Zafra', 'Montijo', 'Miajadas', 'Logrosan', 'Plasencia', 'Almendralejo', 'Montanchez','Don Benito, Villanueva de la Serena', 'Sierra de Gata-Moraleja', 'Other']]
    user = update.message.from_user
    usuariotelegram = user.username
    logger.info("Tipo de usuario %s: %s", user.first_name, update.message.text)
    update.message.reply_text('Genial, indica la ciudad donde realizas la producción ')
    tipodeusuario=update.message.text
    with open(usuariotelegram+'.json') as file:
        json_bot = json.load(file)
    json_bot["Tipousuario"]=tipodeusuario
    with open(usuariotelegram+'.json', 'w') as file:
        json.dump(json_bot, file, indent=4)
    return CIUDAD

def Ciudad(update, context):
    user = update.message.from_user
    usuariotelegram = user.username
    #reply_keyboard = [['Cáceres', 'Badajoz', 'Valverde de Leganés', 'Merida', 'Zafra', 'Montijo', 'Miajadas', 'Logrosan', 'Plasencia', 'Almendralejo', 'Montanchez','Don Benito, Villanueva de la Serena', 'Sierra de Gata-Moraleja', 'Other']]
    logger.info("Ciudad: %s", update.message.text)
    ciudad=update.message.text
    with open(usuariotelegram+'.json') as file:
        json_bot = json.load(file)
    json_bot["Ciudad"]=ciudad
    with open(usuariotelegram+'.json', 'w') as file:
        json.dump(json_bot, file, indent=4)
    update.message.reply_text('A continuación, indica la cantidad actual de productos fabricados: '
                              )

    return CAPACTUAL

def Capactual(update, context):
    user = update.message.from_user
    usuariotelegram = user.username
    logger.info("Capacidad : %s", update.message.text)
    Produccionactual=update.message.text
    update.message.reply_text('Muchas gracias, su capacidad actual ha sido actualizada')
    with open(usuariotelegram+'.json') as file:
        json_bot = json.load(file)
    json_bot["Stock"]=Produccionactual
    with open(usuariotelegram+'.json', 'w') as file:
        json.dump(json_bot, file, indent=4)

    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)




def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            TIPOUSUARIO: [MessageHandler(Filters.regex('^(Maker|Solicitante|Other)$'), tipousuario)],

            CIUDAD: [MessageHandler(Filters.regex('^(Cáceres|Badajoz|Valverde de Leganés|Merida|Zafra|Montijo|Miajadas|Logrosan|Plasencia|Almendralejo|Montanchez|Don Benito, Villanueva de la Serena|Sierra de Gata-Moraleja|Other)$'), Ciudad)
                    ],

            CAPACTUAL: [MessageHandler(Filters.text, Capactual)]

            #DIRECCION: [MessageHandler(Filters.text, address)]
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