import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import time
import threading

TOKEN = "8636159746:AAFwSj8NjWbJp0iJW_vHyyoQeK6-bE5zbag"

CANAL_FREE = -1003731784397
CANAL_VIP = -1003770413249

bot = telebot.TeleBot(TOKEN)

estado = {
    "ativo": False,
    "canal": None,
    "dados": {},
    "entrada": None,
    "gale": False,
    "aguardando": False,
    "wins": 0,
    "loss": 0,
    "empates": 0,
    "lock": False
}

# ================= BOTÕES ================= #

def menu():
    kb = InlineKeyboardMarkup()

    for prefix in ["azc","azb","vmc","vmb"]:
        for i in range(1,7,3):
            kb.row(
                InlineKeyboardButton(f"{prefix.upper()} {i}", callback_data=f"{prefix}_{i}"),
                InlineKeyboardButton(f"{prefix.upper()} {i+1}", callback_data=f"{prefix}_{i+1}"),
                InlineKeyboardButton(f"{prefix.upper()} {i+2}", callback_data=f"{prefix}_{i+2}")
            )

    kb.row(
        InlineKeyboardButton("🚨 AVARIA", callback_data="avaria"),
        InlineKeyboardButton("🔄 TROCA", callback_data="troca")
    )

    return kb

# ================= LÓGICA ================= #

def resultado():
    az = estado["dados"].get("azc",0) + estado["dados"].get("azb",0)
    vm = estado["dados"].get("vmc",0) + estado["dados"].get("vmb",0)

    if az > vm:
        return "🔵"
    elif vm > az:
        return "🔴"
    return "🟡"

def entrada():
    return "🔵 PLAYER"

# ================= SINAL ================= #

def enviar():
    estado["dados"] = {}
    estado["entrada"] = entrada()
    estado["aguardando"] = True

    bot.send_message(estado["canal"], f"""📊 NOVA ENTRADA

{estado["entrada"]}
🟡 PROTEGER EMPATE
""")

    bot.send_message(estado["canal"], "🎲 INSERE OS DADOS:", reply_markup=menu())

# ================= LOOP ================= #

def loop():
    time.sleep(27)

    while estado["ativo"]:

        if not estado["aguardando"]:
            enviar()

        for _ in range(189):
            if not estado["ativo"]:
                return
            time.sleep(1)

    resumo()

# ================= CALLBACK ================= #

@bot.callback_query_handler(func=lambda call: True)
def cb(call):
    if estado["lock"]:
        return

    data = call.data

    if data == "avaria":
        estado["ativo"] = False
        bot.send_message(estado["canal"], "🚨 CICLO TERMINADO - AVARIA")
        resumo()
        return

    if data == "troca":
        estado["ativo"] = False
        bot.send_message(estado["canal"], "🔄 CICLO TERMINADO - TROCA")
        resumo()
        return

    tipo, val = data.split("_")
    estado["dados"][tipo] = int(val)

    if len(estado["dados"]) == 4:
        estado["lock"] = True

        res = resultado()

        bot.send_message(estado["canal"], f"🎲 Resultado: {res}")

        if res == "🟡":
            estado["empates"] += 1

        elif res == "🔵":
            estado["wins"] += 1
            estado["gale"] = False

        else:
            if not estado["gale"]:
                estado["gale"] = True
                bot.send_message(estado["canal"], "⚠️ Gale 1 (opcional)")
            else:
                estado["loss"] += 1
                estado["gale"] = False

        estado["aguardando"] = False
        estado["lock"] = False

# ================= COMANDOS ================= #

@bot.message_handler(commands=['startvip'])
def startvip(msg):
    estado["ativo"] = True
    estado["canal"] = CANAL_VIP
    threading.Thread(target=loop).start()
    bot.send_message(msg.chat.id, "VIP iniciado")

@bot.message_handler(commands=['startfree'])
def startfree(msg):
    estado["ativo"] = True
    estado["canal"] = CANAL_FREE
    threading.Thread(target=loop).start()
    bot.send_message(msg.chat.id, "FREE iniciado")

@bot.message_handler(commands=['stop'])
def stop(msg):
    estado["ativo"] = False
    bot.send_message(msg.chat.id, "STOP recebido")

# ================= RESUMO ================= #

def resumo():
    total = estado["wins"] + estado["loss"]
    percent = int((estado["wins"]/total)*100) if total else 0

    bot.send_message(estado["canal"], f"""📊 RESULTADO

✅ {estado["wins"]}
🟡 {estado["empates"]}
❌ {estado["loss"]}

📈 {percent}%""")

# ================= START ================= #

print("BOT FINAL")
bot.infinity_polling()
