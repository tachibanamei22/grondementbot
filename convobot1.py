import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

GENDER, PHOTO, LOCATION, BIO = range(4)

def start(update, context):
    reply_keyboard = [['Boy', 'Girl', 'Other']]

    update.message.reply_text(
        'Hello there! I am Grondement. I will talk to you here! '
        'Type /cancel to stop talking with me. \n\n'
        'Firstly, are you a boy or a girl?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return GENDER

def gender(update, context):
    user = update.message.from_user
    logger.info("Gender of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('Gorgeous! Please send me a photo of yourself, '
                              ' so I know what you look like, or you can send /skip if you dont want to.',
                              reply_markup=ReplyKeyboardRemove())
    return PHOTO

def photo(update, context):
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('user_photo.jpg')
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text('Wonderful! Mind to send me your location please? '
                              ' or send /skip if you dont want to send me.')
    return LOCATION

def skip_photo(update, context):
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    update.message.reply_text('Its ok! I bet you look great anyway! Now, can you send me your location please? '
                              'or send /skip.')
    return LOCATION

def location(update, context):
    user = update.message.from_user
    user_location = update.message.location
    logger.info("Location of %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude)
    update.message.reply_text('Great! Maybe I can pay a visit there! '
                              'Lastly, can you tell me something about yourself?')
    return BIO

def skip_location(update, context):
    user = update.message.from_user
    logger.info("user %s did not send a location.", user.first_name)
    update.message.reply_text('Afraid to tell me huh? Relax yourslef pals. '
                              'At last, can you tell me something about yourself?')
    return BIO

def bio(update, context):
    user = update.message.from_user
    logger.info("Bio of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('Thanks for chatting with me! I hope we can talk again sometimes!')

    return ConversationHandler.END

def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s cancelled the conversation.", user.first_name)
    update.message.reply_text('Farewell! I hope we can talk again someday pals!',
                              reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    updater = Updater("1004568616:AAED-QoeDoFZQy_c5rEW2COcoQPzoBgxff4", use_context=True)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            GENDER: [MessageHandler(Filters.regex('^(Boy|Girl|Other)$'), gender)],

            PHOTO: [MessageHandler(Filters.photo, photo),
                    CommandHandler('skip', skip_photo)],

            LOCATION: [MessageHandler(Filters.location, location),
                       CommandHandler('skip', skip_location)],

            BIO: [MessageHandler(Filters.text, bio)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()