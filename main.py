import requests
import pandas as pd
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8762924552:AAEhgjoGtbifpEZr6kMt92M7145qzJnEz8k"

symbol = "BTCUSDT"
balance = 30.0
in_position = False
buy_price = 0

FEE = 0.1  # %
users = set()

# ===== Kline data =====
def get_klines():
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit=50"
    data = requests.get(url).json()
    df = pd.DataFrame(data, columns=[
        "time","o","h","l","c","v","ct","qv","n","tb","tq","i"
    ])
    df["c"] = df["c"].astype(float)
    return df

# ===== EMA =====
def calculate_ema(df):
    df["ema9"] = df["c"].ewm(span=9).mean()
    df["ema21"] = df["c"].ewm(span=21).mean()
    return df

# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users.add(update.effective_chat.id)
    await update.message.reply_text("📊 Real analiz başladı!")

# ===== STATUS =====
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Balans: {balance:.2f} AZN")

# ===== ƏSAS STRATEGİYA =====
async def trading_loop(app):
    global balance, in_position, buy_price

    while True:
        try:
            df = get_klines()
            df = calculate_ema(df)

            last = df.iloc[-1]
            prev = df.iloc[-2]

            # EMA kəsişmə
            if not in_position:
                if prev["ema9"] < prev["ema21"] and last["ema9"] > last["ema21"]:
                    buy_price = last["c"]
                    in_position = True

                    msg = f"🟢 ALDI\nQiymət: {buy_price}"
                    for u in users:
                        await app.bot.send_message(u, msg)

            else:
                price = last["c"]
                change = ((price - buy_price) / buy_price) * 100
                net = change - (FEE * 2)

                # çıxış şərti
                if prev["ema9"] > prev["ema21"] and last["ema9"] < last["ema21"]:
                    profit = balance * (net / 100)
                    balance += profit
                    in_position = False

                    msg = f"💰 SATDI\nBalans: {balance:.2f}\nNəticə: {net:.2f}%"
                    for u in users:
                        await app.bot.send_message(u, msg)

        except Exception as e:
            print("Xəta:", e)

        await asyncio.sleep(10)

# ===== MAIN =====
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))

    asyncio.create_task(trading_loop(app))

    print("Bot işləyir...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
