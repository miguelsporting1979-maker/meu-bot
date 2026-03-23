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
sequencia = 0
ultimo_sinal_timestamp = 0
intervalo_sinal = 246  # 🔥 NOVO TIMING FIXO

# ---------- CONTADORES ----------
wins_azul = wins_vermelho = wins_empate = 0
wins_gale_azul = wins_gale_vermelho = wins_gale_empate = 0
loss_azul = loss_vermelho = loss_empate = loss_gale = 0

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
    global ultimo_sinal_timestamp

    cor = analisar_jogada()

    msg = f"""📊 NOVA ENTRADA

{cor}
🟡 PROTEGER EMPATE
"""

    await context.bot.send_message(chat_id=canal, text=msg, reply_markup=botoes_iniciais())

    ultimo_sinal_timestamp = agora().timestamp()

# ---------- CALLBACK ----------
async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global sequencia
    global wins_azul, wins_vermelho, wins_empate
    global wins_gale_azul, wins_gale_vermelho, wins_gale_empate
    global loss_azul, loss_vermelho, loss_empate, loss_gale

    q = update.callback_query
    await q.answer()

    if q.data == "win_azul":
        atualizar_historico("🔵")
        wins_azul += 1
        sequencia += 1
        await q.message.reply_text(f"✅ VITÓRIA AZUL\n🔥 {sequencia} seguidas")

    elif q.data == "win_vermelho":
        atualizar_historico("🔴")
        wins_vermelho += 1
        sequencia += 1
        await q.message.reply_text(f"✅ VITÓRIA VERMELHO\n🔥 {sequencia} seguidas")

    elif q.data == "empate":
        wins_empate += 1
        sequencia += 1
        await q.message.reply_text(f"🟡 EMPATE\n🔥 {sequencia} seguidas")

    elif q.data in ["loss_azul","loss_vermelho"]:
        sequencia = 0
        await q.message.reply_text("❌ DERROTA")

    elif q.data == "gale":
        await q.message.reply_text("⚠️ GALE 1", reply_markup=botoes_gale())

    elif "win_gale" in q.data:
        sequencia += 1
        await q.message.reply_text(f"🔥 WIN GALE\n🔥 {sequencia} seguidas")

    elif q.data == "loss_gale":
        loss_gale += 1
        sequencia = 0
        await q.message.reply_text("❌ DERROTA FINAL")

# ---------- SCHEDULER ----------
async def scheduler(context):
    global ultimo_sinal_timestamp

    dentro_free, _ = dentro_horario(FREE_HORAS)
    dentro_vip, _ = dentro_horario(VIP_HORAS)

    agora_ts = agora().timestamp()

    if agora_ts - ultimo_sinal_timestamp < intervalo_sinal:
        return

    if dentro_free:
        await enviar_sinal(context, CANAL_FREE)
    elif dentro_vip:
        await enviar_sinal(context, CANAL_VIP)

# ---------- MAIN ----------
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CallbackQueryHandler(callback))

    app.job_queue.run_repeating(scheduler, interval=5, first=5)

    print("🔥 BOT COM TIMING FIXO ATIVO")

    app.run_polling()

if __name__ == "__main__":
    main()
