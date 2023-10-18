import json
from telegram.ext import Updater
from telegram.ext import CommandHandler

with open('./config/pass.json') as f:
    config = json.load(f)
token = config['DEFAULT']['TELEGRAM_TOKEN'] 

# updater 
updater = Updater(token='token', use_context=True)
dispatcher = updater.dispatcher


# command hander
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

# polling
updater.start_polling()