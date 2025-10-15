import requests
import time
import websocket
import json

# --- SETTINGS ---
DERIV_APP_ID = '1089'  # Default app ID for testing
DERIV_API_TOKEN = 'YOUR_DERIV_API_TOKEN'
TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
CHAT_ID = 'YOUR_CHAT_ID'

SYMBOL = 'R_25'  # Volatility 25 Index
ALERT_LEVEL = 2575.842
CHECK_INTERVAL = 10  # seconds

def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {'chat_id': CHAT_ID, 'text': message}
    requests.post(url, data=payload)

def get_deriv_price():
    ws = websocket.create_connection(f"wss://ws.derivws.com/websockets/v3?app_id={DERIV_APP_ID}")
    ws.send(json.dumps({"ticks_history": SYMBOL, "end": "latest", "count": 1, "style": "ticks"}))
    data = json.loads(ws.recv())
    ws.close()
    return float(data['history']['prices'][0])

last_alert = None
while True:
    try:
        price = get_deriv_price()
        print(f"Current price: {price}")
        if price < ALERT_LEVEL and last_alert != "below":
            send_telegram_message(f"🔔 Volatility 25 Index\nR_25 has crossed below {ALERT_LEVEL}")
            last_alert = "below"
        elif price > ALERT_LEVEL and last_alert != "above":
            send_telegram_message(f"🔔 Volatility 25 Index\nR_25 has crossed above {ALERT_LEVEL}")
            last_alert = "above"
    except Exception as e:
        print("Error:", e)
    time.sleep(CHECK_INTERVAL)