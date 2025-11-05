"""
Configuración principal del asistente de voz.
"""
import os
from pathlib import Path

# Directorios base
BASE_DIR = Path(__file__).parent.parent
MODEL_DIR = BASE_DIR / "models/vosk"
PLUGINS_DIR = BASE_DIR / "plugins"
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"

# Configuración de audio
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SIZE = 1024
VAD_AGGRESSIVENESS = 3  # Nivel de agresividad del VAD (0-3)

# Idiomas soportados
DEFAULT_LANGUAGE = "es"
LANGUAGES = {
    "es": {
        "model": "vosk-model-small-es-0.42",
        "wake_words": ["autogestión", "agp", "asistente", "oye"],
        "responses": {
            "welcome": ["¿En qué puedo ayudarte?", "¿Sí, dime?", "¿Neitas algo?"],
            "unknown": "No entendí ese comando. ¿Podrías repetirlo?",
            "error": "Lo siento, ha ocurrido un error al procesar tu solicitud",
            "goodbye": ["Hasta luego", "¡Que tengas un buen día!", "¡Hasta pronto!"]
        }
    },
    "en": {
        "model": "vosk-model-small-en-us-0.15",
        "wake_words": ["hey assistant", "computer", "wake up"],
        "responses": {
            "welcome": ["How can I help you?", "Yes?", "What can I do for you?"],
            "unknown": "I didn't understand that. Could you repeat?",
            "error": "Sorry, an error occurred while processing your request",
            "goodbye": ["Goodbye", "Have a nice day!", "See you later!"]
        }
    }
}

# Configuración de plugins
DEFAULT_PLUGINS = [
    "time",
    "weather",
    "system"
]

# Configuración de registro de logs
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = LOG_DIR / "assistant.log"

# Crear directorios necesarios
for directory in [MODEL_DIR, PLUGINS_DIR, DATA_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
