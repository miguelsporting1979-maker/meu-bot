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
    "aguardando": False,
    "canal": None,
    "dados": {},
    "entrada_atual": None,
    "gale": False,
    "historico": [],
    "wins": 0,
    "loss": 0,
    "empates": 0
}

# ================= BOTÕES ================= #

def menu_dados():
    kb = InlineKeyboardMarkup()

    # AZUL
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

    # VERMELHO
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

    kb.row(
        InlineKeyboardButton("🚨 AVARIA", callback_data="avaria"),
        InlineKeyboardButton("🔄 TROCA", callback_data="troca")
    )

    return kb

# ================= LÓGICA ================= #

def calcular_resultado():
    az = estado["dados"].get("azc",0) + estado["dados"].get("azb",0)
    vm = estado["dados"].get("vmc",0) + estado["dados"].get("vmb",0)

    if az > vm:
        return "🔵"
    elif vm > az:
        return "🔴"
    else:
        return "🟡"

def analisar():
    if len(estado["historico"]) < 2:
        return "🔵 PLAYER"
    if estado["historico"][-1] == estado["historico"][-2]:
        return "🔴 BANKER"
    return "🔵 PLAYER"

# ================= SINAIS ================= #

def enviar_sinal():
    entrada = analisar()

    bot.send_message(estado["canal"], f"""📊 NOVA ENTRADA

{entrada}
🟡 PROTEGER EMPATE
""")

    bot.send_message(estado["canal"], "🎲 INSERE OS DADOS:", reply_markup=menu_dados())

    estado["aguardando"] = True
    estado["entrada_atual"] = entrada
    estado["dados"] = {}

# ================= CICLO ================= #

def ciclo():
    time.sleep(27)  # delay inicial

    while estado["ativo"]:

        if not estado["aguardando"]:
            enviar_sinal()

        time.sleep(189)

    resumo()

# ================= CALLBACK ================= #

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
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

    tipo, valor = data.split("_")
    estado["dados"][tipo] = int(valor)

    if len(estado["dados"]) == 4:
        resultado = calcular_resultado()

        bot.send_message(estado["canal"], f"🎲 Resultado: {resultado}")

        estado["historico"].append(resultado)

        if resultado == "🟡":
            estado["empates"] += 1

        elif ("🔵" in estado["entrada_atual"] and resultado == "🔵") or \
             ("🔴" in estado["entrada_atual"] and resultado == "🔴"):

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

# ================= COMANDOS ================= #

@bot.message_handler(commands=['startvip'])
def start_vip(message):
    estado["ativo"] = True
    estado["canal"] = CANAL_VIP
    threading.Thread(target=ciclo).start()
    bot.send_message(CANAL_VIP, "🚀 CICLO INICIADO (VIP)")

@bot.message_handler(commands=['startfree'])
def start_free(message):
    estado["ativo"] = True
    estado["canal"] = CANAL_FREE
    threading.Thread(target=ciclo).start()
    bot.send_message(CANAL_FREE, "🚀 CICLO INICIADO (FREE)")

@bot.message_handler(commands=['stop'])
def stop(message):
    estado["ativo"] = False
    bot.send_message(estado["canal"], "🛑 CICLO PARADO")

# ================= RESUMO ================= #

def resumo():
    total = estado["wins"] + estado["loss"]
    percent = int((estado["wins"] / total) * 100) if total > 0 else 0

    bot.send_message(estado["canal"], f"""📊 RESULTADO DO CICLO

✅ Vitórias: {estado["wins"]}
🟡 Empates: {estado["empates"]}
❌ Derrotas: {estado["loss"]}

📈 Assertividade: {percent}%
""")

# ================= START ================= #

print("🔥 BOT MANUAL ATIVO")
bot.infinity_polling()
