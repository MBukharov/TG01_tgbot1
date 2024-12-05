import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from config import TOKEN_TG, TOKEN_weather
import requests

import logging
import aiohttp
from aiogram.enums import ParseMode

bot = Bot(token=TOKEN_TG)
dp = Dispatcher()

# Configure logging
logging.basicConfig(level=logging.INFO)

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer('Привет! Я помогу тебе узнать тебе погоду в любом городе.')

@dp.message(Command('help'))
async def help(message):
    await message.answer('Доступные команды: \n /start - приветствие \n /help - перечень команд \n '
                         '/city - ввести город, чтобы узнать погоду')


@dp.message(Command('city'))
async def cmd_city(message: Message):
    await message.reply("Пожалуйста, введите название города:")

@dp.message(lambda message: message.text)
async def get_weather(message: Message):
    city_name = message.text.strip()
    weather_data = await fetch_weather(city_name)

    if weather_data:
        weather_description = weather_data['weather'][0]['description']
        temperature = weather_data['main']['temp']
        response = (
            f"Погода в городе {city_name}:\n"
            f"Описание: {weather_description}\n"
            f"Температура: {temperature}°C"
        )
    else:
        response = "Не удалось получить данные о погоде. Пожалуйста, проверьте название города."

    await message.reply(response, parse_mode=ParseMode.HTML)

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

# def get_weather(city_name):
#     url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={TOKEN_weather}"
#     response = requests.get(url)
#     data = response.json()
#     return data



async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())