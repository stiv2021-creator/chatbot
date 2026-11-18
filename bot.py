import os
import random
import asyncio
from collections import Counter
from pathlib import Path
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from predict import analizar_texto

# ─── Configuración ──────────────────────────────────────

def cargar_env(ruta=Path(__file__).with_name(".env")):
    """Lee un archivo .env sencillo (CLAVE=valor) sin dependencias extra."""
    if not ruta.exists():
        return
    for linea in ruta.read_text(encoding="utf-8-sig", errors="ignore").splitlines():
        linea = linea.strip().strip('"').strip("'").strip()
        if linea and not linea.startswith("#") and "=" in linea:
            clave, valor = linea.split("=", 1)
            os.environ.setdefault(clave.strip(), valor.strip().strip('"').strip("'"))

cargar_env()
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    print("❌ ERROR: TELEGRAM_TOKEN no configurado")
    print("📌 Crea un archivo .env junto a bot.py con esta línea:")
    print("   TELEGRAM_TOKEN=tu_token_aqui")
    raise SystemExit(1)

# ─── Datos ──────────────────────────────────────────────

# INTERPRETACIONES: Qué significa el mensaje que te enviaron
INTERPRETACIONES = {
    "reclamo": [
        "📢 La persona se siente ignorada y reclama tu atención.",
        "😤 Hay frustración porque esperaba una respuesta y no llegó.",
        "💢 Percibe que la estás descuidando o ignorando.",
    ],
    "celos": [
        "😒 Siente inseguridad y teme que haya un tercero.",
        "🔍 Necesita confirmar que sigue siendo importante para ti.",
        "🤨 Desconfía de tus acciones o amistades.",
    ],
    "agresion": [
        "⚠️ Está muy enojado y busca herir o provocar.",
        "🔥 El conflicto puede escalar si respondes de forma similar.",
        "💥 Hay agresividad que debes manejar con cuidado.",
    ],
    "tristeza": [
        "😢 Está pasando por un momento difícil o de dolor.",
        "🫂 Necesita apoyo emocional y contención.",
        "💔 Hay vulnerabilidad, no lo ignores.",
    ],
    "manipulacion": [
        "🎭 Está usando culpa o condiciones para obtener lo que quiere.",
        "⛓️ Quiere presionarte emocionalmente para que actúes.",
        "⚠️ Ten cuidado con responder desde la culpa.",
    ],
    "control": [
        "🔒 Quiere saber todo lo que haces y con quién.",
        "👁️ Hay una necesidad excesiva de controlarte.",
        "📱 No confía plenamente en ti.",
    ],
    "ruptura": [
        "💔 Está considerando seriamente terminar la relación.",
        "😩 Hay agotamiento emocional acumulado.",
        "🚪 Quiere distancia o poner un punto final.",
    ],
    "desinteres": [
        "😐 No muestra interés en seguir la conversación.",
        "❄️ Hay distancia emocional o está ocupado.",
        "📉 Probablemente no quiere profundizar.",
    ],
    "inseguridad": [
        "😟 Tiene dudas sobre la relación o sobre sí mismo.",
        "🤔 Necesita reafirmación y seguridad.",
        "🌀 Busca calmar su ansiedad con respuestas claras.",
    ],
    "afecto": [
        "💕 Está expresando cariño y buenos sentimientos.",
        "🤗 Quiere acercarse y fortalecer el vínculo.",
        "🌸 Hay conexión emocional positiva.",
    ],
    "curiosidad": [
        "🤔 Tiene interés genuino en ti y tu vida.",
        "💬 Quiere iniciar o mantener una conversación.",
        "🔍 Busca conocer más sobre ti.",
    ],
    "normal": [
        "💬 Es una conversación cotidiana sin carga emocional.",
        "✅ No hay señales de conflicto ni urgencia.",
        "📝 Todo fluye con normalidad.",
    ],
}

# SUGERENCIAS: Cómo responder al mensaje (para TI)
SUGERENCIAS = {
    "reclamo": [
        "🗣️ Responde: 'Entiendo que te sientes ignorado, no fue mi intención. Hablemos.'",
        "⏸️ Reconoce su molestia antes de dar explicaciones: 'Tienes razón, no respondí rápido.'",
        "🤝 Pregunta: '¿Qué puedo hacer para que no te sientas así?'",
    ],
    "celos": [
        "🧠 Responde con calma: 'No hay nadie más, pero entiendo tu inseguridad.'",
        "💬 Valida su emoción: 'Veo que esto te preocupa, hablemos sin pelear.'",
        "🔐 Reafirma: 'Eres importante para mí. ¿Podemos hablar de esto tranquilos?'",
    ],
    "agresion": [
        "🌬️ No respondas con agresión. Di: 'Esto se está poniendo feo, hablemos más tarde.'",
        "🚫 Establece límite: 'No voy a responder si me hablas así.'",
        "⏰ Tómate un tiempo: 'Mejor hablamos cuando estemos más calmados.'",
    ],
    "tristeza": [
        "👥 Responde: 'Estoy aquí para ti. ¿Quieres hablar de lo que pasa?'",
        "💬 Muestra apoyo: 'Lamento que te sientas así, cuentas conmigo.'",
        "🤗 Ofrece compañía: '¿Necesitas desahogarte o prefieres distraerte?'",
    ],
    "manipulacion": [
        "🚩 No cedas por culpa. Di: 'No me gusta que me condiciones así.'",
        "🗣️ Marca límite: 'Si me quieres pedir algo, hazlo sin chantajes.'",
        "⚖️ Responde neutro: 'Te escucho, pero no voy a reaccionar desde la culpa.'",
    ],
    "control": [
        "🤝 Responde: 'Confío en ti y espero que tú confíes en mí.'",
        "📱 Marca espacio: 'Está bien que quieras saber, pero también necesito mi espacio.'",
        "🧘 Tranquiliza: 'No pasa nada, pero no puedo responder todo el tiempo.'",
    ],
    "ruptura": [
        "💬 Responde: 'Hablemos esto en persona, es importante.'",
        "🤔 Pide tiempo: 'No tomemos decisiones en caliente. Hablemos mañana.'",
        "🕊️ Si es firme: 'Lo respeto si es tu decisión, pero me duele.'",
    ],
    "desinteres": [
        "🧐 Pregunta: '¿Estás bien? Parece que no tienes ganas de hablar.'",
        "💬 Dale espacio: 'Cuando quieras hablar, aquí estoy.'",
        "⏸️ No insistas: 'Ok, hablamos cuando tengas tiempo.'",
    ],
    "inseguridad": [
        "🔍 Responde: 'Estoy contigo, no tienes nada que temer.'",
        "💬 Tranquiliza: 'Si algo te preocupa, pregúntame sin miedo.'",
        "📖 Reafirma: 'Me importas y no tengo nada que ocultar.'",
    ],
    "afecto": [
        "🌸 Corresponde: 'Yo también te quiero mucho ❤️'",
        "💌 Agradece: 'Qué bonito mensaje, gracias por tus palabras.'",
        "🎁 Sorprende: 'Me hiciste el día, te quiero igual.'",
    ],
    "curiosidad": [
        "🔍 Responde con entusiasmo: 'Todo bien, ¿y tú? Cuéntame.'",
        "💬 Aprovecha: 'Justo pensaba en ti. ¿Qué has hecho?'",
        "🌟 Sigue la conversación: 'Me alegra que preguntes, te cuento...'",
    ],
    "normal": [
        "👍 Responde con naturalidad: 'Todo bien, ¿y tú?'",
        "💬 Sigue la conversación: 'Qué bueno, seguimos hablando.'",
        "🌟 Mantén el tono: 'Genial, cualquier cosa me dices.'",
    ],
}

EMOJIS = {
    "reclamo": "😔",
    "celos": "😒",
    "agresion": "⚠️",
    "tristeza": "😢",
    "manipulacion": "🚩",
    "control": "🔒",
    "ruptura": "💔",
    "desinteres": "😶",
    "inseguridad": "😟",
    "afecto": "💕",
    "curiosidad": "🤔",
    "normal": "💬",
}

EMOJIS_EMOCION = {
    "positivo": "😊",
    "tristeza": "😢",
    "enojo": "😠",
    "sorpresa": "😲",
    "disgusto": "😖",
    "miedo": "😨",
    "neutral": "😐",
}

# ESTRATEGIAS: cómo conviene manejar la conversación según el riesgo
ESTRATEGIAS = {
    "proteger": {
        "titulo": "🛑 Protégete: pon un límite o corta la conversación",
        "descripcion": "El mensaje es tóxico o agresivo. No te conviene seguir esta conversación ahora.",
        "respuestas": [
            "No voy a seguir hablando si me tratas así. Hablamos cuando haya respeto.",
            "Esto no me hace bien. Voy a tomar distancia por ahora.",
            "Prefiero no responder a esto. Cuando podamos hablar con calma, aquí estaré.",
        ],
        "consejo": "No respondas en caliente ni con insultos. Si se repite, silencia o bloquea el chat y guarda capturas.",
    },
    "precaucion": {
        "titulo": "⚠️ Precaución: responde corto y baja la tensión",
        "descripcion": "Hay tensión. Responde con calma, sin justificarte de más y sin alargar la discusión.",
        "respuestas": [
            "Entiendo que estés molesto/a. Lo hablamos con calma más tarde.",
            "No quiero discutir por chat. ¿Lo hablamos en persona?",
            "Te leo. Dame un rato y te respondo con calma.",
        ],
        "consejo": "Un solo mensaje corto y tranquilo basta. Evita los reproches y no sigas el intercambio si sube el tono.",
    },
    "espacio": {
        "titulo": "⏸️ Dale espacio: no insistas",
        "descripcion": "Muestra poco interés. Insistir puede alejar más a la otra persona.",
        "respuestas": [
            "Va, hablamos luego 🙂",
            "Todo bien, cuando tengas tiempo me cuentas.",
            "Ok, cualquier cosa me escribes.",
        ],
        "consejo": "Espera a que la otra persona retome la conversación. No envíes varios mensajes seguidos.",
    },
    "continuar": {
        "titulo": "💬 Continúa: la conversación va bien",
        "descripcion": "No hay señales de riesgo. Puedes alargarla con una pregunta abierta.",
        "respuestas": [],  # usa la sugerencia de la intención + una pregunta abierta
        "consejo": "Las preguntas abiertas (que no se responden con sí o no) mantienen viva la conversación.",
    },
}

PREGUNTAS_ABIERTAS = [
    "¿Y a ti cómo te fue hoy?",
    "Cuéntame más, ¿cómo fue eso?",
    "¿Qué planes tienes para esta semana?",
    "¿Qué es lo que más te gustó de eso?",
    "¿Y qué piensas hacer ahora?",
]

INTENCIONES_TENSAS = {"reclamo", "celos", "manipulacion", "control", "ruptura"}

def decidir_estrategia(toxicidad, riesgo, intencion, ghosting, historial):
    """Elige cómo manejar la conversación según el mensaje actual y los anteriores."""
    recientes = historial[-5:]
    alertas_recientes = sum(1 for h in recientes if h["toxicidad"] == "si" or "Alto" in h["riesgo"])

    if toxicidad == "si" or "Alto" in riesgo or intencion == "agresion" or alertas_recientes >= 2:
        return "proteger"
    if "Medio" in riesgo or intencion in INTENCIONES_TENSAS:
        return "precaucion"
    if ghosting >= 60 or intencion == "desinteres":
        return "espacio"
    return "continuar"

def sugerir_respuesta(estrategia, intencion):
    if estrategia == "continuar":
        return f"{obtener_texto(SUGERENCIAS, intencion)}\n➕ Para seguir hablando: «{random.choice(PREGUNTAS_ABIERTAS)}»"
    if estrategia == "precaucion":
        # La sugerencia de la intención ya es conciliadora; se suma una opción breve
        return f"{obtener_texto(SUGERENCIAS, intencion)}\n✂️ Versión corta: «{random.choice(ESTRATEGIAS['precaucion']['respuestas'])}»"
    return f"🗣️ «{random.choice(ESTRATEGIAS[estrategia]['respuestas'])}»"

# ─── Funciones auxiliares ───────────────────────────────

def construir_barra(valor: int) -> str:
    bloques = valor // 10
    return "█" * bloques + "░" * (10 - bloques)

def obtener_texto(diccionario, clave, default="normal"):
    return random.choice(diccionario.get(clave, diccionario[default]))

def formatear_respuesta(datos: dict) -> str:
    est = ESTRATEGIAS[datos["estrategia"]]
    texto = (
        f"{datos['emoji_principal']} *Análisis del mensaje que te enviaron*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{datos['emoji_emocion']} *Emoción detectada:* {datos['emocion']}\n"
        f"🚩 *Toxicidad:* {datos['toxicidad']}\n"
        f"🧠 *Intención:* {datos['intencion']}\n"
        f"💔 *Ghosting:* {datos['ghosting_bar']} {datos['ghosting']}%\n"
        f"🔥 *Riesgo:* {datos['riesgo']}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 *Qué significa:*\n{datos['interpretacion']}\n\n"
        f"🧭 *Estrategia:* {est['titulo']}\n{datos.get('motivo') or est['descripcion']}\n\n"
        f"💬 *Cómo responder:*\n{datos['sugerencia']}\n\n"
        f"🛡️ *Consejo:* {est['consejo']}"
    )
    if datos["estrategia"] == "proteger":
        texto += (
            "\n\n📞 Si te sientes en peligro, busca apoyo: Línea 123 (emergencias) "
            "o Línea 155 (orientación a mujeres víctimas de violencia, Colombia)."
        )
    return texto

# ─── Comandos ───────────────────────────────────────────

TEXTO_AYUDA = (
    "🤖 *Chat Analyzer Bot*\n\n"
    "Reenvíame o pega un mensaje que te enviaron y te digo:\n"
    "• la emoción y si es tóxico\n"
    "• la intención y el riesgo de conflicto\n"
    "• una estrategia: protegerte, bajar la tensión, dar espacio o seguir hablando\n"
    "• cómo podrías responder según esa estrategia\n\n"
    "*Comandos*\n"
    "/resumen – balance de los mensajes que has analizado\n"
    "/reiniciar – borra tu resumen\n"
    "/ayuda – muestra este mensaje"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(TEXTO_AYUDA, parse_mode="Markdown")

async def resumen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Balance de la conversación: cuántos mensajes, intenciones más comunes, % tóxico."""
    hist = context.user_data.get("historial", [])
    if not hist:
        await update.message.reply_text("📭 Aún no has analizado mensajes. ¡Envíame uno!")
        return
    total = len(hist)
    toxicos = sum(1 for h in hist if h["toxicidad"] == "si")
    altos = sum(1 for h in hist if "Alto" in h["riesgo"])
    ghost_prom = round(sum(h["ghosting"] for h in hist) / total)
    top = Counter(h["intencion"] for h in hist).most_common(5)
    protecciones = sum(1 for h in hist if h.get("estrategia") == "proteger")
    lineas_top = "\n".join(f"  {EMOJIS.get(i, '💬')} {i.capitalize()}: {n}" for i, n in top)

    pct_toxico = toxicos * 100 // total
    if pct_toxico >= 40 or altos >= 2 or protecciones >= 2:
        veredicto = "🚩 Hay muchas señales de conflicto. Considera hablarlo con calma o poner límites."
    elif pct_toxico > 0 or altos > 0 or protecciones > 0 or ghost_prom >= 50:
        veredicto = "🟡 Hay algunas alertas; presta atención a cómo evoluciona."
    else:
        veredicto = "🟢 En general la conversación se ve sana."

    await update.message.reply_text(
        f"📊 *Resumen de tus análisis*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📨 Mensajes analizados: {total}\n"
        f"🚩 Tóxicos: {toxicos} ({pct_toxico}%)\n"
        f"🔥 Riesgo alto: {altos}\n"
        f"💔 Ghosting promedio: {construir_barra(ghost_prom)} {ghost_prom}%\n"
        f"🛑 Veces que te recomendé protegerte: {protecciones}\n"
        f"🧠 Intenciones más frecuentes:\n{lineas_top}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{veredicto}",
        parse_mode="Markdown",
    )

async def reiniciar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["historial"] = []
    await update.message.reply_text("🧹 Resumen borrado. Empezamos de cero.")

# ─── Handler principal ──────────────────────────────────

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        texto = update.message.text
        await context.bot.send_chat_action(update.effective_chat.id, ChatAction.TYPING)

        # El modelo es lento: se ejecuta en otro hilo para no congelar el bot
        emocion, toxicidad, ghosting, riesgo, intencion, confianza = await asyncio.to_thread(analizar_texto, texto)

        historial = context.user_data.setdefault("historial", [])
        estrategia = decidir_estrategia(toxicidad, riesgo, intencion, ghosting, historial)
        historial.append({"intencion": intencion, "toxicidad": toxicidad, "ghosting": ghosting,
                          "riesgo": riesgo, "estrategia": estrategia})
        del historial[:-50]  # guarda solo los últimos 50
        
        datos = {
            "emoji_principal": EMOJIS.get(intencion, "💬"),
            "emoji_emocion": EMOJIS_EMOCION.get(emocion, "😐"),
            "emocion": emocion.capitalize(),
            "toxicidad": "🔴 Alta" if toxicidad == "si" else "🟢 Baja",
            "intencion": intencion.capitalize(),
            "ghosting": ghosting,
            "ghosting_bar": construir_barra(ghosting),
            "riesgo": riesgo,
            "interpretacion": obtener_texto(INTERPRETACIONES, intencion),
            "sugerencia": sugerir_respuesta(estrategia, intencion),
            "estrategia": estrategia,
            "motivo": (
                "Este mensaje parece tranquilo, pero vienen varios mensajes tóxicos seguidos. Mantén la distancia."
                if estrategia == "proteger" and toxicidad != "si" and "Alto" not in riesgo and intencion != "agresion"
                else None
            ),
        }
        
        respuesta = formatear_respuesta(datos)
        try:
            await update.message.reply_text(respuesta, parse_mode="Markdown")
        except Exception:
            # Si el Markdown falla por algún carácter, se envía como texto plano
            await update.message.reply_text(respuesta.replace("*", ""))

    except Exception as e:
        print(f"❌ Error: {e}")
        await update.message.reply_text("⚠️ Ocurrió un error al procesar el mensaje.")

# ─── Inicialización ─────────────────────────────────────

def main():
    print("🤖 Bot de análisis de mensajes activo...")
    print("📌 Analizo los mensajes que TE ENVÍAN y te digo cómo responder")
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ayuda", start))
    app.add_handler(CommandHandler("resumen", resumen))
    app.add_handler(CommandHandler("reiniciar", reiniciar))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    
    print("🟢 Bot corriendo... Esperando mensajes")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()