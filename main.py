import os
import json
import time
import requests
import websocket

print("🚀 Starting multi-pair Deriv → Telegram bot ✅")

# Environment variables (set in Render dashboard)
DERIV_API_TOKEN = os.getenv("DERIV_API_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not DERIV_API_TOKEN or not TELEGRAM_BOT_TOKEN or not CHAT_ID:
    print("❌ Missing one or more environment variables.")
    time.sleep(60)
    exit()

# 🧠 Add your pairs here (synthetic, forex, or crypto)
SYMBOLS = ["R_10", "R_25", "R_50", "1HZ10V", "1HZ75V", "1HZ100V", "JD10", "JD50", "JD100"]

DERIV_APP_ID = "1089"  # Use your own if you have one
DERIV_URL = f"wss://ws.derivws.com/websockets/v3?app_id={DERIV_APP_ID}"

def send_telegram_message(message):
    """Send message to Telegram chat."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": message})
    except Exception as e:
        print(f"⚠️ Telegram error: {e}")

def on_message(ws, message):
    """Handle incoming ticks."""
    data = json.loads(message)
    if "tick" in data:
        symbol = data["tick"]["symbol"]
        price = data["tick"]["quote"]
        msg = f"💹 {symbol}: {price}"
        print(msg)
        send_telegram_message(msg)

def on_error(ws, error):
    print(f"⚠️ WebSocket error: {error}")
    send_telegram_message(f"⚠️ WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("❌ Connection closed — reconnecting in 5s...")
    time.sleep(5)
    start_socket()

def on_open(ws):
    """Subscribe to all symbols."""
    print("✅ Connected to Deriv WebSocket.")
    for sym in SYMBOLS:
        ws.send(json.dumps({"ticks": sym}))
        print(f"📡 Subscribed to {sym}")
    send_telegram_message(f"✅ Bot connected.\nTracking: {', '.join(SYMBOLS)}")

def start_socket():
    """Start WebSocket connection and maintain it."""
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

# --- Run the bot ---
if __name__ == "__main__":
    start_socket()