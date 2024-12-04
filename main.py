import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from config import TOKEN_TG, TOKEN_weather
import requests
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

bot = Bot(token=TOKEN_TG)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer('Привет! Я помогу тебе узнать тебе погоду в любом городе.')

@dp.message(Command='help')
async def help(message):
    await message.answer('Доступные команды: \n /start - приветствие \n /help - перечень команд \n '
                         '/city - ввести город, чтобы узнать погоду')

class WeatherStates(StatesGroup):
    waiting_for_city = State()

@dp.message(commands='city')
async def city(message: Message):
    await message.reply("Введите название города:")
    await WeatherStates.waiting_for_city.set()

@dp.message(state=WeatherStates.waiting_for_city)
async def process_city(message: types.Message, state: FSMContext):
    city_name = message.text
    weather_data = get_weather(city_name)





async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())