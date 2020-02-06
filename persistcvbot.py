from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, PicklePersistence)

import logging

from convobot import done

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [['Name', 'Age'],
                  ['Hobby', 'Something else'],
                  ['Done']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def facts_to_str(user_data):
    facts = list()

    for key, value in user_data.items():
        facts.append('{} - {}'.format(key, value))

    return "\n".join(facts).join(['\n', '\n'])


def start(update, context):
    reply_text = "Greetings! I am Grondement."
    if context.user_data:
        reply_text += " You already told me about your {}. Why dont you tell me more " \
                      "about yourself? Or perhaps change anything that I " \
                      "already know about you.".format(", ".join(context.user_data.keys()))
    else:
        reply_text += " I will hold a more intense conversation with you. So why dont you tell me " \
                      "something about yourself?"
    update.message.reply_text(reply_text, reply_markup=markup)

    return CHOOSING


def regular_choice(update, context):
    text = update.message.text.lower()
    context.user_data['choice'] = text
    if context.user_data.get(text):
        reply_text = 'Your {}? I already know ' \
                     'about that: {}'.format(text, context.user_data[text])
    else:
        reply_text = 'Your {}? Yes, I would be honored to hear about that!'.format(text)
    update.message.reply_text(reply_text)

    return TYPING_REPLY


def custom_choice(update, context):
    update.message.reply_text('For sure, please send me the category first, '
                              'for example, "Most remarkable collection"')

    return TYPING_CHOICE


def received_information(update, context):
    text = update.message.text
    category = context.user_data['choice']
    context.user_data[category] = text.lower()
    del context.user_data['choice']

    update.message.reply_text("Superb! To be clear, this is what you already told me so far:"
                              "{}"
                              "You can tell me more, or you can change your opinion on "
                              "something.".format(facts_to_str(context.user_data)),
                              reply_markup=markup)

    return CHOOSING


def show_data(update, context):
    if 'choice' in context.user_data:
        del context.user_data['choice']

    update.message.reply_text("You know, I learned these facts about you:"
                              "{}"
                              "Until next meeting pals!".format(facts_to_str(context.user_data)))
    return ConversationHandler.END


def error(update, context):
    """Log Errors coused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    pp = PicklePersistence(filename='conversationbot')
    updater = Updater("1004568616:AAED-QoeDoFZQy_c5rEW2COcoQPzoBgxff4", persistence=pp, use_context=True)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            CHOOSING: [MessageHandler(Filters.regex('^(Name|Age|Hobby)$'),
                                      regular_choice),
                       MessageHandler(Filters.regex('^Something else$'),
                                      custom_choice),
                       ],
            TYPING_CHOICE: [MessageHandler(Filters.text,
                                           regular_choice),
                            ],
            TYPING_REPLY: [MessageHandler(Filters.text,
                                          received_information),
                           ],
        },

        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)],
        name="my_conversation",
        persistent=True
    )

    dp.add_handler(conv_handler)

    show_data_handler = CommandHandler('show_data', show_data)
    dp.add_handler(show_data_handler)

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
