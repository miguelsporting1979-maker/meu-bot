import random
from datetime import datetime, time
import pytz
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

TOKEN = "8667107306:AAHsMiPG9oslWJ-z2_VNPtZvptsnn7o70k4"

CANAL_FREE = -1003731784397
CANAL_VIP = -1003770413249

FREE_HORAS = [(10,11),(14,15),(21,22)]
VIP_HORAS = [(9,10),(11,12),(15,16),(17,18),(20,21),(22,23)]

sinal_ativo = False
em_gale = False

historico = []
ultimo_estado_horario = False

ultimo_sinal_tempo = None
ultimo_aviso_tempo = None
ultimo_vip_tempo = None

wins_azul = 0
wins_vermelho = 0
loss_azul = 0
loss_vermelho = 0
empates = 0
sequencia = 0

def agora():
    tz = pytz.timezone("Europe/Lisbon")
    return datetime.now(tz)

def dentro_horario(lista):
    h = agora().hour
    return any(i <= h < f for i,f in lista)

def dentro_de_qualquer_horario():
    return dentro_horario(FREE_HORAS) or dentro_horario(VIP_HORAS)

def analisar_jogada():
    if len(historico) < 2:
        return random.choice(["🔵 PLAYER","🔴 BANKER"])

    if historico[-1] == historico[-2]:
        return "🔵 PLAYER" if historico[-1] == "🔴" else "🔴 BANKER"
    else:
        return "🔵 PLAYER" if historico[-1] == "🔵" else "🔴 BANKER"

def atualizar_historico(cor):
    historico.append(cor)
    if len(historico) > 10:
        historico.pop(0)

def botoes_iniciais():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ VITÓRIA AZUL", callback_data="win_azul"),
         InlineKeyboardButton("✅ VITÓRIA VERMELHO", callback_data="win_vermelho")],
        [InlineKeyboardButton("❌ DERROTA AZUL", callback_data="loss_azul"),
         InlineKeyboardButton("❌ DERROTA VERMELHO", callback_data="loss_vermelho")],
        [InlineKeyboardButton("🟡 EMPATE", callback_data="empate")],
        [InlineKeyboardButton("⚠️ FAZER GALE 1", callback_data="gale")]
    ])

def botoes_gale():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ VITÓRIA AZUL", callback_data="win_azul"),
         InlineKeyboardButton("✅ VITÓRIA VERMELHO", callback_data="win_vermelho")],
        [InlineKeyboardButton("❌ DERROTA FINAL", callback_data="loss_final")]
    ])

async def enviar_sinal(context, canal):
    global sinal_ativo, ultimo_sinal_tempo

    cor = analisar_jogada()

    msg = f"""📊 NOVA ENTRADA

{cor}
🟡 PROTEGER EMPATE
"""

    await context.bot.send_message(chat_id=canal, text=msg, reply_markup=botoes_iniciais())

    sinal_ativo = True
    ultimo_sinal_tempo = agora()

async def enviar_aviso(context):
    if ultimo_sinal_tempo and (agora() - ultimo_sinal_tempo).seconds < 120:
        return

    msg = """⚠️ JOGO RESPONSÁVEL

🔞 Proibido menores de 18 anos
💰 Não jogue dinheiro que não pode perder
📊 Use gestão de banca

Jogue com responsabilidade."""

    await context.bot.send_message(chat_id=CANAL_FREE, text=msg)
    await context.bot.send_message(chat_id=CANAL_VIP, text=msg)

async def enviar_vip(context):
    if not dentro_horario(FREE_HORAS):
        return

    if ultimo_sinal_tempo and (agora() - ultimo_sinal_tempo).seconds < 120:
        return

    msg = """🚀 ACESSO VIP

🔥 Sinais exclusivos
📈 Maior assertividade
💎 Resultados consistentes

👉 Entra no VIP e leva o jogo a outro nível"""

    await context.bot.send_message(chat_id=CANAL_FREE, text=msg)

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global sinal_ativo, sequencia

    q = update.callback_query
    await q.answer()

    if q.data == "win_azul":
        atualizar_historico("🔵")
        sequencia += 1
        await q.message.reply_text(f"✅ VITÓRIA AZUL\n🔥 VITÓRIAS SEGUIDAS: {sequencia}")
        sinal_ativo = False

    elif q.data == "win_vermelho":
        atualizar_historico("🔴")
        sequencia += 1
        await q.message.reply_text(f"✅ VITÓRIA VERMELHO\n🔥 VITÓRIAS SEGUIDAS: {sequencia}")
        sinal_ativo = False

    elif q.data == "loss_azul":
        atualizar_historico("🔴")
        sequencia = 0
        await q.message.reply_text("❌ DERROTA AZUL")
        sinal_ativo = False

    elif q.data == "loss_vermelho":
        atualizar_historico("🔵")
        sequencia = 0
        await q.message.reply_text("❌ DERROTA VERMELHO")
        sinal_ativo = False

    elif q.data == "loss_final":
        sequencia = 0
        await q.message.reply_text("❌ DERROTA FINAL")
        sinal_ativo = False

    elif q.data == "empate":
        await q.message.reply_text("🟡 EMPATE")
        sinal_ativo = False

    elif q.data == "gale":
        await q.message.reply_text("⚠️ FAZER GALE", reply_markup=botoes_gale())

async def scheduler(context):
    global sinal_ativo, historico, ultimo_estado_horario

    dentro = dentro_de_qualquer_horario()

    if not dentro and ultimo_estado_horario:
        historico.clear()

    ultimo_estado_horario = dentro

    if not sinal_ativo:
        if dentro_horario(FREE_HORAS):
            await enviar_sinal(context, CANAL_FREE)
        elif dentro_horario(VIP_HORAS):
            await enviar_sinal(context, CANAL_VIP)

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CallbackQueryHandler(callback))

    app.job_queue.run_repeating(scheduler, interval=240, first=5)
    app.job_queue.run_repeating(enviar_aviso, interval=3600, first=600)
    app.job_queue.run_repeating(enviar_vip, interval=1800, first=900)

    print("🔥 BOT ATIVO")

    app.run_polling()

if __name__ == "__main__":
    main()
