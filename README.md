Aquí tienes el `README.md` completo en formato Markdown listo para copiar y pegar:

```markdown
# 🤖 Chat Analyzer Bot

**Chat Analyzer Bot** es un bot de Telegram que utiliza Inteligencia Artificial y Procesamiento de Lenguaje Natural (NLP) para analizar mensajes de texto en español. El bot detecta emociones, toxicidad, intención comunicativa, nivel de ghosting y riesgo de conflicto, **ofreciendo sugerencias sobre cómo responder** a cada mensaje.

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Arquitectura del Proyecto](#-arquitectura-del-proyecto)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [Ejemplos de Mensajes](#-ejemplos-de-mensajes)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Posibles Mejoras](#-posibles-mejoras)
- [Licencia](#-licencia)
- [Contacto](#-contacto)

---

## ✨ Características

| Característica | Descripción |
|----------------|-------------|
| 🎭 **Análisis Emocional** | Detecta 7 emociones: positivo, tristeza, enojo, sorpresa, disgusto, miedo, neutral |
| 🚫 **Detección de Toxicidad** | Identifica lenguaje ofensivo, agresivo o dañino |
| 🧠 **Clasificación de Intención** | Reconoce 12 intenciones: afecto, reclamo, celos, agresión, ruptura, manipulación, control, desinterés, inseguridad, curiosidad, tristeza, normal |
| 💔 **Métrica de Ghosting** | Calcula probabilidad de desinterés o distanciamiento (0-95%) |
| 🔥 **Evaluación de Riesgo** | 3 niveles: 🔴 Alto, 🟡 Medio, 🟢 Bajo |
| 💬 **Sugerencias de Respuesta** | Te dice **cómo responder** al mensaje que recibiste |
| 📊 **Interfaz Amigable** | Respuestas formateadas con emojis y barras de progreso |

---

## 🛠️ Tecnologías Utilizadas

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **Python** | 3.11+ | Lenguaje principal |
| **pysentimiento** | 0.7.3 | NLP para español (emociones y hate speech) |
| **Transformers** | 4.6.1+ | Modelos BERT para análisis de texto |
| **PyTorch** | 2.0+ | Deep learning |
| **python-telegram-bot** | 21.6+ | Framework del bot |
| **scikit-learn** | - | Utilidades de ML |

---



## 📦 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/rubisabel00/machine-learning-Bot-telegram.git
cd chat-analyzer-bot
```

### 2. Crear entorno virtual (recomendado)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

**`requirements.txt`:**
```txt
python-telegram-bot>=21.6
pysentimiento>=0.7.3
transformers>=4.30
torch>=2.0.0
```

---

## ⚙️ Configuración

### 1. Crear un bot en Telegram

1. Abre Telegram y busca [@BotFather](https://t.me/BotFather)
2. Envía el comando: `/newbot`
3. Elige un nombre para tu bot (ej: `Chat Analyzer Bot`)
4. Elige un username (ej: `chat_analyzer_bot`)
5. **Guarda el token** que te entregue BotFather

### 2. Configurar el token

Lo más sencillo: copia `.env.example` como `.env` y escribe tu token:

```
TELEGRAM_TOKEN=tu_token_aqui
```

(`.env` está en `.gitignore`, así que el token no se sube a GitHub.)
También puedes usar una variable de entorno:

**Windows (PowerShell):**
```powershell
$env:TELEGRAM_TOKEN="tu_token_aqui"
```

**Windows (CMD):**
```cmd
set TELEGRAM_TOKEN=tu_token_aqui
```

**Linux/Mac:**
```bash
export TELEGRAM_TOKEN="tu_token_aqui"
```

### 3. Ejecutar el bot

```bash
python bot.py
```

Verás algo como:
```
🔄 Cargando modelos de pysentimiento...
✅ Modelos cargados correctamente
🤖 Bot de análisis de mensajes activo...
📝 Token configurado: ✅ Sí
🟢 Bot corriendo... Esperando mensajes
```

---

## 🎯 Uso

1. Abre Telegram y busca tu bot por su username
2. Envía cualquier mensaje de texto al bot
3. El bot te responderá con un análisis completo del mensaje
4. **El análisis incluye sugerencias de cómo responder**

### Comandos

| Comando | Qué hace |
|---------|----------|
| `/start` o `/ayuda` | Explica cómo usar el bot |
| `/resumen` | Balance de los mensajes que has analizado: % tóxicos, riesgo alto, ghosting promedio, intenciones más frecuentes y un veredicto |
| `/reiniciar` | Borra tu resumen |

---

## 📝 Ejemplos de Mensajes

| Mensaje que te envían | Emoción | Intención | Toxicidad | Riesgo | Sugerencia de respuesta |
|-----------------------|---------|-----------|-----------|--------|------------------------|
| "te quiero mucho" | Positivo | Afecto | Baja | Bajo | "Yo también te quiero mucho ❤️" |
| "por qué no me respondes" | Tristeza | Reclamo | Baja | Medio | "Entiendo que te sientes ignorado, no fue mi intención" |
| "con quién estabas" | Enojo | Celos | Baja | Medio | "No hay nadie más, pero entiendo tu inseguridad" |
| "eres un idiota" | Enojo | Agresión | Alta | Alto | "Esto se está poniendo feo, hablemos más tarde" |
| "ok" | Neutral | Desinterés | Baja | Bajo | "¿Estás bien? Parece que no tienes ganas de hablar" |
| "cómo estás" | Positivo | Curiosidad | Baja | Bajo | "Todo bien, ¿y tú? Cuéntame" |
| "quiero terminar" | Tristeza | Ruptura | Baja | Medio | "Hablemos esto en persona, es importante" |
| "estoy triste" | Tristeza | Tristeza | Baja | Bajo | "Estoy aquí para ti. ¿Quieres hablar de lo que pasa?" |

### Ejemplo de respuesta del bot:

```
💕 *Análisis del mensaje que te enviaron*
━━━━━━━━━━━━━━━━━━━━━━━━━━
😊 *Emoción detectada:* Positivo
🚩 *Toxicidad:* 🟢 Baja
🧠 *Intención:* Afecto
💔 *Ghosting:* ░░░░░░░░░░ 0%
🔥 *Riesgo:* 🟢 Bajo
━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 *Qué significa:*
Está expresando cariño y buenos sentimientos. Quiere acercarse y fortalecer el vínculo.

💬 *Cómo responder:*
🌸 Corresponde: 'Yo también te quiero mucho ❤️'
```

---

## 📁 Estructura del Proyecto

```
chat-analyzer-bot/
│
├── bot.py                 # Código principal del bot de Telegram
├── predict.py             # Motor de análisis con IA y reglas
├── requirements.txt       # Dependencias del proyecto
├── README.md              # Documentación
│
└── models/                # (Opcional) Modelos entrenados personalizados
    ├── modelo_emociones.pkl
    ├── modelo_toxicidad.pkl
    ├── modelo_intencion.pkl
    └── vectorizer.pkl
```

---

## 🔮 Posibles Mejoras

- [ ] **Modelo personalizado**: Entrenar con dataset propio para mayor precisión
- [ ] **Soporte multimedia**: Análisis de imágenes, audios y documentos
- [ ] **Dashboard web**: Visualización de métricas y estadísticas
- [ ] **API REST**: Exponer funcionalidades como servicio web
- [ ] **Base de datos**: Almacenamiento anonimizado para análisis longitudinal
- [ ] **Dockerización**: Contenedor para despliegue en la nube
- [ ] **Soporte multi-idioma**: Ampliar a inglés, portugués, etc.
- [ ] **Historial de conversaciones**: Analizar evolución de emociones en el tiempo

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea tu rama de features (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

## 📧 Contacto

- **Autor**: [Tu nombre]
- **Email**: [tu@email.com]
- **GitHub**: [github.com/tuusuario](https://github.com/tuusuario)

---

## ⚠️ Notas de Seguridad

- **Nunca** compartas tu token de Telegram públicamente
- **No subas** el token a repositorios públicos
- Usa siempre variables de entorno para información sensible
- Si tu token se expone, revócalo inmediatamente con [@BotFather](https://t.me/BotFather)

---

## 🙏 Agradecimientos

- [pysentimiento](https://github.com/pysentimiento/pysentimiento) - Librería de NLP para español
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Framework del bot
- [Hugging Face](https://huggingface.co/) - Modelos preentrenados

---

## 📊 Estado del Proyecto

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.11+-green)
![License](https://img.shields.io/badge/license-MIT-green)

---

**¡Disfruta analizando y mejorando tus conversaciones! 🚀**
```
