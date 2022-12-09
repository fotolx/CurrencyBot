import extensions as ext


global convert_bot

try:
    # If you specify parameter source='MOEX' then quotes will be taken from MOEX exchange.
    # If none specified, quotes taken from cryptocompare.com
    convert_bot = ext.ConvertBot(source='MOEX')

except ext.APIException as e:
    print('APIException raised')
    print(e)
    convert_bot.send_error_message()
