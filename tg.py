import asyncio
import sqlite3
import uuid
from aiogram import Bot, Dispatcher, types
from aiogram.types import WebAppInfo
from aiogram.utils import executor
import requests
from utils import generate_referral_link


API_TOKEN = "7326939938:AAEVXnDEb48kgPR93GPKJuTcN14Kee-HZ1k"


FLASK_SERVER_URL = "https://396e-93-127-54-145.ngrok-free.app"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Initialize database
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            username TEXT,
            referral_code TEXT UNIQUE,
            referred_by INTEGER,
            FOREIGN KEY (referred_by) REFERENCES users (user_id)
        )
    ''')
    conn.commit()
    conn.close()

def user_exists(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = c.fetchone()
    conn.close()
    return user

def get_user_by_referral_code(referral_code):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE referral_code=?", (referral_code,))
    user = c.fetchone()
    conn.close()
    return user

def get_referral_code(user_id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT referral_code FROM users WHERE user_id=?", (user_id,))
    referral_code = c.fetchone()
    conn.close()
    return referral_code[0] if referral_code else None

def register_user(user_id, username, referral_code=None):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Generate referral code for new user
    new_referral_code = str(uuid.uuid4())

    if referral_code:
        # Find the referrer by referral code
        referrer = get_user_by_referral_code(referral_code)
        if referrer:
            referrer_id = referrer[0]
            # Record referral
            # Award bonus to referrer (implement your logic here)
            print(f"Awarding bonus to user {referrer_id}")
        else:
            referrer_id = None
    else:
        referrer_id = None

    c.execute("INSERT INTO users (user_id, username, referral_code, referred_by) VALUES (?, ?, ?, ?)",
              (user_id, username, new_referral_code, referrer_id))

    conn.commit()
    conn.close()

    return new_referral_code

def get_all_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT user_id, username FROM users")
    users = c.fetchall()
    conn.close()
    return users

@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    user_id = message.from_user.id
    referral_code = None

    if '?start=' in message.text:
        referral_code = message.text.split('start=')[1]
        # Отправляем запрос на Flask-сервер для обновления кликов
        response = requests.get(f"{FLASK_SERVER_URL}/apply_referral?start12")
        if response.status_code == 200:
            result = response.json()
            if result['status'] == 'success':
                await message.answer(f"Ваша реферальная ссылка использована. Вы получили 500 поинтов!")
            else:
                await message.answer("Не удалось обработать реферальную ссылку.")
        else:
            await message.answer("Не удалось обработать реферальную ссылку.")

    else:
        await message.answer(f"С возвращением, {message.from_user.username}! Рады видеть вас снова!")

    photo = open('static/photo_2024-07-15_11-04-55-removebg-preview (2).png', 'rb')
    await bot.send_photo(message.chat.id, photo)

    markup = types.ReplyKeyboardMarkup()
    markup.add(types.KeyboardButton("Играть", web_app=WebAppInfo(url='https://3a66-93-127-54-145.ngrok-free.app')))

    await message.answer("Добро пожаловать в Bamboo Simulator! 🎋\n\n"
                         "Присоединяйтесь к нашей захватывающей игре кликер, где вы зарабатываете Bamboo Coins! "
                         "Bamboo Coins можно использовать для покупки различных товаров и даже обменять на криптовалюту. "
                         "Начните игру прямо сейчас, нажав на кнопку ниже.", reply_markup=markup)

@dp.message_handler(commands=['get_referral_link'])
async def get_referral_link(message: types.Message):
    referral_link = generate_referral_link()
    if referral_link:
        await message.answer(f"Ваша реферальная ссылка:   https://396e-93-127-54-145.ngrok-free.app/apply_referral?start=12")
    else:
        await message.answer("Не удалось получить реферальную ссылку.")


@dp.message_handler(commands=['chat_id'])
async def chat_id_message(message: types.Message):
    users = get_all_users()
    if users:
        response = "Список пользователей:\n"
        for user_id, username in users:
            response += f"User ID: {user_id}, Username: @{username if username else 'Неизвестно'}\n"
    else:
        response = "В базе данных нет зарегистрированных пользователей."

    await message.answer(response)

@dp.callback_query_handler(lambda call: call.data == "play")
async def play_game(call: types.CallbackQuery):
    await call.message.answer("Игра началась!")

if __name__ == '__main__':
    init_db()
    executor.start_polling(dp, skip_updates=True)