# Gemini - Asistente de Voz Inteligente

## Descripción General
Gemini es un asistente de voz avanzado con reconocimiento de voz en tiempo real, procesamiento de comandos y un sistema modular de plugins. Diseñado para ser altamente personalizable y fácil de extender.

## Características Principales

### 🎙️ Reconocimiento de Voz
- Soporte para múltiples motores de reconocimiento (Vosk, Google Speech)
- Procesamiento en tiempo real
- Reducción de ruido y mejora de audio
- Soporte para múltiples idiomas

### 🧠 Procesamiento de Comandos
- Sistema de intenciones basado en IA
- Procesamiento de lenguaje natural
- Soporte para comandos personalizados
- Contexto de conversación

### 🔌 Sistema de Plugins
- Arquitectura modular
- Fácil creación de nuevos comandos
- Carga dinámica de plugins
- Aislamiento de funcionalidades

### 📊 Monitoreo y Auditoría
- Registro detallado de actividades
- Sistema de auditoría completo
- Generación de informes
- Seguimiento de rendimiento

## Requisitos del Sistema

### Mínimos
- Python 3.8+
- 4GB RAM
- 1GB de espacio en disco
- Micrófono

### Recomendados
- Python 3.10+
- 8GB RAM
- 2GB de espacio en disco
- Tarjeta de sonido compatible con ASIO

## Estructura del Proyecto

```text
gemini/
├── core/                 # Módulos principales
│   ├── audio/            # Procesamiento de audio
│   ├── nlp/              # Procesamiento de lenguaje natural
│   ├── plugins/          # Sistema de plugins
│   └── utils/            # Utilidades
├── plugins/              # Plugins del sistema
│   ├── system/           # Comandos del sistema
│   ├── web/              # Interfaz web
│   └── skills/           # Habilidades adicionales
├── config/               # Archivos de configuración
├── logs/                 # Archivos de registro
└── models/               # Modelos de IA
```

## Configuración

### Variables de Entorno

```env
# Configuración básica
GEMINI_LANGUAGE=es
GEMINI_DEBUG=false
GEMINI_LOG_LEVEL=INFO

# Motor de reconocimiento de voz
SPEECH_ENGINE=vosk
VOSK_MODEL_PATH=./models/vosk-model

# Configuración de audio
AUDIO_SAMPLE_RATE=16000
AUDIO_CHANNELS=1
AUDIO_CHUNK=1024

# Configuración de red
API_PORT=5000
API_HOST=0.0.0.0
```

## Uso Básico

### Iniciar el Asistente

```bash
python -m gemini
```

### Comandos Disponibles

| Comando | Descripción | Ejemplo |
|---------|-------------|----------|
| `ayuda` | Muestra la ayuda | "¿Qué puedes hacer?" |
| `hora` | Muestra la hora actual | "¿Qué hora es?" |
| `fecha` | Muestra la fecha actual | "¿Qué día es hoy?" |
| `apagar` | Apaga el sistema | "Apágate" |
| `buscar` | Realiza una búsqueda | "Busca información sobre Python" |

## Desarrollo

### Crear un Nuevo Plugin

1. Crea un nuevo archivo en `plugins/`
2. Define tu clase de plugin:

```python
from core.plugins import Plugin, command

class MiPlugin(Plugin):
    def __init__(self):
        super().__init__(
            name="mi_plugin",
            version="1.0.0",
            description="Descripción de mi plugin"
        )
    
    @command("mi_comando")
    def mi_metodo(self, text, context):
        """Descripción del comando"""
        return "Respuesta del comando"
```

### Pruebas

```bash
# Ejecutar pruebas unitarias
pytest tests/

# Ejecutar pruebas de cobertura
pytest --cov=gemini tests/
```

## Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## Contribución

Las contribuciones son bienvenidas. Por favor, lee [CONTRIBUTING.md](CONTRIBUTING.md) para más detalles.

## Créditos

- Equipo de desarrollo de Gemini
- [Vosk](https://alphacephei.com/vosk/) - Motor de reconocimiento de voz
- [PyAudio](https://pypi.org/project/PyAudio/) - Procesamiento de audio
