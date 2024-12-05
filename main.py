import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from config import TOKEN_TG, TOKEN_weather
import requests

import logging
import aiohttp
from aiogram.enums import ParseMode

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from gtts import gTTS   #озвучка текста
import os

bot = Bot(token=TOKEN_TG)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Configure logging
logging.basicConfig(level=logging.INFO)

class WeatherStates(StatesGroup):
    waiting_for_city = State()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(f'Привет, {message.from_user.first_name}! Я помогу тебе узнать погоду в любом городе.')

@dp.message(Command('help'))
async def help(message):
    await message.answer('Доступные команды: \n /start - приветствие \n /help - перечень команд \n '
                         '/city - ввести город, чтобы узнать погоду')


@dp.message(Command('city'))
async def cmd_city(message: Message, state: FSMContext):
    await message.reply("Пожалуйста, введите название города:")
    await state.set_state(WeatherStates.waiting_for_city)

@dp.message(WeatherStates.waiting_for_city)
async def get_weather(message: Message, state: FSMContext):
    city_name = message.text.strip()
    weather_data = await fetch_weather(city_name)

    if weather_data:
        weather_description = weather_data['weather'][0]['description']
        temperature = weather_data['main']['temp']
        response = (
            f"Погода в городе {city_name}:\n"
            f"{weather_description}\n"
            f"Температура: {int(temperature)}°C"
        )
    else:
        response = "Не удалось получить данные о погоде. Пожалуйста, проверьте название города."

    await message.reply(response, parse_mode=ParseMode.HTML)

    #Озвучка сообщения
    voice = gTTS(text=response, lang='ru')
    voice.save('tmp/voice.ogg')
    audio = FSInputFile('tmp/voice.ogg')
    await bot.send_voice(message.chat.id, audio)
    os.remove('tmp/voice.ogg')

    picture = { 'ясно': 'https://vecherka74.ru/uploads/posts/2017-03/medium/1489747844_sun.jpg',
                'дождь': 'https://sp-lyamina.ru/media/project_mo_116/f9/b5/f7/77/0e/17/dozhd.jpg',
                'небольшой дождь':'https://sp-lyamina.ru/media/project_mo_116/f9/b5/f7/77/0e/17/dozhd.jpg',
                'пасмурно': 'https://thumbs.dreamstime.com/b/%D0%BD%D0%B5%D0%B1%D0%BE-%D1%81%D0%BE%D0%BB%D0%BD%D0%B5%D1%87%D0%BD%D0%BE-%D0%B8-%D0%BF%D0%B0%D1%81%D0%BC%D1%83%D1%80%D0%BD%D0%BE-%D1%81%D0%BE%D0%BB%D0%BD%D0%B5%D1%87%D0%BD%D1%8B%D0%B5-%D0%BF%D0%B0%D1%81%D0%BC%D1%83%D1%80%D0%BD%D1%8B%D0%B5-%D0%B8%D0%B7%D0%BE%D0%B1%D1%80%D0%B0%D0%B6%D0%B5%D0%BD%D0%B8%D1%8F-%D0%B4%D0%BB%D1%8F-181133795.jpg',
                'облачно с прояснениями':'https://cher.all-rf.com/static/news/i/cbd5155d-c921-4880-9344-8d553eeec38b.jpg',
                'переменная облачность': 'https://s0.rbk.ru/v6_top_pics/media/img/7/01/756342821324017.jpg',
                'небольшая облачность': 'https://s0.rbk.ru/v6_top_pics/media/img/7/01/756342821324017.jpg',
                'небольшой снегопад':'https://s0.bloknot-morozovsk.ru/thumb/850x0xcut/upload/iblock/81b/ct454393hrhknfs5nn9fcwe7tphh3yrg/1920x1200_1540698_www.ArtFile.ru_.jpg',
                'небольшой снег':'https://s0.bloknot-morozovsk.ru/thumb/850x0xcut/upload/iblock/81b/ct454393hrhknfs5nn9fcwe7tphh3yrg/1920x1200_1540698_www.ArtFile.ru_.jpg',}
    if weather_description in picture:
        url = picture[weather_description]
        await bot.send_photo(message.chat.id, url)
    await state.clear()

async def fetch_weather(city_name: str):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city_name,
        'appid': TOKEN_weather,
        'units': 'metric',
        'lang': 'ru'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(base_url, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                logging.error(f"Error fetching weather data: {response.status}")
                return None

@dp.message(F.photo)
async def photo(message: Message):
    await message.reply("Норм фотка. Давай, я ее сохраню.")
    await bot.download(message.photo[-1], f'tmp/{message.photo[-1].file_id}.jpg')


@dp.message(Command('photo', prefix='&'))
async def photo(message: Message):
    await message.reply("Если хочешь отправить мне фотку, отправь ее в чат.")

@dp.message(Command('video'))
async def video(message: Message):
    await bot.send_chat_action(message.chat.id, 'upload_video')
    video = FSInputFile('tmp/video.mp4')
    await bot.send_video(message.chat.id, video)


@dp.message()
async def unknown(message: Message):
    await message.answer("Если Вы хотите узнать погоду, выберите команду /city")



async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())