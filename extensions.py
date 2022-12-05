import requests
import json
import telebot
from telebot import types
import bot_token
import re


class ConvertBot:

    def __init__(self):
        self.message = None
        self.q = ConvertCurrency()

        self.bot = telebot.TeleBot(bot_token.TOKEN)

        self.currencies = {"рублей": "RUB", "рубль": "RUB", "рублях": "RUB", "рубли": "RUB", "рубля": "RUB",
                           "доллар": "USD", "долларах": "USD", "долларов": "USD", "доллары": "USD",
                           "евро": "EUR", "евров": "EUR",
                           "йена": "JPY", "иена": "JPY", "иен": "JPY", "иены": "JPY", "иенах": "JPY",
                           "йен": "JPY", "йены": "JPY", "йенах": "JPY",
                           "юань": "CNY", "юаней": "CNY", "юанях": "CNY", "юанем": "CNY", "юаням": "CNY", "юани": "CNY"
                           }
        self.filter_words = ["в", "за", "на", ""]
        self.markup = types.ReplyKeyboardMarkup(row_width=2)
        self.itembtn1 = types.KeyboardButton('/start')
        self.itembtn2 = types.KeyboardButton('/values')
        self.markup.add(self.itembtn1, self.itembtn2)

        self.bot.register_message_handler(self.handle_start_help, commands=['start', 'help'])
        self.bot.register_message_handler(self.handle_values_help, commands=['values'])
        self.bot.register_message_handler(self.handle_calc, content_types=['text'])
        self.bot.register_message_handler(self.handle_docs_image, content_types=['document', 'image', 'sticker'])
        self.bot.infinity_polling()
        pass

    def handle_start_help(self, message):
        r = requests.get('https://min-api.cryptocompare.com/data/price?fsym=USD&tsyms=JPY,EUR,RUB')
        r = json.loads(r.content)

        msg = f"Приветствую, {message.chat.first_name}!\nСегодня один доллар $ США стоит {r['RUB']} руб. ₽\n" \
              f"Отправь мне сообщение вида\n" \
              f"<имя валюты цену которой хочешь узнать> <имя валюты в которой надо узнать цену первой валюты> <количество " \
              f"первой валюты>\n" \
              f"Йена юань 150\n" \
              f"или\n" \
              f"300 долларов в рублях\n" \
              f"И я пришлю тебе ответ, сколько стоит валюта.\n" \
              f"Мои команды:\n" \
              f"/start - приветствие\n" \
              f"/help - справка\n" \
              f"/values - список поддерживаемых валют"

        markup = types.ReplyKeyboardMarkup(row_width=2)
        itembtn1 = types.KeyboardButton('/start')
        itembtn2 = types.KeyboardButton('/values')
        markup.add(itembtn1, itembtn2)

        self.bot.send_message(message.chat.id, msg, reply_markup=self.markup)
        self.message = message
        pass

    def handle_values_help(self, message):
        msg = f"Я могу перевести следующие валюты между собой:\n" \
              f"Рубль, доллар, евро, йена, юань."

        self.bot.send_message(message.chat.id, msg, reply_markup=self.markup)
        self.message = message
        pass

    def handle_calc(self, message):
        msg_split = re.split("[.:;, ]", str(message.text))
        msg_split = list(filter(lambda s: s not in self.filter_words, msg_split))
        amount = None
        convert = []
        for entry in msg_split:
            try:
                amount = float(entry)
            except ValueError:
                convert.append(entry)
                continue
        if amount is None:
            self.bot.send_message(message.chat.id, 'Не указано количество валюты')
            return
        else:
            print(amount)
        if len(convert) != 2:
            self.bot.send_message(message.chat.id, 'Не распознана валюта')
            self.handle_values_help(message)
            raise APIException
        if convert[0].lower() not in self.currencies or convert[1].lower() not in self.currencies:
            self.bot.send_message(message.chat.id, 'Не распознана валюта')
            self.handle_values_help(message)
            raise APIException
        if self.currencies.get(convert[0].lower()) == self.currencies.get(convert[1].lower()):
            self.bot.send_message(message.chat.id, 'Укажите разные валюты')
            self.handle_values_help(message)
            raise APIException
        price = round(self.q.get_price(self.currencies.get(convert[0].lower()),
                                       self.currencies.get(convert[1].lower()), amount), 2)
        self.bot.send_message(message.chat.id, f"{amount} {convert[0].lower()} в {convert[1].lower()} равно {price}",
                              reply_markup=self.markup)
        self.message = message
        pass

    # Обрабатываются все изображения, аудиозаписи и стикеры
    def handle_docs_image(self, message):
        self.bot.send_message(message.chat.id, 'Прикольно )))', reply_markup=self.markup)
        pass

    def send_error_message(self):
        self.bot.send_message(self.message.chat.id, 'Возникла проблема )))', reply_markup=self.markup)
        pass


class ConvertCurrency:
    def __int__(self):
        self.r = requests.get('https://min-api.cryptocompare.com/data/price?fsym=USD&tsyms=JPY,EUR,RUB')
        self.r = json.loads(self.r.content)
        return self.r
        pass

    @staticmethod
    def get_price(base, quote, amount):
        url = f'https://min-api.cryptocompare.com/data/price?fsym={base}&tsyms={quote}'

        r = requests.get(url)
        r = json.loads(r.content)
        if r.get('Response') == 'Error':
            print(r.get('Message'))
            raise APIException()
        return r.get(quote) * amount
        pass


class APIException(Exception):
    pass
