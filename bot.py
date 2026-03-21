import random
import os
from datetime import datetime, time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("8441283882:AAGWtfuqmZZKBK3aUDT-P-V6sxHTVSgT24c")

CANAL_FREE = -1003731784397
CANAL_VIP = -1003770413249

FREE_HORAS = [(10,11),(15,16),(21,22)]
VIP_HORAS = [(9,10),(11,12),(15,16),(17,18),(20,21),(22,23)]

sinal_ativo = False
em_gale = False

wins_azul = 0
wins_vermelho = 0
loss_azul = 0
loss_vermelho = 0
empates = 0
sequencia = 0

def dentro_horario(lista):
    agora = datetime.now().hour
    return any(i <= agora < f for i,f in lista)

def botoes_iniciais():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ VITÓRIA AZUL", callback_data="win_azul"),
            InlineKeyboardButton("✅ VITÓRIA VERMELHO", callback_data="win_vermelho"),
        ],
        [
            InlineKeyboardButton("❌ DERROTA AZUL", callback_data="loss_azul"),
            InlineKeyboardButton("❌ DERROTA VERMELHO", callback_data="loss_vermelho"),
        ],
        [
            InlineKeyboardButton("🟡 EMPATE", callback_data="empate"),
        ],
        [
            InlineKeyboardButton("⚠️ FAZER GALE 1 (opcional)", callback_data="gale")
        ]
    ])

def botoes_gale():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ VITÓRIA AZUL", callback_data="win_azul"),
            InlineKeyboardButton("✅ VITÓRIA VERMELHO", callback_data="win_vermelho"),
        ],
        [
            InlineKeyboardButton("❌ DERROTA - NÃO ACONSELHO GALE 2", callback_data="loss_final"),
        ]
    ])

async def enviar_sinal(context, canal):
    global sinal_ativo, em_gale

    cor = random.choice(["🔵 PLAYER","🔴 BANKER"])

    msg = f"""
📊 NOVA ENTRADA

{cor}
🟡 PROTEGER EMPATE
"""

    await context.bot.send_message(
        chat_id=canal,
        text=msg,
        reply_markup=botoes_iniciais()
    )

    sinal_ativo = True
    em_gale = False

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global sinal_ativo, em_gale, sequencia
    global wins_azul, wins_vermelho, loss_azul, loss_vermelho, empates

    q = update.callback_query
    await q.answer()

    if q.data == "win_azul":
        wins_azul += 1
        sequencia += 1
        await q.message.reply_text(f"✅ VITÓRIA AZUL\n🔥 Sequência: {sequencia}")
        sinal_ativo = False

    elif q.data == "win_vermelho":
        wins_vermelho += 1
        sequencia += 1
        await q.message.reply_text(f"✅ VITÓRIA VERMELHO\n🔥 Sequência: {sequencia}")
        sinal_ativo = False

    elif q.data == "loss_azul":
        loss_azul += 1
        sequencia = 0
        await q.message.reply_text("❌ DERROTA AZUL")
        sinal_ativo = False

    elif q.data == "loss_vermelho":
        loss_vermelho += 1
        sequencia = 0
        await q.message.reply_text("❌ DERROTA VERMELHO")
        sinal_ativo = False

    elif q.data == "loss_final":
        loss_azul += 1
        loss_vermelho += 1
        sequencia = 0
        await q.message.reply_text("❌ DERROTA\n⚠️ Não aconselho GALE 2")
        sinal_ativo = False

    elif q.data == "empate":
        empates += 1
        sequencia += 1
        await q.message.reply_text("🟡 EMPATE\n🛡️ Proteção aplicada")
        sinal_ativo = False

    elif q.data == "gale":
        em_gale = True
        sequencia = 0
        await q.message.reply_text(
            "⚠️ FAZER GALE 1 (opcional)",
            reply_markup=botoes_gale()
        )

async def scheduler(context):
    global sinal_ativo

    if sinal_ativo:
        return

    if dentro_horario(FREE_HORAS):
        await enviar_sinal(context, CANAL_FREE)

    if dentro_horario(VIP_HORAS):
        await enviar_sinal(context, CANAL_VIP)

async def bom_dia(context):
    msg = """
🌅 BOM DIA

📊 HORÁRIOS DE HOJE

FREE:
10h–11h
15h–16h
21h–22h

VIP:
09h–10h
11h–12h
15h–16h
17h–18h
20h–21h
22h–23h
"""
    await context.bot.send_message(chat_id=CANAL_FREE, text=msg)
    await context.bot.send_message(chat_id=CANAL_VIP, text=msg)

async def relatorio_dia(context):
    total = wins_azul + wins_vermelho + empates + loss_azul + loss_vermelho

    if total == 0:
        return

    wins_total = wins_azul + wins_vermelho + empates
    assertividade = int((wins_total / total) * 100)

    msg = f"""
🌙 BOA NOITE

📊 RESULTADOS DO DIA

🔵 Vitórias Azul: {wins_azul}
🔴 Vitórias Vermelho: {wins_vermelho}
🟡 Empates: {empates}
❌ Derrotas Azul: {loss_azul}
❌ Derrotas Vermelho: {loss_vermelho}

📈 Assertividade: {assertividade}%
"""

    await context.bot.send_message(chat_id=CANAL_FREE, text=msg)
    await context.bot.send_message(chat_id=CANAL_VIP, text=msg)

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CallbackQueryHandler(callback))

    app.job_queue.run_repeating(scheduler, interval=240, first=5)

    app.job_queue.run_daily(bom_dia, time=time(8,30))
    app.job_queue.run_daily(relatorio_dia, time=time(23,10))

    print("🔥 BOT ATIVO")

    app.run_polling()

if __name__ == "__main__":
    main()




