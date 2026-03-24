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

# ================= ENVIO ================= #

def enviar_sinal(canal):
    entrada = analisar()

    bot.send_message(canal, f"""📊 NOVA ENTRADA

{entrada}
🟡 PROTEGER EMPATE
""")

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
        terminar_ciclo("🔄 CICLO TERMINADO\nNão apostar após troca.")
        return

    tipo, valor = data.split("_")
    estado["dados"][tipo] = int(valor)

    if len(estado["dados"]) == 4:
        resultado = calcular_resultado()
        canal = estado["ultimo_sinal"]

        bot.send_message(canal, f"🎲 Resultado: {resultado}")

        estado["historico"].append(resultado)

        if resultado == "🟡":
            estado["empates"] += 1
        else:
            if not estado["gale"]:
                estado["gale"] = True
                bot.send_message(canal, "⚠️ Gale 1 (opcional)")
            else:
                estado["gale"] = False
                if resultado == "🔵":
                    estado["wins"] += 1
                else:
                    estado["loss"] += 1

        estado["dados"] = {}
        estado["aguardando"] = False

# ================= CICLO ================= #

def ciclo(canal, duracao_min):
    estado["ciclo_ativo"] = True
    inicio = time.time()

    while time.time() - inicio < duracao_min * 60:
        if not estado["aguardando"]:
            enviar_sinal(canal)

        time.sleep(30)

    resumo(canal)

def resumo(canal):
    total = estado["wins"] + estado["loss"]

    percent = int((estado["wins"] / total) * 100) if total > 0 else 0

    bot.send_message(canal, f"""📊 RESULTADO DO CICLO

✅ Vitórias: {estado["wins"]}
🤝 Empates: {estado["empates"]}
❌ Derrotas: {estado["loss"]}

📈 Assertividade: {percent}%
""")

# ================= HORÁRIOS (ANTI-FALHA) ================= #

executados = []

def scheduler():
    while True:
        agora = datetime.now().strftime("%H:%M")

        horarios = [
            ("09:00","FREE"), ("14:30","FREE"), ("17:30","FREE"),
            ("10:00","VIP"), ("11:00","VIP"), ("15:30","VIP"),
            ("16:30","VIP"), ("18:30","VIP"), ("20:00","VIP"), ("21:00","VIP")
        ]

        for hora, tipo in horarios:
            if agora >= hora and hora not in executados:
                executados.append(hora)

                if tipo == "VIP":
                    threading.Thread(target=ciclo, args=(CANAL_VIP,30)).start()
                else:
                    threading.Thread(target=ciclo, args=(CANAL_FREE,30)).start()

        time.sleep(20)

# ================= START ================= #

threading.Thread(target=scheduler).start()

print("🔥 BOT ATIVO")

bot.infinity_polling()
