import threading
import sounddevice as sd
import vosk
import json
import queue
import logging
import numpy as np
from config import WAKE_WORDS, TIMEOUT, SENSIBILIDAD_WAKE, MODEL_PATH
from tts import hablar
from interfaz import asistente
import time

# Cola global para el audio
audio_queue = None
# Reconocedor de voz
rec = None
# Cola para enviar comandos procesados
comando_queue = None
# Estado de escucha activa
escuchando = False
# Tiempo de espera antes de volver al modo inactivo (segundos)
TIEMPO_ESPERA = 5.0
ultimo_tiempo_actividad = time.time()

# Función para verificar si el texto contiene alguna palabra de activación
def contiene_wakeword(texto):
    if not texto:
        return False
    
    texto = texto.lower().strip()
    print(f"\n=== Análisis de reconocimiento ===")
    print(f"Texto reconocido: '{texto}'")
    print(f"Palabras de activación: {WAKE_WORDS}")
    
    # Verificar si alguna palabra de activación está en el texto
    for palabra in WAKE_WORDS:
        # Búsqueda más flexible de palabras de activación
        if palabra in texto or any(palabra.split()[0] in texto.split() for palabra in WAKE_WORDS if len(palabra.split()) > 1):
            print(f"¡Posible palabra de activación detectada en: '{texto}'!")
            # Verificar el nivel de confianza
            palabras_texto = set(texto.split())
            palabras_activacion = set(palabra.split())
            coincidencias = palabras_texto.intersection(palabras_activacion)
            
            # Calcular porcentaje de coincidencia
            porcentaje = len(coincidencias) / len(palabras_activacion) if palabras_activacion else 0
            print(f"Nivel de confianza: {porcentaje*100:.1f}%")
            
            if porcentaje >= SENSIBILIDAD_WAKE:
                print(f"¡Palabra de activación confirmada!")
                return True
    
    print("No se detectaron palabras de activación con suficiente confianza")
    return False

# Función para limpiar el texto de palabras de activación
def limpiar_comando(texto):
    texto = texto.lower()
    for palabra in WAKE_WORDS:
        texto = texto.replace(palabra, '')
    return texto.strip()

def callback(indata, frames, time, status):
    global ultimo_tiempo_actividad
    
    if status:
        logging.warning(f"Audio status: {status}")
    
    # Calcular el volumen actual
    volumen_actual = np.max(np.abs(indata)) * 100  # Convertir a porcentaje
    
    # Solo procesar si el volumen supera el umbral
    if volumen_actual > UMBRAL_VOLUMEN:
        # Aplicar ganancia al audio
        audio_ampliado = indata * ganancia
        audio_ampliado = audio_ampliado.astype('int16')
        
        # Actualizar el tiempo de última actividad
        ultimo_tiempo_actividad = time.time()
        
        # Mostrar nivel de volumen (opcional, para depuración)
        print(f"\rNivel de volumen: {volumen_actual:.1f}%" + " " * 10, end="")
        
        # Enviar a la cola de procesamiento
        audio_queue.put(bytes(audio_ampliado))
    else:
        tiempo_transcurrido = time.time() - ultimo_tiempo_actividad
        if tiempo_transcurrido > 2.0:  # Solo mostrar el mensaje si ha pasado un tiempo sin actividad
            print("\rEsperando voz..." + " " * 20, end="")

def worker_audio():
    global escuchando, ultimo_tiempo_actividad, rec
    
    # Configuración de audio
    samplerate = 16000
    channels = 1
    dtype = 'int16'
    
    # Ajustes de ganancia de audio (puedes ajustar este valor)
    ganancia = 1.5  # Aumentar si el micrófono es muy bajo
    
    # Listar y mostrar dispositivos de audio disponibles
    print("\n=== Configuración de Audio ===")
    print("Dispositivos de audio disponibles:")
    dispositivos = sd.query_devices()
    
    # Mostrar dispositivos disponibles
    for i, dispositivo in enumerate(dispositivos):
        print(f"{i}: {dispositivo['name']} (Entradas: {dispositivo['max_input_channels']})")
    
    # Intentar con el dispositivo predeterminado
    dispositivo_entrada = sd.default.device[0]
    print(f"\nUsando dispositivo de audio (entrada): {dispositivos[dispositivo_entrada]['name']}")
    
    # Verificar si el dispositivo de entrada es válido
    if dispositivos[dispositivo_entrada]['max_input_channels'] == 0:
        error_msg = "¡Error! El dispositivo seleccionado no tiene canales de entrada."
        print(error_msg)
        asistente.agregar_log(error_msg)
        asistente.cambiar_color("red", "Error de micrófono")
        return
    
    try:
        # Configurar el stream de audio
        with sd.RawInputStream(
            samplerate=samplerate,
            blocksize=8000,
            device=dispositivo_entrada,
            dtype=dtype,
            channels=channels,
            callback=callback
        ) as stream:
            print("\n=== Iniciando reconocimiento de voz ===")
            print("Di 'autogestión' o 'asistente' para activar el modo de escucha...")
            
            # Actualizar la interfaz
            asistente.cambiar_color("green", "Listo")
            asistente.agregar_log("Sistema de reconocimiento de voz inicializado")
            asistente.agregar_log(f"Dispositivo: {dispositivos[dispositivo_entrada]['name']}")
            asistente.agregar_log(f"Tasa de muestreo: {samplerate} Hz")
            
            # Verificar si el stream de audio está activo
            print(f"Estado del stream: {'Activo' if stream.active else 'Inactivo'}")
            print(f"Tasa de muestreo: {stream.samplerate} Hz")
            print(f"Canales: {stream.channels}")
            print("\n=== Escuchando... ===\n")
            
            while True:
                try:
                    # Obtener datos de audio de la cola
                    data = audio_queue.get(timeout=TIMEOUT)
                    
                    # Procesar el audio con Vosk
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        texto = result.get("text", "").strip()
                        
                        if not texto:
                            continue
                            
                        # Mostrar en la interfaz
                        asistente.agregar_log(f"Reconocido: {texto}")
                        print(f"\nTexto reconocido: '{texto}'")
                        print(f"Palabras de activación: {WAKE_WORDS}")
                        
                        # Actualizar el último tiempo de actividad
                        ultimo_tiempo_actividad = time.time()
                        
                        # Verificar si el texto contiene alguna palabra de activación
                        if contiene_wakeword(texto):
                            if not escuchando:
                                escuchando = True
                                asistente.cambiar_color("blue", "Escuchando...")
                                asistente.agregar_log("¡Palabra de activación detectada!")
                                hablar("¿En qué puedo ayudarte?")
                        
                        # Si está en modo escucha, procesar el comando
                        elif escuchando:
                            comando = limpiar_comando(texto)
                            if comando:  # Solo procesar si hay algo después de la palabra de activación
                                asistente.agregar_log(f"Procesando comando: {comando}")
                                asistente.cambiar_color("yellow", "Procesando...")
                                if comando_queue:
                                    comando_queue.put(comando)
                            else:
                                escuchando = False
                                asistente.cambiar_color("green", "Listo")
                                asistente.agregar_log("Modo de escucha desactivado")
                    
                    # Verificar tiempo de inactividad
                    if escuchando and (time.time() - ultimo_tiempo_actividad > TIEMPO_ESPERA):
                        escuchando = False
                        asistente.cambiar_color("green", "Listo")
                        asistente.agregar_log("Tiempo de inactividad excedido")
                    
                except queue.Empty:
                    # Verificar tiempo de inactividad
                    if escuchando and (time.time() - ultimo_tiempo_actividad > TIEMPO_ESPERA):
                        escuchando = False
                        asistente.cambiar_color("green", "Listo")
                        asistente.agregar_log("Tiempo de inactividad excedido")
                        asistente.detener_animacion()
                    continue
                    
    except Exception as e:
        print(f"\n=== Error en el flujo de audio ===")
        print(f"Tipo de error: {type(e).__name__}")
        print(f"Mensaje: {str(e)}")
        print("\nPosibles soluciones:")
        print("1. Verifica que el micrófono esté conectado correctamente.")
        print("2. Asegúrate de que el micrófono tenga permisos de acceso.")
        print("3. Prueba con un dispositivo de audio diferente.")
        print("4. Verifica que no haya otras aplicaciones usando el micrófono.")
        print("5. Reinicia el asistente e intenta de nuevo.")
        raise  # Relanzar la excepción para que sea manejada por run_worker

# Inicializar el worker de audio
def start_audio_worker(audio_q, modelo_vosk, cmd_queue=None):
    global audio_queue, rec, comando_queue
    audio_queue = audio_q
    comando_queue = cmd_queue
    
    # Configurar el modelo Vosk
    try:
        print("\nInicializando el modelo de reconocimiento de voz...")
        print(f"Ruta del modelo: {MODEL_PATH}")
        
        # Verificar que el modelo existe
        import os
        if not os.path.exists(MODEL_PATH):
            print(f"¡Error! No se encontró el modelo en la ruta: {MODEL_PATH}")
            print("Asegúrate de que el modelo Vosk para español esté descargado y en la carpeta correcta.")
            return
            
        # Inicializar el reconocedor
        rec = vosk.KaldiRecognizer(modelo_vosk, 16000)
        rec.SetWords(True)
        print("Modelo de reconocimiento de voz inicializado correctamente.")
        
        # Listar dispositivos de audio disponibles
        print("\nDispositivos de audio disponibles:")
        print(sd.query_devices())
        
        # Configurar el dispositivo de audio predeterminado
        dispositivo_entrada = sd.default.device[0]  # Usar el dispositivo predeterminado
        print(f"\nUsando dispositivo de audio (entrada): {sd.query_devices(dispositivo_entrada)['name']}")
        
        def run_worker():
            while True:
                try:
                    worker_audio()
                except Exception as e:
                    print(f"\nError en el worker de audio: {e}")
                    print("Reiniciando worker de audio en 2 segundos...")
                    time.sleep(2)
        
        # Iniciar el hilo del worker de audio
        threading.Thread(target=run_worker, daemon=True).start()
        
    except Exception as e:
        print(f"\nError al inicializar el reconocimiento de voz: {e}")
        print("Asegúrate de que el modelo Vosk para español esté correctamente instalado.")
        print("Puedes descargarlo desde: https://alphacephei.com/vosk/models")
        print(f"y extraerlo en: {os.path.abspath('models')}")
