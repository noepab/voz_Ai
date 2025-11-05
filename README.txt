# AGP Asistente Voz Modular (Nivel Pro)

## Features:
- Comandos por voz totalmente editables desde un simple .json
- Añadir nuevas funciones por webhook, Gmail, calendario fácilmente.
- Feedback visual y de logs en todo momento
- Modular, fácil de testear y mantener

## Integraciones demostradas:
- Google Calendar y Gmail
- Webhook API propia
- OpenAI para IA conversacional

## Tests
- Sólo haz `pytest` en tests/

## Despliegue
- Prepara tu requirements.txt y sigue la estructura modular para escalar rápido

¡Listo para personalizar y llevar a producción!
# AGP Asistente de Voz - Modular

Este proyecto es una arquitectura modular para asistentes de voz Py para pymes y automatización.

## Estructura de carpetas

- main.py              ← Entrada principal
- config.py            ← Configuración global
- interfaz.py          ← GUI y estado visual
- reconocimiento.py    ← Voz a texto (Vosk/audio)
- tts.py               ← Texto a voz (pyttsx3)
- comandos.py          ← Procesamiento de órdenes
- utils.py             ← Funciones auxiliares
- requirements.txt     ← Dependencias
- models/              ← Carpeta con los modelos Vosk

### Ejecución rápida

1. Instala dependencias: `pip install -r requirements.txt`
2. Descarga y pon el modelo Vosk en `models/`
3. Lanza el asistente: `python main.py`

==============================
ASISTENTE DE VOZ AUTOGESTIÓNPRO ANDALUZ
VERSIÓN DIOS 4.0 🔥
==============================

🧠 REQUISITOS:
- Python 3.9 o superior
- Micrófono activo y configurado
- Modelo Vosk: models/vosk-model-small-es-0.42
  (descárgalo desde https://alphacephei.com/vosk/models)
- Windows 10/11 (para comandos de sistema)

🎙️ INSTALACIÓN RÁPIDA:

1. Haz doble clic en "setup.bat"
2. Espera a que termine (instalará todo automáticamente)
3. Descarga el modelo Vosk si no lo tienes
4. Ejecuta:

   call venv\Scripts\activate
   python archivo.py

   (Reemplaza "archivo.py" con el nombre de tu script)

📁 ESTRUCTURA DE CARPETAS:

tu_proyecto/
├── archivo.py                    (tu script principal)
├── setup.bat                     (instalador automático)
├── requirements.txt              (dependencias)
├── README.txt                    (este archivo)
├── models/
│   └── vosk-model-small-es-0.42/ (modelo de voz)
├── venv/                         (entorno virtual)
├── asistente.log                 (se crea al ejecutar)
└── historial_comandos.txt        (se crea al ejecutar)

🔊 PALABRAS DE ACTIVACIÓN:

Di cualquiera de estas para activar comandos:
- "autogestión"
- "agp"
- "asistente"
- "illo"
- "compae"

🎯 COMANDOS DISPONIBLES:

SALUDOS:
- "illo, hola"
- "autogestión, buenos días"
- "compae, cómo estás"

INFORMACIÓN:
- "illo, qué hora es"
- "autogestión, qué día es"
- "compae, fecha"

NAVEGACIÓN WEB:
- "illo, abre google"
- "autogestión, abre youtube"
- "compae, abre gmail"

AUTOGESTIÓNPRO:
- "illo, abre agp"
- "autogestión, abre panel"
- "compae, abre métricas"
- "illo, abre crm"

APLICACIONES:
- "autogestión, abre bloc de notas"
- "illo, abre terminal"
- "compae, abre calculadora"

ESCRITURA:
- "illo, escribe esto hola mundo"
- "autogestión, anota prueba de texto"

DICTADO CONTINUO:
- "illo, empieza dictado"
  (luego habla normalmente sin wake word)
- "fin del dictado"
  (para terminar el modo dictado)

AYUDA Y SALIDA:
- "illo, ayuda"
- "autogestión, qué puedes hacer"
- "compae, salir"

💡 INDICADOR VISUAL:

El asistente muestra una ventana con un círculo de colores:

🔵 AZUL    = Escuchando (esperando wake word)
🟢 VERDE   = Comando detectado, procesando
🟡 AMARILLO = Hablando
🔴 ROJO    = Error o apagando
🔵 CYAN    = Escuchando activamente

🗣️ SISTEMA DE VOZ:

- Respuestas con acento y expresiones andaluzas
- Usa pyttsx3 (voz local, funciona sin internet)
- Voz natural y clara
- Velocidad optimizada a 175 WPM

📊 CARACTERÍSTICAS AVANZADAS:

✅ Reconocimiento fuzzy (entiende comandos similares)
✅ Sistema de contexto (recuerda conversación)
✅ Múltiples workers (audio, comandos, voz separados)
✅ Sin bloqueos (todo funciona en paralelo)
✅ Recuperación automática de errores
✅ Logs detallados para debugging
✅ Historial de todos los comandos

📄 ARCHIVOS GENERADOS:

- asistente.log: Logs técnicos detallados
- historial_comandos.txt: Historial de comandos ejecutados

🐛 SOLUCIÓN DE PROBLEMAS:

PROBLEMA: No reconoce mi voz
SOLUCIÓN: 
  - Verifica que el micrófono esté configurado como predeterminado
  - Habla claro y a volumen normal
  - Asegúrate de decir la wake word ("illo", "autogestión", etc.)

PROBLEMA: No responde por voz
SOLUCIÓN:
  - Verifica que los altavoces estén encendidos
  - El texto se muestra en consola aunque no haya audio
  - Revisa asistente.log para ver errores

PROBLEMA: Error al cargar modelo
SOLUCIÓN:
  - Descarga vosk-model-small-es-0.42 desde:
    https://alphacephei.com/vosk/models
  - Descomprímelo en la carpeta models/

PROBLEMA: "RuntimeError: Calling Tcl from different apartment"
SOLUCIÓN:
  - Ya está resuelto en esta versión 4.0
  - Tkinter ahora se ejecuta en el hilo principal

PROBLEMA: No se instalan las dependencias
SOLUCIÓN:
  - Ejecuta: python -m pip install --upgrade pip
  - Luego: pip install -r requirements.txt
  - Verifica que Python esté en PATH

🔧 COMANDOS DE MANTENIMIENTO:

# Reinstalar dependencias
call venv\Scripts\activate
pip install -r requirements.txt --force-reinstall

# Limpiar logs
del asistente.log
del historial_comandos.txt

# Ver logs en tiempo real
call venv\Scripts\activate
python archivo.py

# Verificar micrófono
python -m sounddevice

📞 SOPORTE:

Si encuentras algún problema:
1. Revisa asistente.log
2. Verifica que todas las dependencias estén instaladas
3. Asegúrate de que el modelo Vosk esté en su lugar
4. Comprueba que el micrófono funcione

💬 EJEMPLOS DE USO:

Ejemplo 1 - Abrir aplicación:
TÚ: "Illo, abre google"
ASISTENTE: "Abriendo Google" [abre Chrome con Google]

Ejemplo 2 - Consulta de hora:
TÚ: "Autogestión, qué hora es"
ASISTENTE: "Son las 15:30"

Ejemplo 3 - Dictado:
TÚ: "Compae, empieza dictado"
ASISTENTE: "Modo dictado activado. Di fin del dictado para terminar."
TÚ: "Este es un texto de prueba que se escribirá automáticamente"
TÚ: "fin del dictado"
ASISTENTE: "Modo dictado finalizado."

Ejemplo 4 - Conversación:
TÚ: "Illo, cómo estás"
ASISTENTE: "Mejor que nunca, compae. Listo pa' currá."

📝 NOTAS DE VERSIÓN:

v4.0 DIOS 🔥
- Sistema de workers especializados (audio, TTS, comandos)
- Colas thread-safe para procesamiento asíncrono
- Detección inteligente de wake words con fuzzy matching
- Interfaz visual premium con animaciones
- Sistema de contexto con buffer circular
- TTS optimizado que no bloquea el reconocimiento
- Comandos expandidos (30+ comandos)
- Gestión de errores robusta con recuperación automática
- Logs nivel DEBUG para troubleshooting avanzado

💻 DESARROLLADO POR:
AutogestiónPro – Asistente Andaluz v4.0 DIOS
Sistema de reconocimiento de voz conversacional
Optimizado para productividad y uso diario

==============================
¡Listo pa' currá, illo! 🔥
==============================