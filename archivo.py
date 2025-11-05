import os
import sys
import queue
import sounddevice as sd
import vosk
import json
import difflib
import logging
import threading
import pyautogui
import re
import time
import tkinter as tk
from datetime import datetime
from collections import deque

# ========== Configuración General ==========
MODEL_PATH = "models/vosk-model-small-es-0.42"
WAKE_WORDS = ["autogestión", "agp", "asistente", "illo", "compae"]
HISTORIAL = "historial_comandos.txt"
TIMEOUT = 0.5
SENSIBILIDAD_WAKE = 0.7

# ========== Inicialización ==========
print(f"🧠 Cargando modelo Vosk desde: {MODEL_PATH}")
try:
    model = vosk.Model(MODEL_PATH)
    rec = vosk.KaldiRecognizer(model, 16000)
    rec.SetWords(True)
    print("✅ Modelo cargado correctamente")
except Exception as e:
    print(f"❌ Error cargando modelo: {e}")
    sys.exit(1)

audio_queue = queue.Queue()
comando_queue = queue.Queue()
tts_queue = queue.Queue()

logging.basicConfig(filename="asistente.log",
                   level=logging.DEBUG,
                   format="%(asctime)s - %(levelname)s - %(message)s")

modo_dictado = False
ultimo_tema = None
estado_actual = "esperando"
buffer_texto = deque(maxlen=50)

# ========== Indicador Visual ==========

class IndicadorEstado:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AGP Asistente")
        self.root.geometry("180x220+20+20")
        self.root.resizable(False, False)
        self.root.configure(bg="#1a1a1a")
        self.root.attributes('-topmost', True)
        self.canvas = tk.Canvas(self.root, width=120, height=120, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(padx=15, pady=10)
        self.circulo_borde = self.canvas.create_oval(5,5,115,115, fill="", outline="#444", width=3)
        self.circulo = self.canvas.create_oval(15,15,105,105, fill="gray", outline="")
        self.label_estado = tk.Label(self.root, text="Iniciando...", bg="#1a1a1a", fg="white", font=("Arial",10,"bold"))
        self.label_estado.pack()
        self.historial_label = tk.Label(self.root, text="", bg="#1a1a1a", fg="lightgray", font=("Arial",8))
        self.historial_label.pack()
        self.color_actual = "gray"
        self.texto_estado = "Iniciando..."
        self.animacion_activa = False

    def cambiar_color(self, color, texto=""):
        self.color_actual = color
        self.texto_estado = texto
        try: self.root.after(0, self._actualizar_interfaz)
        except: pass

    def _actualizar_interfaz(self):
        try:
            self.canvas.itemconfig(self.circulo, fill=self.color_actual)
            self.label_estado.config(text=self.texto_estado)
            self.historial_label.config(text="\n".join(list(buffer_texto)[-3:]))
            bordes = {"green":"#00ff00", "blue":"#0088ff", "yellow":"#ffaa00", "red":"#ff0000", "gray":"#444444"}
            self.canvas.itemconfig(self.circulo_borde, outline=bordes.get(self.color_actual, "#444"))
        except: pass

led = IndicadorEstado()

# ========== TTS ==========
try:
    import pyttsx3
    tts_engine = pyttsx3.init()
    tts_engine.setProperty("rate", 175)
    tts_engine.setProperty("volume", 0.9)
    for voice in tts_engine.getProperty('voices'):
        if 'spanish' in voice.name.lower() or 'helena' in voice.name.lower():
            tts_engine.setProperty('voice', voice.id)
            break
    TTS_DISPONIBLE = True
    print("✅ TTS inicializado")
except Exception as e:
    TTS_DISPONIBLE = False
    print(f"⚠️ TTS no disponible: {e}")

def worker_tts():
    global estado_actual
    while True:
        try:
            texto = tts_queue.get(timeout=2)
        except queue.Empty:
            continue
        if texto is None:
            break
        estado_actual = "hablando"
        led.cambiar_color("yellow", "Hablando...")
        logging.info(f"TTS: {texto}")
        if TTS_DISPONIBLE:
            try:
                tts_engine.say(texto)
                tts_engine.runAndWait()
            except Exception as e:
                logging.error(f"Error TTS: {e}")
                print(f"(sin audio): {texto}")
        else:
            print(f"(TTS OFF) {texto}")
        time.sleep(min(len(texto)*0.05, 2))
        estado_actual = "esperando"
        led.cambiar_color("blue", "Escuchando...")

def hablar(texto):
    print(f"💬 {texto}")
    tts_queue.put(texto)
    buffer_texto.append("> " + texto)

tts_thread = threading.Thread(target=worker_tts, daemon=True)
tts_thread.start()

# ========== Audio callback ==========
def callback(indata, frames, time, status):
    if status:
        logging.warning(f"Audio status: {status}")
    audio_queue.put(bytes(indata))

# ========== Historial ==========
def registrar_historial(entrada, accion):
    try:
        with open(HISTORIAL, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} | {entrada} -> {accion}\n")
    except Exception as e:
        logging.error(f"Historial error: {e}")

def agregar_contexto(texto):
    buffer_texto.append(texto)

# ========== Utilidades de texto ==========
def normalizar_texto(texto):
    correcciones = {
        "auto gestión": "autogestión","compa": "compae",
        "abre guguel": "abre google","abre yu tiub": "abre youtube",
        "qué horas": "qué hora es","qué días": "qué día es"
    }
    texto_lower = texto.lower()
    for original, correccion in correcciones.items():
        texto_lower = texto_lower.replace(original, correccion)
    return texto_lower

def detectar_wake_word(texto):
    texto_norm = normalizar_texto(texto)
    for wake in WAKE_WORDS:
        if wake in texto_norm: return True
    palabras = texto_norm.split()
    for palabra in palabras:
        for wake in WAKE_WORDS:
            similitud = difflib.SequenceMatcher(None, palabra, wake).ratio()
            if similitud >= SENSIBILIDAD_WAKE:
                logging.info(f"Wake word: '{palabra}' ≈ '{wake}' ({similitud:.2f})")
                return True
    return False

# ========== Conversacional por defecto ==========
def responder_conversacion(texto):
    global ultimo_tema
    texto_norm = normalizar_texto(texto)
    respuestas = [
        "No te he pillao bien, ¿puedes repetirlo, illo?",
        "¿Quieres que abra algo o que escriba?",
        "Eso no lo tengo programado todavía, compae.",
        "No entiendo eso aún, pero lo aprenderé."
    ]
    import random
    if ultimo_tema and any(p in texto_norm for p in ultimo_tema.split()):
        respuesta = "Sigues con lo mismo, ¿no? Dime qué necesitas."
    else:
        respuesta = random.choice(respuestas)
    hablar(respuesta)
    registrar_historial(texto, "no_reconocido")
    ultimo_tema = texto_norm

# ========== Dictado ==========
def escribir_por_voz(texto):
    texto_limpio = re.sub(r"^(escribe esto|anota|pon|redacta|dicta|transcribe)\s*", "", texto, flags=re.IGNORECASE)
    hablar(f"Vale, escribo: {texto_limpio}")
    time.sleep(0.5)
    pyautogui.write(texto_limpio + " ", interval=0.05)
    registrar_historial(texto, f"escribió: {texto_limpio}")

def iniciar_dictado():
    global modo_dictado
    modo_dictado = True
    hablar("Modo dictado activado. Di 'fin del dictado' para terminar.")
    led.cambiar_color("green", "DICTADO ACTIVO")

def detener_dictado():
    global modo_dictado
    modo_dictado = False
    hablar("Modo dictado finalizado.")
    led.cambiar_color("blue", "Escuchando...")

def procesar_dictado(texto):
    pyautogui.write(" " + texto, interval=0.03)
    registrar_historial(texto, "dictado")

# ========== Comandos ==========
def ejecutar_comando(texto):
    global modo_dictado
    texto_norm = normalizar_texto(texto)
    led.cambiar_color("green", "Procesando...")
    if modo_dictado and "fin del dictado" not in texto_norm:
        procesar_dictado(texto)
        return
    if "empieza dictado" in texto_norm or "inicia dictado" in texto_norm:
        iniciar_dictado()
        return
    if "fin del dictado" in texto_norm or "termina dictado" in texto_norm:
        detener_dictado()
        return
    if any(texto_norm.startswith(p) for p in ["escribe", "anota", "pon ", "redacta", "dicta", "transcribe"]):
        escribir_por_voz(texto)
        return
    comandos = {
        "salir": lambda: salir_programa(),
        "apagar": lambda: salir_programa(),
        "hola": lambda: hablar("¡Hola illo! Aquí estoy."),
        "buenos días": lambda: hablar("Buenos días, compae. ¿Qué necesitas?"),
        "buenas tardes": lambda: hablar("Buenas tardes, ¿en qué te ayudo?"),
        "cómo estás": lambda: hablar("Mejor que nunca, compae. Listo pa' currá."),
        "qué tal": lambda: hablar("Aquí andamos, ¿y tú qué?"),
        "qué hora es": lambda: hablar(datetime.now().strftime("Son las %H:%M")),
        "qué día es": lambda: hablar(datetime.now().strftime("Hoy es %A %d de %B")),
        "fecha": lambda: hablar(datetime.now().strftime("Estamos a %d de %B de %Y")),
        "abre google": lambda: (os.system("start chrome https://www.google.com"), hablar("Abriendo Google")),
        "abre youtube": lambda: (os.system("start chrome https://www.youtube.com"), hablar("Abriendo YouTube")),
        "abre correo": lambda: (os.system("start chrome https://mail.google.com"), hablar("Abriendo correo")),
        "abre gmail": lambda: (os.system("start chrome https://mail.google.com"), hablar("Abriendo Gmail")),
        "abre agp": lambda: (os.system("start chrome https://autogestionpro.com"), hablar("Abriendo AutogestiónPro")),
        "abre panel agp": lambda: (os.system("start chrome https://panel.autogestionpro.com"), hablar("Abriendo panel")),
        "abre métricas": lambda: (os.system("start chrome https://metrics.autogestionpro.com"), hablar("Abriendo métricas")),
        "abre crm": lambda: (os.system("start chrome https://crm.autogestionpro.com"), hablar("Abriendo CRM")),
        "abre bloc de notas": lambda: (os.system("notepad"), hablar("Abriendo bloc de notas")),
        "abre notepad": lambda: (os.system("notepad"), hablar("Abriendo notepad")),
        "abre terminal": lambda: (os.system("start cmd"), hablar("Abriendo terminal")),
        "abre calculadora": lambda: (os.system("calc"), hablar("Abriendo calculadora")),
        "ayuda": lambda: hablar("Puedo abrir apps, buscar en Google, escribir por ti, y más: saluda, pregunta hora, di 'escribe' lo que quieras dictar."),
        "qué puedes hacer": lambda: hablar("Puedo abrir programas, navegar por internet, escribir texto y responder preguntas básicas."),
    }
    mejor = difflib.get_close_matches(texto_norm, comandos.keys(), n=1, cutoff=0.6)
    if mejor:
        comando = mejor[0]
        try:
            comandos[comando]()
            registrar_historial(texto, comando)
            agregar_contexto(f"ejecutó: {comando}")
        except Exception as e:
            logging.error(f"Error ejecutando comando '{comando}': {e}")
            hablar("Hubo un error ejecutando eso, illo.")
    else:
        responder_conversacion(texto)
    led.cambiar_color("blue", "Escuchando...")

def worker_comandos():
    while True:
        try:
            texto = comando_queue.get(timeout=2)
        except queue.Empty:
            continue
        if texto is None:
            break
        ejecutar_comando(texto)

comando_thread = threading.Thread(target=worker_comandos, daemon=True)
comando_thread.start()

def worker_audio():
    global estado_actual
    print("🎙️ Escuchando... (di 'autogestión', 'illo' o 'compae')")
    led.cambiar_color("blue", "Escuchando...")
    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16", channels=1, callback=callback):
        try:
            while True:
                try:
                    data = audio_queue.get(timeout=TIMEOUT)
                except queue.Empty:
                    continue
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    texto = result.get("text", "").strip()
                    if texto:
                        print(f"🗣️ '{texto}'")
                        logging.debug(f"Reconocido: {texto}")
                        agregar_contexto(texto)
                        if detectar_wake_word(texto):
                            print(f"✅ Wake word detectada en: '{texto}'")
                            led.cambiar_color("green", "Comando!")
                            estado_actual = "procesando"
                            texto_comando = texto
                            for wake in WAKE_WORDS:
                                texto_comando = texto_comando.replace(wake, "").strip()
                            if texto_comando:
                                comando_queue.put(texto_comando)
                            else:
                                led.cambiar_color("green", "Te escucho...")
                                hablar("Dime")
        except Exception as e:
            logging.error(f"Error en worker de audio: {e}")
            print(f"❌ Error crítico: {e}")
            led.cambiar_color("red", "Error")

def salir_programa():
    global estado_actual
    estado_actual = "cerrando"
    led.cambiar_color("red", "Apagando...")
    hablar("Apagando el asistente. Hasta luego, illo.")
    time.sleep(2)
    tts_queue.put(None)
    comando_queue.put(None)
    logging.info("Asistente finalizado")
    try:
        led.root.quit()
        led.root.destroy()
    except:
        pass
    sys.exit(0)

def main():
    print("\n" + "="*50)
    print("🎯 ASISTENTE DE VOZ AGP - MODULAR MEJORADO")
    print("="*50 + "\n")
    print("📝 Dev: preparado para ampliación modular y compatible con nuevos comandos y contextos.")
    print("💡 Palabras de activación:", ", ".join(WAKE_WORDS))
    print("💡 Ejemplo: 'illo abre google', 'autogestión qué hora es', o di 'ayuda'\n")
    led.cambiar_color("yellow", "Iniciando...")
    hablar("Asistente de voz AutogestiónPro andaluz activado, listo para ayudarte compae.")

    audio_thread = threading.Thread(target=worker_audio, daemon=True)
    audio_thread.start()
    try:
        led.root.protocol("WM_DELETE_WINDOW", salir_programa)
        led.root.mainloop()
    except KeyboardInterrupt:
        print("\n⚠️ Interrupción detectada, cerrando asistente...")
        salir_programa()
    except Exception as e:
        print(f"❌ Error en la interfaz principal: {e}")
        logging.error(f"Error en mainloop: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Error fatal de lanzador: {e}")
        logging.critical(f"Error fatal: {e}")
        sys.exit(1)
