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
    kb = InlineKeyboardMarkup(row_width=3)

    for i in range(1,7):
        kb.add(InlineKeyboardButton(f"🔵 Cima {i}", callback_data=f"azc_{i}"))
    for i in range(1,7):
        kb.add(InlineKeyboardButton(f"🔵 Baixo {i}", callback_data=f"azb_{i}"))
    for i in range(1,7):
        kb.add(InlineKeyboardButton(f"🔴 Cima {i}", callback_data=f"vmc_{i}"))
    for i in range(1,7):
        kb.add(InlineKeyboardButton(f"🔴 Baixo {i}", callback_data=f"vmb_{i}"))

    kb.add(
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

    if "_" in data:
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
            if resultado != "🟡":
                if estado["publico"]:
                    bot.send_message(canal, "⚠️ Gale 1 (opcional)")
            else:
                estado["wins"] += 1
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

def ciclo(canal):
    estado["ciclo_ativo"] = True
    inicio = time.time()

    while time.time() - inicio < 3600:
        if not estado["ciclo_ativo"]:
            break

        if not estado["aguardando"]:
            enviar_sinal(canal)

        time.sleep(246)

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

        if agora in ["08:00","09:00","10:00","11:00","14:00","15:00","16:00","17:00","18:00","19:00","20:00","21:00","22:00"]:
            threading.Thread(target=ciclo, args=(CANAL_VIP,)).start()

        if agora in ["10:00","15:00","20:00"]:
            threading.Thread(target=ciclo, args=(CANAL_FREE,)).start()

        time.sleep(60)

# ================= START ================= #

threading.Thread(target=scheduler).start()

print("🔥 BOT ATIVO")

bot.infinity_polling()
