#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, BaseFilter
import logging
import importlib
from os.path import expanduser

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Help text for dialog system 
helptext  = "'so what?' - available commands\n\n"
helptext += "'hey dude' - say hi to your Pi\n\n"
helptext += "'how are you?' - ask Pi for his mood\n\n"
helptext += "'thanks man' - thank Pi for his effort\n\n"
helptext += "'awake?' - ask Pi for his uptime\n\n"
helptext += "'show me' - get single image\n\n"
helptext += "'move it' - get video\n\n"
helptext += "'attack!' - activate sound cannon\n\n"
helptext += "'stop attack' - stop sound cannon\n\n"
helptext += "'reboot dude' - make Pi reboot\n\n"
helptext += "'go to sleep' - make Pi shut down\n\n"


plugins = {}

class LimitToUser(BaseFilter):
    def __init__(self, authorized_users):
        self.authorized_users = authorized_users
    def filter(self, message):
        return message.from_user.id in self.authorized_users

def start(bot, update):
    logger.info('Start "%s" \n' % update.message)
    update.message.reply_text('Hi!')

def handlemessage(bot, update):
    logger.info('Received "%s"\n' % update.message)

    for k, v in plugins.items():
        if v.handlemessage(bot, update.message):
            print("Message handled by %s" % k)
            return

    if update.message.text.lower() == 'hey dude':
        update.message.reply_text("Wassup?")
    elif update.message.text.lower() == 'so what?':
        update.message.reply_text(helptext)
    elif update.message.text.lower() == 'how are you?':
        update.message.reply_text("Kinda bored, man!")
    elif update.message.text.lower() == 'thanks man':
        update.message.reply_text("You got it!")
    else:
        update.message.reply_text("What ya sayin', dog?")

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))

def main():
    home = expanduser("~")
    try:
        config = json.load(open('%s/.minion_bot.json' % home))
    except FileNotFoundError:
        print('move minion_bot.json to home directory ~/.minion_bot.json')
        sys.exit(-1)

    limit_to_user = LimitToUser(config['telegram']['users'])

    updater = Updater(token=config['telegram']['token'])
    dp = updater.dispatcher

    global plugins
    for k,v in config.items():
        if k == "telegram":
            {}
        elif v["enable"]:
            print('load plugin %s' % k)
            try:
                loadedplugin = importlib.__import__("plugins.%s" % k, fromlist=[k]).__export__
                plugins[k] = loadedplugin(v)
            except (AttributeError, NameError):
                print("Couldn't load plugin %s" % k)

    print('Done')

    dp.add_handler(CommandHandler("start", start, limit_to_user))
    dp.add_handler(MessageHandler(Filters.text & limit_to_user, handlemessage))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
