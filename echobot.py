import logging
import telegram
from telegram.error import NetworkError, Unauthorized
from time import sleep


update_id = None


def main():
    """Run the bot."""
    global update_id

    bot = telegram.Bot('1004568616:AAED-QoeDoFZQy_c5rEW2COcoQPzoBgxff4')


    try:
        update_id = bot.get_updates()[0].update_id
    except IndexError:
        update_id = None

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    while True:
        try:
            echo(bot)
        except NetworkError:
            sleep(1)
        except Unauthorized:

            update_id += 1


def echo(bot):
    """Echo the message the user sent."""
    global update_id

    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1

        if update.message:
            update.message.reply_text(update.message.text)


if __name__ == '__main__':
    main()