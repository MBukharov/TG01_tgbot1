import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile

from config import TOKEN_TG
from gtts import gTTS
from googletrans import Translator
import os

bot = Bot(token=TOKEN_TG)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(f'Привет, {message.from_user.first_name}! Я сохраню любое фото, которое ты мне отправишь, '
                         f'а также переведу на английский твое сообщение мне.')


@dp.message(Command('help'))
async def help(message):
    await message.answer('Отправь мне фото и на его сохраню. Или отправь мне сообщение и я его переведу на английский язык')

@dp.message(F.photo)
async def photo(message: Message):
    await message.reply("Норм фотка. Давай-ка, я ее сохраню.")
    await bot.download(message.photo[-1], f'img/{message.photo[-1].file_id}.jpg')

@dp.message()
async def translate(message: Message):
    translator = Translator()
    translated_text = translator.translate(message.text, dest="en").text
    await message.reply(translated_text)

    #озвучка переведенного сообщения
    voice = gTTS(text=translated_text, lang='en')
    voice.save('tmp/voice.ogg')
    audio = FSInputFile('tmp/voice.ogg')
    await bot.send_voice(message.chat.id, audio)
    os.remove('tmp/voice.ogg')

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
