import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from config import TOKEN_TG

bot = Bot(token=TOKEN_TG)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer('Привет! Я помогу тебе узнать тебе погоду в любом городе.')







async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())