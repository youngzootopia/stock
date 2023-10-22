import json
import telepot 

class TeleBot():
    def __init__(self):
        super().__init__()
        with open('./config/pass.json') as f:
            self.config = json.load(f)

        self.token = self.config['DEFAULT']['TELEGRAM_TOKEN'] 
        self.user_id = self.config['DEFAULT']['TELEGRAM_ID'] 

        self.bot = telepot.Bot(self.token)

    def report_message(self, data):
        self.bot.sendMessage(chat_id=self.user_id, text=str(data))

