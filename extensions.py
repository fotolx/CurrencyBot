import requests
import json
import telebot
from telebot import types
import bot_token
import re


class ConvertBot:
    def __init__(self, source='cryptocompare.com'):
        self.message = None
        self.source = source
        if self.source == 'MOEX':
            self.q = ConvertCurrencyMOEX()
            print(self.q.first_request['marketdata']['data'][0][8])
        else:
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
        self.markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
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
        msg = f"Приветствую, {message.chat.first_name}!\nСегодня один доллар $ США стоит {self.q.first_request['marketdata']['data'][0][8]} руб. ₽\n" \
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
        if self.source == 'MOEX':
            msg = msg+'\nПеревод осуществляется на основе курсов валют с Мосбиржи.'

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
    def __init__(self):
        self.first_request = json.loads(
            requests.get('https://min-api.cryptocompare.com/data/price?fsym=USD&tsyms=RUB').content)

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


class ConvertCurrencyMOEX(ConvertCurrency):
    def __init__(self):
        super().__init__()
        self.first_request = json.loads(
            requests.get(f'http://iss.moex.com/iss/engines/currency/markets/selt/securities.json?iss.only=securities,'
                         f'marketdata&securities=CETS:USD000000TOD&iss.meta=off').content)

    @staticmethod
    def get_price(base, quote, amount):
        inversed = None
        ticker1_inv = False
        ticker2_inv = False
        currency_tickers = {'USDRUB': 'USD000000TOD', 'USDJPY': 'USDJPY_TOD', 'USDCNY': 'USDCNY_TOD',
                            'JPYRUB': 'JPYRUB_TOD',
                            'CNYRUB': 'CNY000000TOD',
                            'EURUSD': 'EURUSD000TOD', 'EURRUB': 'EUR_RUB__TOD'
                            }
        inversed_tickers = {'USDEUR': 'EURUSD000TOD',
                            'RUBUSD': 'USD000000TOD', 'RUBJPY': 'JPYRUB_TOD', 'RUBCNY': 'CNY000000TOD',
                            'RUBEUR': 'EUR_RUB__TOD',
                            'JPYUSD': 'USDJPY_TOD', 'CNYUSD': 'USDCNY_TOD'}

        no_tickers = {'JPYCNY': '', 'JPYEUR': '',
                      'CNYJPY': '', 'CNYEUR': '',
                      'EURJPY': '', 'EURCNY': ''}
        if base + quote in currency_tickers:
            url = f'http://iss.moex.com/iss/engines/currency/markets/selt/securities.json?iss.only=securities,' \
                  f'marketdata&securities=CETS:{currency_tickers.get(base + quote)}&iss.meta=off '
        elif base + quote in inversed_tickers:
            inversed = True
            url = f'http://iss.moex.com/iss/engines/currency/markets/selt/securities.json?iss.only=securities,' \
                  f'marketdata&securities=CETS:{currency_tickers.get(quote + base)}&iss.meta=off '
        else:
            if base == 'EUR':
                ticker1 = currency_tickers.get('EURUSD')
                ticker1_inv = True
            else:
                ticker1 = currency_tickers.get("USD" + base)
            if quote == 'EUR':
                ticker2 = currency_tickers.get('EURUSD')
                ticker2_inv = True
            else:
                ticker2 = currency_tickers.get("USD" + quote)
            url1 = f'http://iss.moex.com/iss/engines/currency/markets/selt/securities.json?iss.only=securities,' \
                   f'marketdata&securities=CETS:{ticker1}&iss.meta=off '
            url2 = f'http://iss.moex.com/iss/engines/currency/markets/selt/securities.json?iss.only=securities,' \
                   f'marketdata&securities=CETS:{ticker2}&iss.meta=off '
            try:
                r1 = json.loads(requests.get(url1).content)
                r2 = json.loads(requests.get(url2).content)
            except Exception as e:
                print('Error')
                print(e)
                raise APIException()
            if ticker1_inv:
                return (r2['securities']['data'][0][15] / (1/r1['securities']['data'][0][15])) * amount
            if ticker2_inv:
                return ((1/r2['securities']['data'][0][15])/ r1['securities']['data'][0][15]) * amount
            else:
                return (r2['securities']['data'][0][15] / r1['securities']['data'][0][15]) * amount
                raise APIException()
        try:
            r = json.loads(requests.get(url).content)
        except Exception as e:
            print('Error')
            print(e)
            raise APIException()

        if inversed:
            return 1 / r['securities']['data'][0][15] * amount
        else:
            return r['securities']['data'][0][15] * amount
