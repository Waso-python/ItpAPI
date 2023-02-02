import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from bot_utils import get_product_by_text, get_product_from_db

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token="")
# Диспетчер
dp = Dispatcher(bot)

# Хэндлер на команду /start
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Привет!\nНапиши мне что-нибудь!")

@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("Напиши мне что-нибудь, и я отпрпавлю этот текст тебе в ответ!")

@dp.message_handler()
async def echo_message(msg: types.Message):
    res_dict = get_product_from_db(msg.text) 
    if len(res_dict) <= 15:
        for el in res_dict:
            res_string = str(el[7]) + '\n' + el[2] + '\n' + el[1] + '\n' + str(el[3]) + '\n' + str(el[4]) if el else 'NOT FOUND'
            await bot.send_message(msg.from_user.id, res_string)
            i = 0
            if el[5]:
                urls = el[5].split(', ')
                for url in urls:
                    if i < 2:
                        await bot.send_photo(msg.from_user.id, photo='https://b2b.i-t-p.pro/'+url+'?size=original')
                        i+=1
    else:
        res_string = 'Too mach result - {}'.format(len(res_dict))
        await bot.send_message(msg.from_user.id, res_string)

# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())