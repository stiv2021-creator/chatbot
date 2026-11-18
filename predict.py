# predict.py - Versión para pysentimiento 0.7.3
import re
from pysentimiento import create_analyzer

# ─── Modelos preentrenados ─────────────────────────

print("🔄 Cargando modelos de pysentimiento...")
emotion_analyzer = create_analyzer(task="emotion", lang="es")
hate_analyzer = create_analyzer(task="hate_speech", lang="es")
print("✅ Modelos cargados correctamente")

# ─── Intención (reglas mejoradas) ─────────────────────

def contiene(texto, frases):
    """True si alguna frase aparece como palabra/frase completa en el texto."""
    return any(re.search(r"(?<!\w)" + re.escape(f) + r"(?!\w)", texto) for f in frases)

NEGACIONES = {"no", "nunca", "jamás", "jamas", "tampoco", "ni"}

def _coincidencias(texto, frase):
    """Posiciones de la frase; descarta 'te quiero' + verbo en infinitivo ('te quiero molestar')."""
    for m in re.finditer(r"(?<!\w)" + re.escape(frase) + r"(?!\w)", texto):
        despues = texto[m.end():].split()[:1]
        if frase == "te quiero" and despues and re.fullmatch(r"\w+(ar|er|ir)", despues[0]):
            continue
        negada = bool(NEGACIONES & set(texto[:m.start()].split()[-2:]))
        yield negada

def contiene_sin_negar(texto, frases):
    """La frase aparece sin una negación justo antes ('te quiero' sí, 'no te quiero' no)."""
    return any(not neg for f in frases for neg in _coincidencias(texto, f))

def contiene_negado(texto, frases):
    """La frase aparece negada ('no te quiero', 'jamás te quiero volver a ver')."""
    return any(neg for f in frases for neg in _coincidencias(texto, f))

AFECTO = ["te quiero", "te amo", "me gustas", "te extraño", "te necesito", "te adoro", "te quiero mucho", "quiero verte", "te quiero ver"]
AFECTO_NEGABLE = AFECTO + ["te quiero volver a ver", "quiero volver a verte", "te quiero ver", "quiero verte",
                           "quiero saber nada de ti", "quiero hablar contigo"]

def detectar_intencion(texto):
    texto = texto.lower()
    
    # Agresión
    if contiene(texto, ["odio", "te odio", "estúpido", "estúpida", "idiota", "imbécil", "imbecil", "mierda", "qué asco", "que asco", "inútil", "inutil", "tonto", "tonta", "pendejo", "pendeja", "malparido", "malparida", "gonorrea", "hijueputa", "perra", "zorra", "basura", "asqueroso", "asquerosa", "cállate", "callate"]):
        return "agresion"
    
    # Ruptura / rechazo
    elif contiene(texto, ["terminar", "terminemos", "dejemos esto", "no quiero seguir", "se acabó", "acabó", "hasta aquí",
                        "se terminó", "no te quiero volver a ver", "no quiero volver a verte", "no te quiero ver",
                        "no me busques", "no me escribas", "no me vuelvas a escribir", "olvídame", "olvidame",
                        "déjame en paz", "dejame en paz", "aléjate", "alejate",
                        "nunca más", "nunca mas", "adiós para siempre", "no quiero saber nada de ti",
                        "te voy a bloquear", "te bloqueé", "lo nuestro terminó"]) or contiene_negado(texto, AFECTO_NEGABLE):
        return "ruptura"
    
    # Afecto positivo
    elif contiene_sin_negar(texto, AFECTO):
        return "afecto"
    
    # Inseguridad
    elif contiene(texto, ["todavía me quieres", "aún me quieres", "me sigues queriendo", "me vas a dejar", "soy suficiente", "no soy suficiente", "te aburrí", "ya no te gusto"]):
        return "inseguridad"
    
    # Reclamos
    elif contiene(texto, ["por qué no respondes", "me ignoras", "no contestas", "por qué tardas", "por qué demoras", "no me escribes"]):
        return "reclamo"
    
    # Celos
    elif contiene(texto, ["con quién", "quién es", "te veo con", "andabas con", "quién te escribió", "quién te habla"]):
        return "celos"
    
    # Manipulación
    elif contiene(texto, ["si me quisieras", "deberías", "nunca haces", "siempre igual", "como siempre", "si realmente me quisieras"]):
        return "manipulacion"
    
    # Control
    elif contiene(texto, ["dónde estás", "qué haces", "con quién hablas", "dime la verdad", "ubicación", "envía ubicación"]):
        return "control"
    
    # Desinterés
    elif contiene(texto, ["ok", "vale", "ah", "ya", "como digas", "da igual", "me da igual", "jaja", "jeje", "ok ok"]):
        return "desinteres"
    
    # Curiosidad
    elif contiene(texto, ["qué tal", "cómo estás", "qué haces", "cómo te va", "en qué andas", "qué cuentas"]):
        return "curiosidad"
    
    # Tristeza
    elif contiene(texto, ["triste", "deprimido", "mal", "solo", "soledad", "llorar", "me siento mal"]):
        return "tristeza"
    
    else:
        return "normal"

# ─── Ghosting ─────────────────────────────────────────

def calcular_ghosting(texto, intencion, emocion):
    score = 0
    texto = texto.lower()
    
    # Mensajes muy cortos
    if len(texto) <= 5:
        score += 35
    
    # Respuesta de una palabra
    if len(texto.split()) == 1:
        score += 25
    
    # Palabras que indican desinterés
    if contiene(texto, ["ok", "vale", "ah", "ya", "luego", "ocupado", "ahora no", "después", "mañana", "ahora no puedo"]):
        score += 30
    
    # Intención relacionada
    if intencion == "desinteres":
        score += 35
    elif intencion == "reclamo":
        score += 15
    elif intencion == "afecto":
        score -= 25
    
    # Emoción negativa
    if emocion in ["sadness", "anger", "fear", "disgust"]:
        score += 10
    elif emocion in ["joy", "surprise"]:
        score -= 15
    
    return max(0, min(score, 95))

# ─── Calcular riesgo ───────────────────────────────────

def es_toxico(hate_result):
    etiquetas = hate_result.output
    if isinstance(etiquetas, str):
        etiquetas = [etiquetas]
    return "hateful" in etiquetas or "aggressive" in etiquetas

def calcular_riesgo(hate_result, intencion, emocion):
    # Verificar si hay hate_speech
    if es_toxico(hate_result) or intencion == "agresion":
        return "🔴 Alto"
    elif intencion in ["celos", "reclamo", "ruptura", "manipulacion", "agresion"]:
        return "🟡 Medio"
    elif emocion in ["anger", "disgust"]:
        return "🟡 Medio"
    else:
        return "🟢 Bajo"

# ─── Mapear emociones ───────────────────────────────────

def mapear_emocion(emocion_raw):
    emocion_map = {
        'joy': 'positivo',
        'sadness': 'tristeza',
        'anger': 'enojo',
        'surprise': 'sorpresa',
        'disgust': 'disgusto',
        'fear': 'miedo',
        'neutral': 'neutral',
        'others': 'neutral'
    }
    return emocion_map.get(emocion_raw, 'neutral')

# ─── Función principal ─────────────────────────────────

def analizar_texto(texto):
    try:
        # 🔥 MODELOS IA con pysentimiento
        emocion_pred = emotion_analyzer.predict(texto)
        hate_pred = hate_analyzer.predict(texto)
        
        # Obtener emoción principal
        emocion_raw = emocion_pred.output
        emocion = mapear_emocion(emocion_raw)
        
        # Toxicidad (basada en hate_speech)
        # Intención (reglas)
        intencion = detectar_intencion(texto)
        
        # Toxicidad: el modelo detecta discurso de odio (contra grupos);
        # los insultos personales se detectan con la intención "agresion"
        toxicidad = "si" if es_toxico(hate_pred) or intencion == "agresion" else "no"
        
        # Ghosting
        ghosting = calcular_ghosting(texto, intencion, emocion_raw)
        
        # Riesgo
        riesgo = calcular_riesgo(hate_pred, intencion, emocion_raw)
        
        # Confianza
        confianza = max(emocion_pred.probas.values())
        
        return emocion, toxicidad, ghosting, riesgo, intencion, int(confianza * 100)
    
    except Exception as e:
        print(f"Error en analizar_texto: {e}")
        return "neutral", "no", 0, "🟢 Bajo", "normal", 50