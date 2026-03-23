import random
import asyncio
from datetime import datetime, time, timedelta
import pytz
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

TOKEN = "8667107306:AAHsMiPG9oslWJ-z2_VNPtZvptsnn7o70k4"

CANAL_FREE = -1003731784397
CANAL_VIP = -1003770413249

FREE_HORAS = [(10,11),(14,15),(21,22)]
VIP_HORAS = [(9,10),(11,12),(15,16),(17,18),(20,21),(22,23)]

# ---------- CONFIG ----------
intervalo_sinal = 246

# ---------- ESTADO ----------
historico = []
sequencia = 0
base_timestamp = None
contador_sinais = 0

lock_envio = asyncio.Lock()

# ---------- CONTADORES ----------
wins = loss = 0

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
    return "🔵 PLAYER" if historico[-1] == "🔵" else "🔴 BANKER"

def atualizar_historico(cor):
    historico.append(cor)
    if len(historico) > 10:
        historico.pop(0)

# ---------- BOTÕES ----------
def botoes():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ AZUL", callback_data="win_azul"),
         InlineKeyboardButton("✅ VERMELHO", callback_data="win_vermelho")],
        [InlineKeyboardButton("❌ LOSS", callback_data="loss")],
        [InlineKeyboardButton("🟡 EMPATE", callback_data="empate")]
    ])

# ---------- SINAL ----------
async def enviar_sinal(context, canal):
    global base_timestamp, contador_sinais

    async with lock_envio:

        if base_timestamp is None:
            base_timestamp = agora().timestamp()
            contador_sinais = 0

        esperado = base_timestamp + (contador_sinais * intervalo_sinal)
        agora_ts = agora().timestamp()

        if agora_ts < esperado:
            return

        cor = analisar_jogada()

        await context.bot.send_message(
            chat_id=canal,
            text=f"📊 NOVA ENTRADA\n\n{cor}\n🟡 PROTEGER EMPATE",
            reply_markup=botoes()
        )

        contador_sinais += 1

# ---------- CALLBACK ----------
async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global sequencia, wins, loss

    q = update.callback_query
    await q.answer()

    if "win" in q.data:
        sequencia += 1
        wins += 1
        await q.message.reply_text(f"✅ WIN\n🔥 {sequencia} seguidas")

    elif q.data == "empate":
        sequencia += 1
        await q.message.reply_text(f"🟡 EMPATE\n🔥 {sequencia} seguidas")

    elif q.data == "loss":
        sequencia = 0
        loss += 1
        await q.message.reply_text("❌ LOSS")

# ---------- MENSAGENS AUTOMÁTICAS ----------
async def avisos(context):
    now = agora()
    h = now.hour
    m = now.minute

    for lista, canal in [(FREE_HORAS, CANAL_FREE), (VIP_HORAS, CANAL_VIP)]:
        for inicio, fim in lista:
            # aviso 5 min antes
            if h == inicio and m == 55:
                await context.bot.send_message(canal, "🚀 VAMOS INICIAR O CICLO - FIQUEM ATENTOS")

            # início
            if h == inicio and m == 0:
                await context.bot.send_message(canal, "🔥 SINAIS INICIADOS")

            # fim
            if h == fim and m == 0:
                await context.bot.send_message(canal, "🛑 SESSÃO ENCERRADA")

# ---------- RELATÓRIO ----------
async def relatorio(context):
    total = wins + loss
    if total == 0:
        return

    perc = int((wins / total) * 100)

    msg = f"""📊 RELATÓRIO DO DIA

✅ Wins: {wins}
❌ Loss: {loss}

📈 Assertividade: {perc}%"""

    await context.bot.send_message(CANAL_FREE, msg)
    await context.bot.send_message(CANAL_VIP, msg)

# ---------- SCHEDULER ----------
async def scheduler(context):
    dentro_free, _ = dentro_horario(FREE_HORAS)
    dentro_vip, _ = dentro_horario(VIP_HORAS)

    if dentro_free:
        await enviar_sinal(context, CANAL_FREE)
    elif dentro_vip:
        await enviar_sinal(context, CANAL_VIP)

    await avisos(context)

# ---------- MAIN ----------
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CallbackQueryHandler(callback))

    app.job_queue.run_repeating(scheduler, interval=1, first=1)

    app.job_queue.run_daily(relatorio, time=time(23, 0))

    print("🔥 BOT FINAL PROFISSIONAL ATIVO")

    app.run_polling()

if __name__ == "__main__":
    main()
