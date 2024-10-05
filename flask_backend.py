import sqlite3
from flask import Flask, render_template, request, redirect, url_for, jsonify
import re
import uuid
from utils import generate_referral_link


app = Flask(__name__)

def init_db():
    # Инициализация базы данных для кошельков
    conn = sqlite3.connect('wallets.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS wallets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wallet_address TEXT UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

    # Инициализация базы данных для кликов
    conn = sqlite3.connect('user_clicks.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            click_count INTEGER
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/generate_link', methods=['GET'])
def generate_link():
    try:
        link = generate_referral_link()
        return jsonify({'link': link}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred while generating link'}), 500


@app.route('/apply_referral', methods=['GET'])
def apply_referral():
    try:
        referral_code = request.args.get('start')
        if not referral_code:
            return jsonify({'error': 'Referral code is required'}), 400

        conn = sqlite3.connect('user_clicks.db')
        c = conn.cursor()

        # Обновление количества кликов для всех пользователей
        c.execute("UPDATE clicks SET click_count = click_count + 500")
        conn.commit()
        conn.close()

        return jsonify({'status': 'success', 'message': '500 points added to all users'}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred while applying referral'}), 500

@app.route('/links')
def links():
    return render_template('links.html')

def is_valid_wallet_address(address):
    # Проверка для Ethereum адреса: 0x + 40 hex символов
    return re.match(r'^0x[a-fA-F0-9]{40}$', address) is not None

@app.route('/connect_wallet', methods=['POST'])
def connect_wallet():
    try:
        wallet_address = request.form.get('wallet_address')  # Используем form для получения данных

        if not wallet_address:
            return jsonify({'error': 'Wallet address is required'}), 400

        if not is_valid_wallet_address(wallet_address):
            return jsonify({'error': 'Invalid wallet address'}), 400

        conn = sqlite3.connect('wallets.db')
        c = conn.cursor()

        # Проверка на существование
        c.execute("SELECT * FROM wallets WHERE wallet_address = ?", (wallet_address,))
        if c.fetchone():
            conn.close()
            return redirect(url_for('success'))

        # Вставка нового адреса
        c.execute("INSERT INTO wallets (wallet_address) VALUES (?)", (wallet_address,))
        conn.commit()
        conn.close()

        return redirect(url_for('success'))

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred while connecting wallet'}), 500

@app.route('/connect_wallet_page')
def connect_wallet_page():
    wallet_address = request.args.get('wallet_address')
    if wallet_address:
        conn = sqlite3.connect('wallets.db')
        c = conn.cursor()
        c.execute("SELECT * FROM wallets WHERE wallet_address = ?", (wallet_address,))
        if c.fetchone():
            conn.close()
            return redirect(url_for('success'))
        conn.close()
    return render_template('connect_wallet.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/frens')
def frens():
    return render_template('frens.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/update_clicks', methods=['POST'])
def update_clicks():
    try:
        count = request.json.get('click_count', 0)

        conn = sqlite3.connect('user_clicks.db')
        c = conn.cursor()

        # Обновление количества кликов
        c.execute('INSERT OR REPLACE INTO clicks (id, click_count) VALUES (1, ?)', (count,))
        conn.commit()
        conn.close()

        return jsonify({'status': 'success'}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred while updating clicks'}), 500



@app.route('/get_clicks', methods=['GET'])
def get_clicks():
    try:
        conn = sqlite3.connect('user_clicks.db')
        c = conn.cursor()

        c.execute('SELECT click_count FROM clicks WHERE id = 1')
        row = c.fetchone()
        conn.close()

        click_count = row[0] if row else 0
        return jsonify({'click_count': click_count}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred while fetching clicks'}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True)