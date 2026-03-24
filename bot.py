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
    "aguardando": False,
    "wins": 0,
    "loss": 0,
    "empates": 0
}

# ================= BOTÕES ================= #

def menu():
    kb = InlineKeyboardMarkup()

    # 🔵 AZUL CIMA
    kb.row(
        InlineKeyboardButton("🔵 C1", callback_data="azc_1"),
        InlineKeyboardButton("🔵 C2", callback_data="azc_2"),
        InlineKeyboardButton("🔵 C3", callback_data="azc_3")
    )
    kb.row(
        InlineKeyboardButton("🔵 C4", callback_data="azc_4"),
        InlineKeyboardButton("🔵 C5", callback_data="azc_5"),
        InlineKeyboardButton("🔵 C6", callback_data="azc_6")
    )

    kb.row(InlineKeyboardButton("🔵────────────", callback_data="ignore"))

    # 🔵 AZUL BAIXO
    kb.row(
        InlineKeyboardButton("🔵 B1", callback_data="azb_1"),
        InlineKeyboardButton("🔵 B2", callback_data="azb_2"),
        InlineKeyboardButton("🔵 B3", callback_data="azb_3")
    )
    kb.row(
        InlineKeyboardButton("🔵 B4", callback_data="azb_4"),
        InlineKeyboardButton("🔵 B5", callback_data="azb_5"),
        InlineKeyboardButton("🔵 B6", callback_data="azb_6")
    )

    kb.row(InlineKeyboardButton("🟡════════════", callback_data="ignore"))

    # 🔴 VERMELHO CIMA
    kb.row(
        InlineKeyboardButton("🔴 C1", callback_data="vmc_1"),
        InlineKeyboardButton("🔴 C2", callback_data="vmc_2"),
        InlineKeyboardButton("🔴 C3", callback_data="vmc_3")
    )
    kb.row(
        InlineKeyboardButton("🔴 C4", callback_data="vmc_4"),
        InlineKeyboardButton("🔴 C5", callback_data="vmc_5"),
        InlineKeyboardButton("🔴 C6", callback_data="vmc_6")
    )

    kb.row(InlineKeyboardButton("🔴────────────", callback_data="ignore"))

    # 🔴 VERMELHO BAIXO
    kb.row(
        InlineKeyboardButton("🔴 B1", callback_data="vmb_1"),
        InlineKeyboardButton("🔴 B2", callback_data="vmb_2"),
        InlineKeyboardButton("🔴 B3", callback_data="vmb_3")
    )
    kb.row(
        InlineKeyboardButton("🔴 B4", callback_data="vmb_4"),
        InlineKeyboardButton("🔴 B5", callback_data="vmb_5"),
        InlineKeyboardButton("🔴 B6", callback_data="vmb_6")
    )

    kb.row(InlineKeyboardButton("⚫════════════", callback_data="ignore"))

    kb.row(
        InlineKeyboardButton("🚨 AVARIA", callback_data="avaria"),
        InlineKeyboardButton("🔄 TROCA", callback_data="troca")
    )

    return kb

# ================= RESULTADO ================= #

def calcular():
    az = estado["dados"].get("azc",0) + estado["dados"].get("azb",0)
    vm = estado["dados"].get("vmc",0) + estado["dados"].get("vmb",0)

    if az > vm:
        return "🔵"
    elif vm > az:
        return "🔴"
    return "🟡"

# ================= SINAL ================= #

def enviar():
    estado["dados"] = {}
    estado["aguardando"] = True

    bot.send_message(estado["canal"], "📊 NOVA ENTRADA\n\n🔵 PLAYER\n🟡 PROTEGER EMPATE")
    bot.send_message(estado["canal"], "🎲 INSERE OS DADOS:", reply_markup=menu())

# ================= LOOP ================= #

def ciclo():
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
    data = call.data

    if data == "ignore":
        return

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
        res = calcular()

        bot.send_message(estado["canal"], f"🎲 Resultado: {res}")

        if res == "🟡":
            estado["empates"] += 1
        elif res == "🔵":
            estado["wins"] += 1
        else:
            estado["loss"] += 1

        estado["aguardando"] = False

# ================= COMANDOS ================= #

@bot.message_handler(commands=['startvip'])
def startvip(msg):
    estado["ativo"] = True
    estado["canal"] = CANAL_VIP
    threading.Thread(target=ciclo).start()
    bot.send_message(msg.chat.id, "VIP iniciado")

@bot.message_handler(commands=['startfree'])
def startfree(msg):
    estado["ativo"] = True
    estado["canal"] = CANAL_FREE
    threading.Thread(target=ciclo).start()
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

print("BOT LIMPO FINAL")
bot.infinity_polling()
