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

# ---------- ESTADO ----------
historico = []
sinal_ativo = False
em_gale = False

ultimo_sinal_tempo = None
timeout_segundos = 90

ultimo_horario = None

# ---------- CONTADORES ----------
wins_azul = wins_vermelho = wins_empate = 0
wins_gale_azul = wins_gale_vermelho = wins_gale_empate = 0

loss_azul = loss_vermelho = loss_empate = loss_gale = 0

sequencia = 0

# ---------- TEMPO ----------
def agora():
    tz = pytz.timezone("Europe/Lisbon")
    return datetime.now(tz)

def dentro_horario(lista):
    h = agora().hour
    for i,f in lista:
        if i <= h < f:
            return True, i
    return False, None

# ---------- RESET ----------
def resetar_estado():
    global historico, sequencia, sinal_ativo, em_gale

    historico.clear()
    sequencia = 0
    sinal_ativo = False
    em_gale = False

# ---------- TIMEOUT ----------
def verificar_timeout():
    global sinal_ativo

    if sinal_ativo and ultimo_sinal_tempo:
        if (agora() - ultimo_sinal_tempo).total_seconds() > timeout_segundos:
            sinal_ativo = False

# ---------- LÓGICA ----------
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

# ---------- BOTÕES ----------
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
        [InlineKeyboardButton("✅ VITÓRIA AZUL", callback_data="win_gale_azul"),
         InlineKeyboardButton("🟡 EMPATE APÓS GALE 1", callback_data="win_gale_empate"),
         InlineKeyboardButton("✅ VITÓRIA VERMELHO", callback_data="win_gale_vermelho")],
        [InlineKeyboardButton("❌ DERROTA FINAL", callback_data="loss_gale")]
    ])

# ---------- SINAL ----------
async def enviar_sinal(context, canal):
    global sinal_ativo, ultimo_sinal_tempo

    if sinal_ativo:
        return

    cor = analisar_jogada()

    msg = f"""📊 NOVA ENTRADA

{cor}
🟡 PROTEGER EMPATE
"""

    await context.bot.send_message(chat_id=canal, text=msg, reply_markup=botoes_iniciais())

    sinal_ativo = True
    ultimo_sinal_tempo = agora()

# ---------- CALLBACK ----------
async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global sinal_ativo, em_gale, sequencia
    global wins_azul, wins_vermelho, wins_empate
    global wins_gale_azul, wins_gale_vermelho, wins_gale_empate
    global loss_azul, loss_vermelho, loss_empate, loss_gale

    q = update.callback_query
    await q.answer()

    if not sinal_ativo:
        return

    # VITÓRIAS
    if q.data == "win_azul":
        atualizar_historico("🔵")
        wins_azul += 1
        sequencia += 1
        await q.message.reply_text(f"✅ VITÓRIA AZUL\n🔥 VITÓRIAS SEGUIDAS: {sequencia}")
        sinal_ativo = False

    elif q.data == "win_vermelho":
        atualizar_historico("🔴")
        wins_vermelho += 1
        sequencia += 1
        await q.message.reply_text(f"✅ VITÓRIA VERMELHO\n🔥 VITÓRIAS SEGUIDAS: {sequencia}")
        sinal_ativo = False

    elif q.data == "empate":
        wins_empate += 1
        sequencia += 1
        await q.message.reply_text(f"🟡 VITÓRIA NO EMPATE\n🔥 VITÓRIAS SEGUIDAS: {sequencia}")
        sinal_ativo = False

    # DERROTAS
    elif q.data in ["loss_azul","loss_vermelho"]:
        sequencia = 0
        await q.message.reply_text("❌ DERROTA")
        sinal_ativo = False

    # GALE
    elif q.data == "gale":
        em_gale = True
        await q.message.reply_text("⚠️ FAZER GALE 1", reply_markup=botoes_gale())

    elif "win_gale" in q.data:
        sequencia += 1
        await q.message.reply_text(f"🔥 VITÓRIA NO GALE\n🔥 VITÓRIAS SEGUIDAS: {sequencia}")
        sinal_ativo = False

    elif q.data == "loss_gale":
        loss_gale += 1
        sequencia = 0
        await q.message.reply_text("❌ DERROTA FINAL")
        sinal_ativo = False

# ---------- SCHEDULER ----------
async def scheduler(context):
    global ultimo_horario

    verificar_timeout()

    dentro_free, h_free = dentro_horario(FREE_HORAS)
    dentro_vip, h_vip = dentro_horario(VIP_HORAS)

    horario_atual = h_free if dentro_free else h_vip

    if horario_atual != ultimo_horario and horario_atual is not None:
        resetar_estado()
        ultimo_horario = horario_atual

    if not sinal_ativo:
        if dentro_free:
            await enviar_sinal(context, CANAL_FREE)
        elif dentro_vip:
            await enviar_sinal(context, CANAL_VIP)

# ---------- MAIN ----------
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CallbackQueryHandler(callback))

    app.job_queue.run_repeating(scheduler, interval=240, first=5)

    print("🔥 BOT ATIVO E ESTÁVEL")

    app.run_polling()

if __name__ == "__main__":
    main()
