import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, LoginUrl
import sqlite3

bot = telebot.TeleBot("7326939938:AAEVXnDEb48kgPR93GPKJuTcN14Kee-HZ1k")

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

@bot.message_handler(commands=['start'])
def start_message(message):
    user_id = message.from_user.id
    username = message.from_user.username

    if user_exists(user_id):
        bot.send_message(message.chat.id, f"С возвращением, {username}! Рады видеть вас снова в Bamboo Simulator! 🎋")
    else:
        register_user(user_id, username)
        bot.send_message(message.chat.id, f"Добро пожаловать, {username}! Вы успешно зарегистрировались в Bamboo Simulator! 🎋")

    photo = open('static/photo_2024-07-15_11-04-55-removebg-preview (2).png', 'rb')
    bot.send_photo(message.chat.id, photo)

    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    login_url = LoginUrl(url="https://lemonbit.online/", bot_username="Bamboo_token_bot", request_write_access=True)
    markup.add(InlineKeyboardButton("Играть", login_url=login_url))

    bot.send_message(message.chat.id, "Добро пожаловать в Bamboo Simulator! 🎋\n\n"
                                      "Присоединяйтесь к нашей захватывающей игре кликер, где вы зарабатываете Bamboo Coins! "
                                      "Bamboo Coins можно использовать для покупки различных товаров и даже обменять на криптовалюту. "
                                      "Начните игру прямо сейчас, нажав на кнопку ниже.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "play")
def play_game(call):
    bot.send_message(call.message.chat.id, "Игра началась!")

if __name__ == '__main__':
    bot.polling()