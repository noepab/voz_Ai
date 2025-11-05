import threading
import logging

try:
    import pyttsx3
    tts_engine = pyttsx3.init()
    tts_engine.setProperty("rate", 175)
    tts_engine.setProperty("volume", 0.9)
    TTS_DISPONIBLE = True
except Exception as e:
    TTS_DISPONIBLE = False
    logging.warning(f"TTS no disponible: {e}")

tts_queue = None  # Se debe setear desde main.py (pasándolo como argumento)

def worker_tts():
    while True:
        try:
            texto = tts_queue.get(timeout=2)
        except Exception:
            continue
        if texto is None:
            break
        if TTS_DISPONIBLE:
            try:
                tts_engine.say(texto)
                tts_engine.runAndWait()
            except Exception as e:
                logging.error(f"Error en TTS: {e}")
        else:
            print(f"(TTS OFF): {texto}")

def hablar(texto):
    tts_queue.put(texto)
    # Actualiza historial visual si quieres aquí

def start_tts_worker(input_queue):
    global tts_queue
    tts_queue = input_queue
    tts_thread = threading.Thread(target=worker_tts, daemon=True)
    tts_thread.start()
