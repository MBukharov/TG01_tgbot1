import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
import sqlite3
from config import TOKEN_TG
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import logging

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN_TG)
dp = Dispatcher(storage=MemoryStorage())

def init_db():
    conn = sqlite3.connect('school_data.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            grade INTEGER
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class Form(StatesGroup):
    name = State()
    age = State()
    grade = State()

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.reply("Привет! Пожалуйста, введите свое имя: ")
    await state.set_state(Form.name)

@dp.message(Form.name)
async def age(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.reply("Укажите свой возраст:")
    await state.set_state(Form.age)

@dp.message(Form.age)
async def grade(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.reply("Укажите свой класс:")
    await state.set_state(Form.grade)

@dp.message(Form.grade)
async def save(message: Message, state: FSMContext):
    data = await state.get_data()
    name = data.get('name')
    age = data.get('age')
    grade = message.text
    conn = sqlite3.connect('school_data.db')
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO students (name, age, grade)
        VALUES (?, ?, ?)
    ''', (name, age, grade))
    conn.commit()
    conn.close()

    await state.clear()

    await message.reply("Ваши данные сохранены!")

@dp.message(Command('show'))
async def show_students(message: Message):
    conn = sqlite3.connect('school_data.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM students')
    rows = cur.fetchall()
    conn.close()

    text = "Список студентов:\n"
    for row in rows:
        text += f"Имя: {row[1]}\nВозраст: {row[2]}\nКласс: {row[3]}\n\n"

    await message.reply(text)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())