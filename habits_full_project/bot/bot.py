import os, time, threading, requests, logging
from dotenv import load_dotenv
import telebot

load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
BACKEND = os.getenv('BACKEND_URL','http://backend:8000')
if not TOKEN:
    raise RuntimeError('Provide TELEGRAM_BOT_TOKEN in env')

bot = telebot.TeleBot(TOKEN)
logging.basicConfig(level=logging.INFO)

def get_token_for_user(telegram_id):
    r = requests.post(f"{BACKEND}/auth/token", json={"telegram_id": str(telegram_id)})
    r.raise_for_status()
    return r.json()['access_token']

@bot.message_handler(commands=['start'])
def start(msg):
    token = get_token_for_user(msg.from_user.id)
    bot.reply_to(msg, "Привет! Твой токен выдан. Используй /add /list /complete /delete")


@bot.message_handler(commands=['add'])
def add(msg):
    try:
        payload = msg.text.split(' ',1)[1]
        title, time_str, days = payload.split(';')
    except Exception:
        bot.reply_to(msg, 'Использование: /add название;HH:MM;дни(0,1,..)')
        return
    token = get_token_for_user(msg.from_user.id)
    headers = {'Authorization': f'Bearer {token}'}
    j = {'title': title.strip(), 'time_of_day': time_str.strip(), 'days': [int(x) for x in days.split(',')] if days else None, 'is_active': True}
    r = requests.post(f"{BACKEND}/habits", json=j, headers=headers)
    if r.status_code>=400:
        bot.reply_to(msg, f"Ошибка: {r.json().get('detail')}")
    else:
        bot.reply_to(msg, f"Создано: {r.json()}")


@bot.message_handler(commands=['list'])
def lst(msg):
    token = get_token_for_user(msg.from_user.id)
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.get(f"{BACKEND}/habits", headers=headers)
    bot.reply_to(msg, str(r.json()))

@bot.message_handler(commands=['complete'])
def complete(msg):
    try:
        _, hid, status = msg.text.split()
        hid = int(hid)
    except Exception:
        bot.reply_to(msg, 'Использование: /complete <habit_id> <done|missed>')
        return
    token = get_token_for_user(msg.from_user.id)
    headers = {'Authorization': f'Bearer {token}'}
    j = {'habit_id': hid, 'status': status}
    r = requests.post(f"{BACKEND}/habits/{hid}/complete", json=j, headers=headers)
    bot.reply_to(msg, str(r.json()))

def due_poller():
    while True:
        try:
            r = requests.post(f"{BACKEND}/due")
            if r.status_code==200:
                items = r.json().get('items', [])
                for it in items:
                    chat = it['telegram_id']
                    text = it['text']
                    try:
                        bot.send_message(chat, text)
                    except Exception as e:
                        logging.warning('send error %s', e)
        except Exception as e:
            logging.warning('due poller error: %s', e)
        time.sleep(60)

t = threading.Thread(target=due_poller, daemon=True)
t.start()

bot.infinity_polling()
