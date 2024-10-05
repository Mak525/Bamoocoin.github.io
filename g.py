import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LoginUrl, WebAppInfo
from aiogram.utils import executor
import sqlite3

API_TOKEN = "7326939938:AAEVXnDEb48kgPR93GPKJuTcN14Kee-HZ1k"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Initialize database
conn = sqlite3.connect('users.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             user_id INTEGER UNIQUE,
             username TEXT)''')

conn.commit()
conn.close()

def user_exists(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def register_user(user_id, username):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()

@dp.message_handler(commands=['start'])
async def start(massage: types.Message):
    markup = types.ReplyKeyboardMarkup()
    markup.add(types.KeyboardButton("Play", web_app=WebAppInfo(url='https://b0c7-93-127-54-145.ngrok-free.app/')))
    await massage.answer("Добро пожаловать в Drill Simulator! 👋\n\n" 
               "Готовься отправиться в захватывающее путешествие, " 
               "где глубины земли скрывают неисчислимые сокровища, " 
               "ожидающие, когда их обнаружат твои навыки бурения.👷", reply_markup=markup)

@dp.callback_query_handler(lambda call: call.data == "play")
async def play_game(call: types.CallbackQuery):
    await call.message.answer("Игра началась!")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)