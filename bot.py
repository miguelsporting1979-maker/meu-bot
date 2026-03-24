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
    "inicio_sinal": 0,
    "wins": 0,
    "loss": 0,
    "empates": 0
}

# ================= BOTÕES ================= #

def menu():
    kb = InlineKeyboardMarkup()

    # AZUL CIMA
    kb.row(InlineKeyboardButton("🔵 C1","azc_1"),InlineKeyboardButton("🔵 C2","azc_2"),InlineKeyboardButton("🔵 C3","azc_3"))
    kb.row(InlineKeyboardButton("🔵 C4","azc_4"),InlineKeyboardButton("🔵 C5","azc_5"),InlineKeyboardButton("🔵 C6","azc_6"))

    kb.row(InlineKeyboardButton("🔵────────","ignore"))

    # AZUL BAIXO
    kb.row(InlineKeyboardButton("🔵 B1","azb_1"),InlineKeyboardButton("🔵 B2","azb_2"),InlineKeyboardButton("🔵 B3","azb_3"))
    kb.row(InlineKeyboardButton("🔵 B4","azb_4"),InlineKeyboardButton("🔵 B5","azb_5"),InlineKeyboardButton("🔵 B6","azb_6"))

    kb.row(InlineKeyboardButton("🟡══════","ignore"))

    # VERMELHO CIMA
    kb.row(InlineKeyboardButton("🔴 C1","vmc_1"),InlineKeyboardButton("🔴 C2","vmc_2"),InlineKeyboardButton("🔴 C3","vmc_3"))
    kb.row(InlineKeyboardButton("🔴 C4","vmc_4"),InlineKeyboardButton("🔴 C5","vmc_5"),InlineKeyboardButton("🔴 C6","vmc_6"))

    kb.row(InlineKeyboardButton("🔴────────","ignore"))

    # VERMELHO BAIXO
    kb.row(InlineKeyboardButton("🔴 B1","vmb_1"),InlineKeyboardButton("🔴 B2","vmb_2"),InlineKeyboardButton("🔴 B3","vmb_3"))
    kb.row(InlineKeyboardButton("🔴 B4","vmb_4"),InlineKeyboardButton("🔴 B5","vmb_5"),InlineKeyboardButton("🔴 B6","vmb_6"))

    kb.row(InlineKeyboardButton("⚫══════","ignore"))

    kb.row(
        InlineKeyboardButton("🚨 AVARIA","avaria"),
        InlineKeyboardButton("🔄 TROCA","troca")
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

def enviar_sinal():
    estado["dados"] = {}
    estado["aguardando"] = True
    estado["inicio_sinal"] = time.time()

    bot.send_message(estado["canal"], "📊 NOVA ENTRADA\n\n🔵 PLAYER\n🟡 PROTEGER EMPATE")
    bot.send_message(estado["canal"], "🎲 INSERE OS DADOS:", reply_markup=menu())

# ================= LOOP ================= #

def ciclo():
    time.sleep(27)

    while estado["ativo"]:

        # timeout de segurança (60s)
        if estado["aguardando"]:
            if time.time() - estado["inicio_sinal"] > 60:
                estado["aguardando"] = False

        if not estado["aguardando"]:
            enviar_sinal()

        for _ in range(189):
            if not estado["ativo"]:
                resumo()
                return
            time.sleep(1)

# ================= CALLBACK ================= #

@bot.callback_query_handler(func=lambda call: True)
def cb(call):
    data = call.data

    if data == "ignore":
        return

    if data == "avaria":
        estado["ativo"] = False
        bot.send_message(estado["canal"], "🚨 CICLO TERMINADO (AVARIA)")
        resumo()
        return

    if data == "troca":
        estado["ativo"] = False
        bot.send_message(estado["canal"], "🔄 CICLO TERMINADO (TROCA)")
        resumo()
        return

    tipo, val = data.split("_")
    estado["dados"][tipo] = int(val)

    if len(estado["dados"]) == 4:
        res = calcular()

        if res == "🔵":
            estado["wins"] += 1
            texto = "✅ Vitória"
        elif res == "🔴":
            estado["loss"] += 1
            texto = "❌ Derrota"
        else:
            estado["empates"] += 1
            texto = "🟡 Empate"

        bot.send_message(estado["canal"], f"🎲 Resultado: {res}\n{texto}")

        estado["aguardando"] = False

# ================= COMANDOS ================= #

@bot.message_handler(commands=['startvip'])
def startvip(msg):
    estado["ativo"] = True
    estado["canal"] = CANAL_VIP
    bot.send_message(CANAL_VIP, "🚀 CICLO INICIADO (VIP)")
    threading.Thread(target=ciclo).start()

@bot.message_handler(commands=['startfree'])
def startfree(msg):
    estado["ativo"] = True
    estado["canal"] = CANAL_FREE
    bot.send_message(CANAL_FREE, "🚀 CICLO INICIADO (FREE)")
    threading.Thread(target=ciclo).start()

@bot.message_handler(commands=['stop'])
def stop(msg):
    estado["ativo"] = False
    bot.send_message(estado["canal"], "🛑 CICLO TERMINADO")
    resumo()

# ================= RESUMO ================= #

def resumo():
    total = estado["wins"] + estado["loss"]
    percent = int((estado["wins"]/total)*100) if total else 0

    bot.send_message(estado["canal"], f"""📊 RESULTADO DO CICLO

✅ Vitórias: {estado["wins"]}
🟡 Empates: {estado["empates"]}
❌ Derrotas: {estado["loss"]}

📈 Assertividade: {percent}%""")

# ================= START ================= #

print("BOT V3 FINAL")
bot.infinity_polling()
