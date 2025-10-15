import os
import json
import time
import requests
import websocket

# Print a startup message so you can see it in Render logs
print("🚀 Starting bot... connected to Render ✅")

# Environment variables (set in Render dashboard)
DERIV_API_TOKEN = os.getenv("DERIV_API_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# --- Safety check ---
if not DERIV_API_TOKEN or not TELEGRAM_BOT_TOKEN or not CHAT_ID:
    print("❌ Missing one or more environment variables.")
    print("Please set DERIV_API_TOKEN, TELEGRAM_BOT_TOKEN, and CHAT_ID in Render.")
    time.sleep(60)
    exit()

# --- Deriv WebSocket setup ---
DERIV_APP_ID = "1089"  # Public test App ID, replace if you have your own
DERIV_URL = f"wss://ws.derivws.com/websockets/v3?app_id={DERIV_APP_ID}"

def send_telegram_message(message):
    """Send message to your Telegram chat."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"⚠️ Telegram error: {e}")

def on_message(ws, message):
    """When a message is received from Deriv."""
    data = json.loads(message)
    if "tick" in data:
        symbol = data["tick"]["symbol"]
        price = data["tick"]["quote"]
        print(f"💹 {symbol}: {price}")
        send_telegram_message(f"💹 {symbol}: {price}")

def on_error(ws, error):
    print(f"⚠️ WebSocket error: {error}")
    send_telegram_message(f"⚠️ WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("❌ Connection closed, reconnecting in 5s...")
    time.sleep(5)
    start_socket()

def on_open(ws):
    """Subscribe to a symbol."""
    print("✅ Connected to Deriv WebSocket.")
    tick_data = {"ticks": "R_100"}  # You can change to other symbols like 'R_75', 'R_50', etc.
    ws.send(json.dumps(tick_data))

def start_socket():
    """Start and maintain the Deriv WebSocket connection."""
    while True:
        try:
            ws = websocket.WebSocketApp(
                DERIV_URL,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            ws.on_open = on_open
            ws.run_forever()
        except Exception as e:
            print(f"⚠️ Error: {e}. Reconnecting...")
            time.sleep(5)

# --- Start the bot ---
if __name__ == "__main__":
    start_socket()