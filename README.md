# Asistente de Voz Inteligente

Un asistente de voz en español con reconocimiento de voz avanzado, procesamiento de comandos y sistema de plugins.

## Características

- 🎤 Reconocimiento de voz en tiempo real con Vosk
- 🎧 Procesamiento de audio avanzado con reducción de ruido
- 🔌 Sistema de plugins para extender funcionalidades
- 🌍 Soporte para múltiples idiomas
- 🧠 Sistema de aprendizaje automático para mejorar el reconocimiento
- 🖥️ Interfaz web opcional para monitoreo y control

## Requisitos

- Python 3.8 o superior
- Sistema operativo: Windows/Linux/macOS
- Micrófono funcionando
- Conexión a Internet (solo para características que lo requieran)

## Instalación

1. Clona el repositorio:

   ```bash
   git clone https://github.com/tuusuario/asistente-voz.git
   cd asistente-voz
   ```

2. Crea un entorno virtual (recomendado):

   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instala las dependencias:

   ```bash
   pip install -r requirements-updated.txt
   ```

4. Descarga el modelo de voz en español de Vosk:

   ```bash
   mkdir -p models
   cd models
   wget https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip
   unzip vosk-model-small-es-0.42.zip
   mv vosk-model-small-es-0.42 vosk-model
   cd ..
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
