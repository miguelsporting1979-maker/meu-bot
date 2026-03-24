import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import time
import threading
from datetime import datetime

TOKEN = "8636159746:AAFwSj8NjWbJp0iJW_vHyyoQeK6-bE5zbag"

CANAL_FREE = -1003731784397
CANAL_VIP = -1003770413249

bot = telebot.TeleBot(TOKEN)

estado = {
    "ciclo_ativo": False,
    "aguardando": False,
    "dados": {},
    "publico": True,
    "gale": False,
    "ultimo_sinal": None,
    "historico": [],
    "wins": 0,
    "loss": 0
}

# ================= BOTÕES ================= #

def menu_dados():
    kb = InlineKeyboardMarkup()

    # 🔵 AZUL CIMA
    kb.row(
        InlineKeyboardButton("🔵 Cima 1", callback_data="azc_1"),
        InlineKeyboardButton("🔵 Cima 2", callback_data="azc_2"),
        InlineKeyboardButton("🔵 Cima 3", callback_data="azc_3"),
    )
    kb.row(
        InlineKeyboardButton("🔵 Cima 4", callback_data="azc_4"),
        InlineKeyboardButton("🔵 Cima 5", callback_data="azc_5"),
        InlineKeyboardButton("🔵 Cima 6", callback_data="azc_6"),
    )

    # 🔵 AZUL BAIXO
    kb.row(
        InlineKeyboardButton("🔵 Baixo 1", callback_data="azb_1"),
        InlineKeyboardButton("🔵 Baixo 2", callback_data="azb_2"),
        InlineKeyboardButton("🔵 Baixo 3", callback_data="azb_3"),
    )
    kb.row(
        InlineKeyboardButton("🔵 Baixo 4", callback_data="azb_4"),
        InlineKeyboardButton("🔵 Baixo 5", callback_data="azb_5"),
        InlineKeyboardButton("🔵 Baixo 6", callback_data="azb_6"),
    )

    # 🔴 VERMELHO CIMA
    kb.row(
        InlineKeyboardButton("🔴 Cima 1", callback_data="vmc_1"),
        InlineKeyboardButton("🔴 Cima 2", callback_data="vmc_2"),
        InlineKeyboardButton("🔴 Cima 3", callback_data="vmc_3"),
    )
    kb.row(
        InlineKeyboardButton("🔴 Cima 4", callback_data="vmc_4"),
        InlineKeyboardButton("🔴 Cima 5", callback_data="vmc_5"),
        InlineKeyboardButton("🔴 Cima 6", callback_data="vmc_6"),
    )

    # 🔴 VERMELHO BAIXO
    kb.row(
        InlineKeyboardButton("🔴 Baixo 1", callback_data="vmb_1"),
        InlineKeyboardButton("🔴 Baixo 2", callback_data="vmb_2"),
        InlineKeyboardButton("🔴 Baixo 3", callback_data="vmb_3"),
    )
    kb.row(
        InlineKeyboardButton("🔴 Baixo 4", callback_data="vmb_4"),
        InlineKeyboardButton("🔴 Baixo 5", callback_data="vmb_5"),
        InlineKeyboardButton("🔴 Baixo 6", callback_data="vmb_6"),
    )

    # CONTROLOS
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

# ================= ENVIO ================= #

def enviar_sinal(canal):
    entrada = analisar()

    msg = f"""📊 NOVA ENTRADA

{entrada}
🟡 PROTEGER EMPATE
"""

    bot.send_message(canal, msg)
    bot.send_message(canal, "🎲 INSERE OS DADOS:", reply_markup=menu_dados())

    estado["aguardando"] = True
    estado["ultimo_sinal"] = canal

# ================= CALLBACK ================= #

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    data = call.data

    if data == "avaria":
        terminar_ciclo("🚨 CICLO TERMINADO\nNão apostar após avaria.")
        return

    if data == "troca":
        terminar_ciclo("🔄 CICLO TERMINADO\nNão apostar após troca de dados.")
        return

    tipo, valor = data.split("_")
    estado["dados"][tipo] = int(valor)

    if len(estado["dados"]) == 4:
        resultado = calcular_resultado()
        canal = estado["ultimo_sinal"]

        if estado["publico"]:
            bot.send_message(canal, f"🎲 Resultado: {resultado}")

        estado["historico"].append(resultado)

        if not estado["gale"]:
            estado["gale"] = True
            if resultado == "🟡":
                estado["wins"] += 1
            else:
                if estado["publico"]:
                    bot.send_message(canal, "⚠️ Gale 1 (opcional)")
        else:
            estado["gale"] = False
            if resultado == "🟡":
                estado["wins"] += 1
            else:
                estado["loss"] += 1

            estado["publico"] = not estado["publico"]

        estado["dados"] = {}
        estado["aguardando"] = False

# ================= CICLO ================= #

def ciclo(canal, duracao):
    estado["ciclo_ativo"] = True
    inicio = time.time()

    while time.time() - inicio < duracao:
        if not estado["ciclo_ativo"]:
            break

        if not estado["aguardando"]:
            enviar_sinal(canal)

        time.sleep(240)

    resumo(canal)

def terminar_ciclo(msg):
    estado["ciclo_ativo"] = False
    bot.send_message(CANAL_VIP, msg)
    resumo(CANAL_VIP)

def resumo(canal):
    total = estado["wins"] + estado["loss"]

    if total == 0:
        bot.send_message(canal, "Sem dados no ciclo.")
        return

    percent = int((estado["wins"] / total) * 100)

    bot.send_message(canal, f"""📊 RESULTADO DO CICLO

✅ Vitórias: {estado["wins"]}
❌ Derrotas: {estado["loss"]}

📈 Assertividade: {percent}%
""")

# ================= HORÁRIOS ================= #

def scheduler():
    while True:
        agora = datetime.now().strftime("%H:%M")

        # VIP
        if agora in ["10:00","11:00","15:30","16:30","18:30","20:00","21:00"]:
            threading.Thread(target=ciclo, args=(CANAL_VIP, 1800)).start()

        # FREE
        if agora in ["09:00","14:30","17:30"]:
            threading.Thread(target=ciclo, args=(CANAL_FREE, 1800)).start()

        time.sleep(60)

# ================= START ================= #

threading.Thread(target=scheduler).start()

print("🔥 BOT ATIVO")

bot.infinity_polling()
