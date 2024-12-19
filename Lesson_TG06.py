import asyncio
import random

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
import sqlite3
import requests

from urllib3 import request

from config import TOKEN_TG
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import logging

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN_TG)
dp = Dispatcher()

button_registr = KeyboardButton(text='Регистрация в телеграм боте')
button_exchange_rates = KeyboardButton(text="Курс валют")
button_tips = KeyboardButton(text="Советы по экономии")
button_finances = KeyboardButton(text="Личные финансы")

keyboards = ReplyKeyboardMarkup(keyboard=[
    [button_registr, button_exchange_rates],
    [button_tips, button_finances]
],resize_keyboard=True)

conn = sqlite3.connect('user.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE,
    name TEXT,
    category1 TEXT,
    category2 TEXT,
    category3 TEXT,
    expenses1 REAL,
    expenses2 REAL,
    expenses3 REAL
)''')
conn.commit()


class FinanceForm(StatesGroup):
    category1 = State()
    category2 = State()
    category3 = State()
    # expenses1 = State()
    # expenses2 = State()
    # expenses3 = State()

@dp.message(CommandStart())
async def start(message: Message):
    await message.reply("Привет! Я ваш личный финансовый помощник. Выберите одну из опций в меню:",
                        reply_markup=keyboards)

@dp.message(F.text == 'Регистрация в телеграм боте')
async def registration(message: Message):
    telegram_id = message.from_user.id
    name = message.from_user.full_name
    cursor.execute('''SELECT * FROM users WHERE telegram_id = ?''', (telegram_id,))
    user = cursor.fetchone()
    if user:
        await message.reply("Вы уже зарегистрированы в боте.")
    else:
        cursor.execute('''INSERT INTO users (telegram_id, name) VALUES (?, ?)''', (telegram_id, name))
        conn.commit()
        await message.reply("Вы зарегистрированы в боте.")

@dp.message(F.text == 'Курс валют')
async def exchange_rates(message: Message):
    url = "https://v6.exchangerate-api.com/v6/09edf8b2bb246e1f801cbfba/latest/USD"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            await message.answer('Не удалось получить данные')
            return
        data = response.json()
        usd_to_rub = data['conversion_rates']['RUB']
        eur_to_rub = usd_to_rub / data['conversion_rates']['EUR']
        await message.answer(f"1 USD - {usd_to_rub:.2f}  RUB\n"
                            f"1 EUR - {eur_to_rub:.2f}  RUB")
    except:
        await message.reply('Произошла ошибка')

@dp.message(F.text == "Советы по экономии")
async def send_tips(message: Message):
    tips = ['Ведите бюджет и следите за своими расходами',
            'Создайте фонд на чёрный день',
            'Сравнивайте цены и ищите скидки',
            'Откажитесь от импульсивных покупок',
            'Готовьте еду сами дома'
    ]
    tip = random.choice(tips)
    await message.answer(tip)

@dp.message(F.text == 'Личные финансы')
async def finances(message: Message, state: FSMContext):
    await state.set_state(FinanceForm.category1)
    await message.answer('Введите первую категорию расходов и сумму трат через запятую (Например: еда, 500)')
@dp.message(FinanceForm.category1)
async def finances(message: Message, state: FSMContext):
    try:
        category, amount = message.text.split(',')
        amount = float(amount.strip())
    except ValueError:
        await message.reply("Данные должны быть в формате 'Категория, Сумма'. Например: еда, 500. Повторите ввод.")
        return
    await state.update_data(category1 = [category.strip(),amount])
    await state.set_state(FinanceForm.category2)
    await message.answer('Введите вторую категорию расходов и сумму трат через запятую (Например: еда, 500)')

@dp.message(FinanceForm.category2)
async def finances(message: Message, state: FSMContext):
    try:
        category, amount = message.text.split(',')
        amount = float(amount.strip())
    except ValueError:
        await message.reply("Данные должны быть в формате 'Категория, Сумма'. Например: еда, 500. Повторите ввод.")
        return
    await state.update_data(category2 = [category.strip(),amount])
    await state.set_state(FinanceForm.category3)
    await message.answer('Введите третью категорию расходов и сумму трат через запятую (Например: еда, 500)')

@dp.message(FinanceForm.category3)
async def finances(message: Message, state: FSMContext):
    try:
        category, amount = message.text.split(',')
        amount = float(amount.strip())
    except ValueError:
        await message.reply("Данные должны быть в формате 'Категория, Сумма'. Например: еда, 500. Повторите ввод.")
        return
    await state.update_data(category3=[category.strip(), amount])

    data = await state.get_data()
    telegram_id = message.from_user.id
    cursor.execute('''UPDATE users SET category1 = ?, expenses1 = ?, category2 = ?, expenses2 = ?, category3 = ?, 
        expenses3 = ? WHERE telegram_id = ?''', (data['category1'][0],data['category1'][1],
                                                 data['category2'][0],data['category2'][1],
                                                 data['category3'][0],data['category3'][1], telegram_id))
    conn.commit()

    await state.clear()
    await message.answer("Категории и расходы сохранены!")

@dp.message(Command('show'))
async def show_base(message: Message):
    cursor.execute('''SELECT * FROM users''')
    data = cursor.fetchall()

    text = "Ваши категории и траты:\n"
    for row in data:
        text += (f"Категория 1: {row[3]} - Сумма трат: {row[6]} р.\n"
                 f"Категория 2: {row[4]} - Сумма трат: {row[7]} р.\n"
                 f"Категория 3: {row[5]} - Сумма трат: {row[8]} р.\n")

    await message.reply(text)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())