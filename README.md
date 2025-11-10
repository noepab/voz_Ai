# 🎙️ AGP - Asistente de Voz Inteligente

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/noepab/voz_Ai?style=social)](https://github.com/noepab/voz_Ai/stargazers)

Un asistente de voz en español con reconocimiento de voz avanzado, procesamiento de comandos y sistema de plugins. Desarrollado con Python y tecnologías de IA para ofrecer una experiencia de usuario fluida y personalizable.

<p align="center">
  <img src="https://img.shields.io/badge/status-activo-brightgreen" alt="Estado del proyecto">
  <img src="https://img.shields.io/github/last-commit/noepab/voz_Ai" alt="Último commit">
  <img src="https://img.shields.io/github/issues/noepab/voz_Ai" alt="Issues abiertos">
</p>

## ✨ Características principales

### 🎤 Reconocimiento de voz avanzado
- Procesamiento en tiempo real con Vosk
- Reducción de ruido y mejora de audio
- Soporte para múltiples idiomas
- Palabras de activación personalizables

### 🛠️ Funcionalidades principales
- Ejecución de comandos por voz
- Sistema de plugins modular
- Interfaz gráfica intuitiva
- Monitoreo de recursos del sistema

### 🚀 Características técnicas
- Arquitectura modular y escalable
- Procesamiento en segundo plano
- Sistema de logging avanzado
- Gestión eficiente de recursos

## 📋 Requisitos del sistema

### Hardware
- Procesador: Dual-core 2GHz o superior
- Memoria RAM: 4GB mínimo (8GB recomendado)
- Espacio en disco: 1GB libre
- Micrófono (con cancelación de ruido recomendada)

### Software
- Python 3.8 o superior
- Sistema operativo:
  - Windows 10/11
  - macOS 10.15+
  - Linux (Ubuntu 20.04+, Fedora 32+, etc.)
- Conexión a Internet (opcional, para ciertas funcionalidades)

## 🚀 Instalación rápida

### 1. Clonar el repositorio
```bash
git clone https://github.com/noepab/voz_Ai.git
cd voz_Ai
```

### 2. Configurar entorno virtual (recomendado)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Descargar modelo de voz
```bash
# Crear directorio para modelos
mkdir -p models

# Descargar modelo en español (versión pequeña)
curl -L https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip -o vosk-model-small-es-0.42.zip
unzip vosk-model-small-es-0.42.zip -d models/
mv models/vosk-model-small-es-0.42 models/vosk-model

# Alternativa: modelo más grande (mejor precisión pero más lento)
# curl -L https://alphacephei.com/vosk/models/vosk-model-es-0.42.zip -o vosk-model-es-0.42.zip
```

## 🏃 Ejecución

### Modo asistente de voz
```bash
python main.py
```

### Modo desarrollo (con logs detallados)
```bash
python -m main --debug
```

### Opciones disponibles
```bash
--debug     Modo depuración (más información en consola)
--no-gui    Ejecutar sin interfaz gráfica
--lang es   Establecer idioma (es/en)
```

## Uso

### Iniciar el asistente
```bash
python main.py
```

### Comandos básicos

- Di "agp" o "autogestión" para activar el asistente
- Pregunta la hora o la fecha
- Di "apágate" para cerrar el asistente

### Opciones de línea de comandos

```bash
--debug     Habilita el modo de depuración
--model     Ruta personalizada al modelo de voz
```

## Estructura del proyecto

```text
asistente-voz/
├── core/                 # Módulos principales
│   ├── __init__.py
│   ├── audio_processor.py  # Procesamiento de audio
│   ├── config.py          # Configuración
│   ├── plugin_manager.py  # Gestión de plugins
│   └── ...
├── plugins/              # Plugins del sistema
│   ├── system_plugin.py  # Comandos básicos
│   └── ...
├── static/               # Archivos estáticos
├── templates/            # Plantillas HTML
├── main.py              # Punto de entrada
└── requirements-updated.txt  # Dependencias
```

## Crear un plugin

1. Crea un nuevo archivo en la carpeta `plugins/` (ej: `mi_plugin.py`)
2. Define una clase que herede de `Plugin`:

   ```python
   from core.plugin_manager import Plugin
   
   class MiPlugin(Plugin):
       def __init__(self):
           super().__init__(
               name="mi_plugin",
               description="Descripción de mi plugin"
           )
   ```
    
    def get_commands(self):
        return {
            "hola": {
                "function": self.saludar,
                "description": "Saluda al usuario",
                "examples": ["di hola", "saluda"]
            }
        }
    
    def saludar(self):
        return "¡Hola! ¿Cómo estás?"

def setup():
    return MiPlugin()
```

## Contribuir

1. Haz un fork del proyecto
2. Crea una rama para tu característica (`git checkout -b feature/nueva-funcionalidad`)
3. Haz commit de tus cambios (`git commit -am 'Añade nueva funcionalidad'`)
4. Haz push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Créditos

- [Vosk](https://alphacephei.com/vosk/) - Motor de reconocimiento de voz
- [SoundDevice](https://python-sounddevice.readthedocs.io/) - Grabación de audio
- [Pyttsx3](https://pypi.org/project/pyttsx3/) - Síntesis de voz

---

Desarrollado con ❤️ por [Tu Nombre]
