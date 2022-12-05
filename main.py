import extensions as ext


global convert_bot

try:
    convert_bot = ext.ConvertBot()
except ext.APIException as e:
    print('APIException raised')
    print(e)
    convert_bot.send_error_message()
