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
ultimo_estado_horario = False

ultimo_sinal_tempo = None
ultimo_aviso_tempo = None
ultimo_vip_tempo = None

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
    return any(i <= h < f for i,f in lista)

def dentro_de_qualquer_horario():
    return dentro_horario(FREE_HORAS) or dentro_horario(VIP_HORAS)

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

    # VITÓRIAS NORMAIS
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

    # DERROTAS NORMAIS
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

    # GALE
    elif q.data == "gale":
        em_gale = True
        await q.message.reply_text("⚠️ FAZER GALE 1", reply_markup=botoes_gale())

    elif q.data == "win_gale_azul":
        wins_gale_azul += 1
        sequencia += 1
        await q.message.reply_text(f"✅ VITÓRIA AZUL (GALE)\n🔥 VITÓRIAS SEGUIDAS: {sequencia}")
        sinal_ativo = False

    elif q.data == "win_gale_vermelho":
        wins_gale_vermelho += 1
        sequencia += 1
        await q.message.reply_text(f"✅ VITÓRIA VERMELHO (GALE)\n🔥 VITÓRIAS SEGUIDAS: {sequencia}")
        sinal_ativo = False

    elif q.data == "win_gale_empate":
        wins_gale_empate += 1
        sequencia += 1
        await q.message.reply_text(f"🟡 VITÓRIA NO EMPATE (GALE)\n🔥 VITÓRIAS SEGUIDAS: {sequencia}")
        sinal_ativo = False

    elif q.data == "loss_gale":
        loss_gale += 1
        sequencia = 0
        await q.message.reply_text("❌ DERROTA FINAL")
        sinal_ativo = False

# ---------- RELATÓRIO ----------
def gerar_relatorio():
    total_wins = (wins_azul + wins_vermelho + wins_empate +
                  wins_gale_azul + wins_gale_vermelho + wins_gale_empate)

    total_loss = loss_azul + loss_vermelho + loss_empate + loss_gale
    total = total_wins + total_loss

    if total == 0:
        return "Sem dados hoje."

    assertividade = int((total_wins / total) * 100)

    return f"""📊 SINAIS DO DIA FINALIZADOS

🔵 Vitórias Azul: {wins_azul}
🔴 Vitórias Vermelho: {wins_vermelho}
🟡 Vitórias Empate: {wins_empate}

🔥 GALE 1:
🔵 Azul: {wins_gale_azul}
🟡 Empate: {wins_gale_empate}
🔴 Vermelho: {wins_gale_vermelho}

❌ DERROTAS:
🔵 Azul: {loss_azul}
🔴 Vermelho: {loss_vermelho}
🟡 Empate: {loss_empate}
⚠️ Após Gale: {loss_gale}

📈 Assertividade: {assertividade}%

🌙 Boa noite a todos
Amanhã estaremos de volta com mais sinais
"""

# ---------- JOBS ----------
async def relatorio_free(context):
    await context.bot.send_message(chat_id=CANAL_FREE, text=gerar_relatorio())

async def relatorio_vip(context):
    await context.bot.send_message(chat_id=CANAL_VIP, text=gerar_relatorio())

# ---------- SCHEDULER ----------
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

# ---------- MAIN ----------
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CallbackQueryHandler(callback))

    app.job_queue.run_repeating(scheduler, interval=240, first=5)

    app.job_queue.run_daily(relatorio_free, time=time(22,10))
    app.job_queue.run_daily(relatorio_vip, time=time(23,10))

    print("🔥 BOT PROFISSIONAL ATIVO")

    app.run_polling()

if __name__ == "__main__":
    main()
