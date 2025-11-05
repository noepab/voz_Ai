import threading
import logging
import json
from tts import hablar
from utils import registrar_historial

comando_queue = None

# Carga comandos de archivo JSON externo para fácil edición/ampliación
with open("comandos.json", "r", encoding="utf8") as f:
    COMANDOS_EXTERNOS = json.load(f)

def ejecutar_comando(texto):
    texto = texto.lower().strip()
    # Comprobación rápida en JSON externo
    if texto in COMANDOS_EXTERNOS:
        accion = COMANDOS_EXTERNOS[texto]
        if accion.startswith("http"):
            import os
            os.system(f'start chrome "{accion}"')
            hablar(f"Abriendo {accion.split('//')[1].split('/')[0]}")
        else:
            hablar(accion)
        registrar_historial(texto, accion)
        return

    # Fallback: ayuda dinámica (comandos disponibles)
    if texto in ("ayuda", "help"):
        posibles = [k for k in COMANDOS_EXTERNOS.keys()]
        hablar("Puedes decir: " + ", ".join(posibles[:5]) + "...")
        return

    # OpenAI integration example (requiere KEY y requests)
    if "openai" in texto:
        try:
            import requests
            OPENAI_KEY = "tu-clave-openai"
            prompt = "¿Qué hora es en Nueva York?"
            res = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_KEY}"},
                json={"model": "gpt-3.5-turbo", "messages": [{"role":"user","content":prompt}]}
            )
            text_res = res.json()["choices"][0]["message"]["content"]
            hablar(text_res)
            registrar_historial(texto, "openai_consulta")
            return
        except Exception as e:
            hablar("No puedo conectar con OpenAI ahora.")
            logging.error(f"OpenAI error: {e}")

    # Por defecto
    hablar("No entiendo ese comando todavía. Di 'ayuda' para saber más.")
    registrar_historial(texto, "no_reconocido")

def worker_comandos():
    while True:
        try:
            texto = comando_queue.get(timeout=2)
        except Exception:
            continue
        if texto is None:
            break
        ejecutar_comando(texto)

def start_comando_worker(input_queue):
    global comando_queue
    comando_queue = input_queue
    threading.Thread(target=worker_comandos, daemon=True).start()
