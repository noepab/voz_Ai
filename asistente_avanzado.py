"""
Asistente de Voz Avanzado - Interfaz Unificada
=============================================
Interfaz completa que integra reconocimiento de voz, control del sistema,
funcionalidades avanzadas y una interfaz de usuario moderna.
"""

import os
import sys
import json
import queue
import threading
import time
import random
import re
import webbrowser
import subprocess
import datetime
import logging
import hashlib
import uuid
import tkinter as tk
import sounddevice as sd
import vosk
import difflib
import pyautogui
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Callable, Any, Union
from dataclasses import dataclass, asdict, field
from enum import Enum, auto

# Configuración de logging
logging.basicConfig(
    filename="asistente.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ========== Configuración General ==========
MODEL_PATH = "models/vosk-model-small-es-0.42"
WAKE_WORDS = ["autogestión", "agp", "asistente", "illo", "compae"]
HISTORIAL = "historial_comandos.txt"
TIMEOUT = 0.5
SENSIBILIDAD_WAKE = 0.7

# Inicialización de colas
audio_queue = queue.Queue()
comando_queue = queue.Queue()
tts_queue = queue.Queue()

# Clase para el indicador visual de estado
class IndicadorEstado:
    """Indicador visual del estado del asistente."""
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Asistente de Voz")
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
        """Cambia el color del indicador y actualiza el texto de estado."""
        self.color_actual = color
        self.texto_estado = texto
        try: 
            self.root.after(0, self._actualizar_interfaz)
        except: 
            pass

    def _actualizar_interfaz(self):
        """Actualiza la interfaz del indicador visual."""
        try:
            self.canvas.itemconfig(self.circulo, fill=self.color_actual)
            self.label_estado.config(text=self.texto_estado)
            self.historial_label.config(text="\n".join(buffer_texto[-3:]))
            bordes = {"green":"#00ff00", "blue":"#0088ff", "yellow":"#ffaa00", "red":"#ff0000", "gray":"#444444"}
            self.canvas.itemconfig(self.circulo_borde, outline=bordes.get(self.color_actual, "#444"))
        except Exception as e:
            pass

# Estado global
modo_dictado = False
estado_actual = "esperando"
buffer_texto = []
ultimo_tema = None

# Inicialización global
led = IndicadorEstado()

# ========== TTS (Text-to-Speech) ==========
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

def hablar(texto):
    """Reproduce el texto como voz y lo muestra en la interfaz."""
    print(f"💬 {texto}")
    tts_queue.put(texto)
    buffer_texto.append("> " + texto)
    return texto

def worker_tts():
    """Hilo para el procesamiento de texto a voz."""
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

# Iniciar hilo de TTS
tts_thread = threading.Thread(target=worker_tts, daemon=True)
tts_thread.start()

def agregar_contexto(texto):
    """Agrega texto al buffer de contexto."""
    buffer_texto.append(texto)
    if len(buffer_texto) > 50:  # Limitar el tamaño del buffer
        buffer_texto.pop(0)
    return texto

def normalizar_texto(texto):
    """Normaliza el texto para mejorar el reconocimiento."""
    correcciones = {
        "auto gestión": "autogestión", "compa": "compae",
        "abre guguel": "abre google", "abre yu tiub": "abre youtube",
        "qué horas": "qué hora es", "qué días": "qué día es"
    }
    texto_lower = texto.lower()
    for original, correccion in correcciones.items():
        texto_lower = texto_lower.replace(original, correccion)
    return texto_lower

def detectar_wake_word(texto):
    """Detecta si el texto contiene una palabra de activación."""
    texto_norm = normalizar_texto(texto)
    for wake in WAKE_WORDS:
        if wake in texto_norm: 
            return True
    palabras = texto_norm.split()
    for palabra in palabras:
        for wake in WAKE_WORDS:
            similitud = difflib.SequenceMatcher(None, palabra, wake).ratio()
            if similitud >= SENSIBILIDAD_WAKE:
                logging.info(f"Wake word: '{palabra}' ≈ '{wake}' ({similitud:.2f})")
                return True
    return False

# ========== Procesamiento de Comandos ==========

comandos = {
    "salir": lambda: salir_programa(),
    "apagar": lambda: salir_programa(),
    "hola": lambda: hablar("¡Hola! ¿En qué puedo ayudarte?"),
    "buenos días": lambda: hablar("Buenos días. ¿En qué puedo ayudarte?"),
    "buenas tardes": lambda: hablar("Buenas tardes. ¿En qué necesitas ayuda?"),
    "cómo estás": lambda: hablar("Estoy funcionando correctamente, gracias por preguntar."),
    "qué tal": lambda: hablar("Todo en orden, ¿y tú?"),
    "qué hora es": lambda: hablar(datetime.datetime.now().strftime("Son las %H:%M")),
    "qué día es": lambda: hablar(datetime.datetime.now().strftime("Hoy es %A %d de %B")),
    "fecha": lambda: hablar(datetime.datetime.now().strftime("Estamos a %d de %B de %Y")),
    "abre google": lambda: (os.system("start chrome https://www.google.com"), hablar("Abriendo Google")),
    "abre youtube": lambda: (os.system("start chrome https://www.youtube.com"), hablar("Abriendo YouTube")),
    "abre correo": lambda: (os.system("start chrome https://mail.google.com"), hablar("Abriendo correo")),
    "ayuda": lambda: hablar("Puedo abrir aplicaciones, buscar en internet, decir la hora y más. ¿En qué te ayudo?"),
    "qué puedes hacer": lambda: hablar("Puedo abrir programas, navegar por internet, responder preguntas básicas y más."),
}

def responder_conversacion(texto):
    """Responde a entradas de conversación no reconocidas como comandos."""
    global ultimo_tema
    respuestas = [
        "No te he entendido bien, ¿puedes repetirlo?",
        "¿Quieres que abra algo o que busque información?",
        "Eso no lo tengo programado todavía.",
        "No entiendo eso aún, pero lo aprenderé."
    ]
    import random
    if ultimo_tema and any(p in texto.lower() for p in ultimo_tema.split()):
        respuesta = "Sigues con lo mismo, ¿no? Dime qué necesitas."
    else:
        respuesta = random.choice(respuestas)
    hablar(respuesta)
    ultimo_tema = texto.lower()
    return respuesta

def procesar_comando(texto):
    """Procesa un comando de voz o texto."""
    global modo_dictado, estado_actual
    
    texto_norm = normalizar_texto(texto)
    led.cambiar_color("green", "Procesando...")
    
    # Verificar si estamos en modo dictado
    if modo_dictado and "fin del dictado" not in texto_norm:
        escribir_por_voz(texto)
        return "Texto dictado"
        
    # Comandos especiales de dictado
    if "empieza dictado" in texto_norm or "inicia dictado" in texto_norm:
        return iniciar_dictado()
    if "fin del dictado" in texto_norm or "termina dictado" in texto_norm:
        return detener_dictado()
        
    # Comandos de escritura
    if any(texto_norm.startswith(p) for p in ["escribe", "anota", "pon ", "redacta", "dicta", "transcribe"]):
        return escribir_por_voz(texto)
    
    # Buscar comando coincidente
    mejor = difflib.get_close_matches(texto_norm, comandos.keys(), n=1, cutoff=0.6)
    if mejor:
        comando = mejor[0]
        try:
            comandos[comando]()
            agregar_contexto(f"Ejecutado: {comando}")
            return f"Comando ejecutado: {comando}"
        except Exception as e:
            error_msg = f"Error ejecutando comando: {str(e)}"
            logging.error(error_msg)
            return error_msg
    else:
        return responder_conversacion(texto)
    
    led.cambiar_color("blue", "Escuchando...")
    return "Procesamiento completado"

# ========== Funciones de Dictado ==========

def escribir_por_voz(texto):
    """Escribe el texto dictado en la posición actual del cursor."""
    texto_limpio = re.sub(r"^(escribe esto|anota|pon|redacta|dicta|transcribe)\s*", "", texto, flags=re.IGNORECASE)
    hablar(f"Voy a escribir: {texto_limpio}")
    time.sleep(0.5)
    pyautogui.write(texto_limpio + " ", interval=0.05)
    agregar_contexto(f"Escribió: {texto_limpio}")
    return f"Texto escrito: {texto_limpio}"

def iniciar_dictado():
    """Activa el modo de dictado."""
    global modo_dictado
    modo_dictado = True
    mensaje = "Modo dictado activado. Di 'fin del dictado' para terminar."
    hablar(mensaje)
    led.cambiar_color("green", "DICTADO ACTIVO")
    return mensaje

def detener_dictado():
    """Desactiva el modo de dictado."""
    global modo_dictado
    modo_dictado = False
    mensaje = "Modo dictado finalizado."
    hablar(mensaje)
    led.cambiar_color("blue", "Escuchando...")
    return mensaje

# ========== Procesamiento de Audio ==========

def callback(indata, frames, time, status):
    """Callback para el stream de audio."""
    if status:
        logging.warning(f"Audio status: {status}")
    audio_queue.put(bytes(indata))

def worker_audio():
    """Hilo para el procesamiento de audio."""
    global estado_actual
    print("🎙️ Escuchando... (di 'autogestión', 'illo' o 'compae')")
    led.cambiar_color("blue", "Escuchando...")
    
    # Inicializar el modelo Vosk
    print(f"🧠 Cargando modelo Vosk desde: {MODEL_PATH}")
    try:
        model = vosk.Model(MODEL_PATH)
        rec = vosk.KaldiRecognizer(model, 16000)
        rec.SetWords(True)
        print("✅ Modelo cargado correctamente")
    except Exception as e:
        error_msg = f"❌ Error cargando modelo: {e}"
        print(error_msg)
        hablar("Error al cargar el modelo de voz")
        return

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
                        print(f"🗣️ Reconocido: '{texto}'")
                        logging.debug(f"Reconocido: {texto}")
                        agregar_contexto(texto)
                        
                        if detectar_wake_word(texto):
                            print(f"✅ Wake word detectada en: '{texto}'")
                            led.cambiar_color("green", "¡Te escucho!")
                            estado_actual = "procesando"
                            
                            # Extraer el comando eliminando la palabra de activación
                            texto_comando = texto
                            for wake in WAKE_WORDS:
                                texto_comando = texto_comando.replace(wake, "").strip()
                            
                            if texto_comando:
                                comando_queue.put(texto_comando)
                            else:
                                hablar("¿Sí? Dime qué necesitas.")
                                
        except Exception as e:
            error_msg = f"Error en el procesamiento de audio: {e}"
            logging.error(error_msg)
            print(f"❌ {error_msg}")
            led.cambiar_color("red", "Error de audio")
            hablar("Ha ocurrido un error con el procesamiento de voz")

def worker_comandos():
    """Hilo para el procesamiento de comandos."""
    while True:
        try:
            texto = comando_queue.get(timeout=2)
            if texto is None:
                break
            procesar_comando(texto)
        except queue.Empty:
            continue
        except Exception as e:
            error_msg = f"Error en worker de comandos: {e}"
            logging.error(error_msg)
            print(f"❌ {error_msg}")

# ========== Funciones del Sistema ==========

def salir_programa():
    """Cierra la aplicación de manera controlada."""
    global estado_actual
    estado_actual = "cerrando"
    led.cambiar_color("red", "Apagando...")
    hablar("Apagando el asistente. Hasta luego.")
    time.sleep(2)
    
    # Detener hilos
    tts_queue.put(None)
    comando_queue.put(None)
    
    logging.info("Asistente finalizado")
    try:
        led.root.quit()
        led.root.destroy()
    except:
        pass
    os._exit(0)

def registrar_historial(entrada, accion):
    """Registra una entrada en el historial de comandos."""
    try:
        with open(HISTORIAL, "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} | {entrada} -> {accion}\n")
    except Exception as e:
        logging.error(f"Error registrando en historial: {e}")

# ========== Inicialización y Bucle Principal ==========

def inicializar_asistente():
    """Inicializa el asistente y sus componentes."""
    print("\n" + "="*50)
    print("🎯 ASISTENTE DE VOZ - INTERFAZ UNIFICADA")
    print("="*50 + "\n")
    print("🔊 Palabras de activación:", ", ".join(f"'{w}'" for w in WAKE_WORDS))
    print("💡 Ejemplo: 'illo abre google', 'asistente qué hora es', o di 'ayuda'\n")
    
    # Iniciar hilos
    audio_thread = threading.Thread(target=worker_audio, daemon=True)
    comando_thread = threading.Thread(target=worker_comandos, daemon=True)
    
    audio_thread.start()
    comando_thread.start()
    
    # Mensaje de bienvenida
    led.cambiar_color("yellow", "Iniciando...")
    hablar("Asistente de voz activado. Estoy listo para ayudarte.")
    
    # Mantener la aplicación en ejecución
    try:
        led.root.mainloop()
    except KeyboardInterrupt:
        print("\n👋 Recibida señal de interrupción. Cerrando...")
    finally:
        salir_programa()

if __name__ == "__main__":
    # Inicializar variables globales
    tts_queue = queue.Queue()
    modo_dictado = False
    estado_actual = "esperando"
    buffer_texto = []
    ultimo_tema = None
    
    # Iniciar la aplicación
    inicializar_asistente()

# Configuración de logging
logging.basicConfig(
    filename="asistente.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class TipoEvento(Enum):
    """Tipos de eventos que se pueden auditar."""
    INICIO_APLICACION = auto()
    CIERRE_APLICACION = auto()
    COMANDO_VOZ = auto()
    RESPUESTA_VOZ = auto()
    ERROR = auto()
    ACCION_USUARIO = auto()
    SISTEMA = auto()
    SEGURIDAD = auto()
    CONFIGURACION = auto()

@dataclass
class EventoAuditoria:
    """Clase para representar un evento de auditoría."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.datetime.now().isoformat())
    tipo: TipoEvento = TipoEvento.SISTEMA
    usuario: str = ""
    accion: str = ""
    detalles: Dict[str, Any] = field(default_factory=dict)
    resultado: str = ""
    ip: str = ""
    user_agent: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el evento a un diccionario."""
        data = asdict(self)
        data["tipo"] = self.tipo.name
        return data

class NivelAuditoria(Enum):
    """Niveles de auditoría."""
    MINIMO = 1  # Solo eventos críticos
    NORMAL = 2  # Eventos importantes
    DETALLADO = 3  # Todos los eventos
    DEBUG = 4  # Incluye información de depuración

class Auditoria:
    """Clase para manejar la auditoría del sistema."""
    
    _instancia = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Implementa el patrón Singleton."""
        with cls._lock:
            if cls._instancia is None:
                cls._instancia = super(Auditoria, cls).__new__(cls)
                cls._instancia._inicializado = False
        return cls._instancia
    
    def __init__(self):
        """Inicializa el sistema de auditoría."""
        if self._inicializado:
            return
            
        self._inicializado = True
        self._eventos: List[EventoAuditoria] = []
        self._nivel = NivelAuditoria.NORMAL
        self._archivo_log = "auditoria.log"
        self._tamano_maximo = 10 * 1024 * 1024  # 10 MB
        self._max_eventos = 10000
        self._lock = threading.Lock()
        self._inicializar_log()
    
    def _inicializar_log(self) -> None:
        """Inicializa el archivo de log de auditoría."""
        try:
            # Crear directorio de logs si no existe
            log_dir = os.path.dirname(self._archivo_log)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            # Rotar el log si es demasiado grande
            if os.path.exists(self._archivo_log) and os.path.getsize(self._archivo_log) > self._tamano_maximo:
                self._rotar_log()
                
        except Exception as e:
            logging.error(f"Error al inicializar el log de auditoría: {e}")
    
    def _rotar_log(self) -> None:
        """Rota el archivo de log cuando alcanza el tamaño máximo."""
        try:
            # Crear copia con timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_base, extension = os.path.splitext(self._archivo_log)
            archivo_rotado = f"{nombre_base}_{timestamp}{extension}"
            
            os.rename(self._archivo_log, archivo_rotado)
            
            # Comprimir el archivo rotado (opcional)
            # import gzip
            # with open(archivo_rotado, 'rb') as f_in:
            #     with gzip.open(f"{archivo_rotado}.gz", 'wb') as f_out:
            #         f_out.writelines(f_in)
            # os.remove(archivo_rotado)
            
        except Exception as e:
            logging.error(f"Error al rotar el log de auditoría: {e}")
    
    def registrar_evento(
        self,
        tipo: TipoEvento,
        accion: str,
        detalles: Optional[Dict[str, Any]] = None,
        resultado: str = "",
        usuario: str = "",
        ip: str = "",
        user_agent: str = ""
    ) -> str:
        """Registra un nuevo evento de auditoría.
        
        Args:
            tipo: Tipo de evento.
            accion: Descripción de la acción realizada.
            detalles: Detalles adicionales del evento.
            resultado: Resultado de la acción.
            usuario: Usuario que realizó la acción.
            ip: Dirección IP del usuario.
            user_agent: Agente de usuario del cliente.
            
        Returns:
            str: ID del evento registrado.
        """
        if detalles is None:
            detalles = {}
            
        evento = EventoAuditoria(
            tipo=tipo,
            usuario=usuario or self._obtener_usuario_actual(),
            accion=accion,
            detalles=detalles,
            resultado=resultado,
            ip=ip or self._obtener_ip(),
            user_agent=user_agent or self._obtener_user_agent()
        )
        
        with self._lock:
            # Limitar el número de eventos en memoria
            if len(self._eventos) >= self._max_eventos:
                self._eventos.pop(0)
                
            self._eventos.append(evento)
            
            # Escribir en el log
            self._escribir_log(evento)
            
        return evento.id
    
    def _escribir_log(self, evento: EventoAuditoria) -> None:
        """Escribe un evento en el archivo de log."""
        try:
            with open(self._archivo_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(evento.to_dict(), ensure_ascii=False) + '\n')
        except Exception as e:
            logging.error(f"Error al escribir en el log de auditoría: {e}")
    
    def obtener_eventos(
        self,
        tipo: Optional[TipoEvento] = None,
        usuario: Optional[str] = None,
        fecha_desde: Optional[datetime.datetime] = None,
        fecha_hasta: Optional[datetime.datetime] = None,
        limite: int = 100
    ) -> List[Dict[str, Any]]:
        """Obtiene eventos de auditoría según los criterios de búsqueda.
        
        Args:
            tipo: Filtrar por tipo de evento.
            usuario: Filtrar por usuario.
            fecha_desde: Filtrar por fecha mínima.
            fecha_hasta: Filtrar por fecha máxima.
            limite: Número máximo de eventos a devolver.
            
        Returns:
            List[Dict[str, Any]]: Lista de eventos que coinciden con los criterios.
        """
        resultados = []
        
        with self._lock:
            # Cargar eventos del archivo de log si es necesario
            eventos = self._cargar_eventos_desde_log()
            
            for evento in reversed(eventos):  # Los más recientes primero
                try:
                    # Aplicar filtros
                    if tipo is not None and evento.tipo != tipo:
                        continue
                        
                    if usuario and evento.usuario != usuario:
                        continue
                        
                    evento_timestamp = datetime.datetime.fromisoformat(evento.timestamp)
                    
                    if fecha_desde and evento_timestamp < fecha_desde:
                        continue
                        
                    if fecha_hasta and evento_timestamp > fecha_hasta:
                        continue
                    
                    resultados.append(evento.to_dict())
                    
                    if len(resultados) >= limite:
                        break
                        
                except Exception as e:
                    logging.error(f"Error al procesar evento de auditoría: {e}")
        
        return resultados
    
    def _cargar_eventos_desde_log(self) -> List[EventoAuditoria]:
        """Carga eventos desde el archivo de log."""
        eventos = []
        
        if not os.path.exists(self._archivo_log):
            return eventos
            
        try:
            with open(self._archivo_log, 'r', encoding='utf-8') as f:
                for linea in f:
                    try:
                        data = json.loads(linea)
                        evento = EventoAuditoria(
                            id=data.get('id', str(uuid.uuid4())),
                            timestamp=data.get('timestamp', datetime.datetime.now().isoformat()),
                            tipo=TipoEvento[data.get('tipo', 'SISTEMA')],
                            usuario=data.get('usuario', ''),
                            accion=data.get('accion', ''),
                            detalles=data.get('detalles', {}),
                            resultado=data.get('resultado', ''),
                            ip=data.get('ip', ''),
                            user_agent=data.get('user_agent', '')
                        )
                        eventos.append(evento)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            logging.error(f"Error al cargar eventos desde el log: {e}")
        
        return eventos
    
    def _obtener_usuario_actual(self) -> str:
        """Obtiene el nombre de usuario actual del sistema."""
        try:
            import getpass
            return getpass.getuser()
        except Exception:
            return "usuario_desconocido"
    
    def _obtener_ip(self) -> str:
        """Intenta obtener la dirección IP del cliente."""
        try:
            import socket
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return ""
    
    def _obtener_user_agent(self) -> str:
        """Obtiene información del agente de usuario."""
        try:
            import platform
            return f"{platform.system()} {platform.release()} {platform.machine()}"
        except Exception:
            return ""
    
    def generar_informe(
        self,
        fecha_desde: Optional[datetime.datetime] = None,
        fecha_hasta: Optional[datetime.datetime] = None,
        formato: str = "txt"
    ) -> str:
        """Genera un informe de auditoría.
        
        Args:
            fecha_desde: Fecha de inicio del informe.
            fecha_hasta: Fecha de fin del informe.
            formato: Formato del informe (txt, json, csv).
            
        Returns:
            str: Ruta al archivo de informe generado.
        """
        eventos = self.obtener_eventos(fecha_desde=fecha_desde, fecha_hasta=fecha_hasta)
        
        # Crear directorio de informes si no existe
        os.makedirs("informes", exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = os.path.join("informes", f"informe_auditoria_{timestamp}.{formato}")
        
        try:
            with open(nombre_archivo, 'w', encoding='utf-8') as f:
                if formato == "json":
                    json.dump(eventos, f, ensure_ascii=False, indent=2)
                elif formato == "csv":
                    import csv
                    if not eventos:
                        return nombre_archivo
                        
                    # Obtener todos los campos posibles
                    campos = set()
                    for evento in eventos:
                        campos.update(evento.keys())
                    
                    writer = csv.DictWriter(f, fieldnames=sorted(campos))
                    writer.writeheader()
                    writer.writerows(eventos)
                else:  # txt por defecto
                    for evento in eventos:
                        f.write(f"[{evento.get('timestamp', '')}] {evento.get('tipo', '')}: {evento.get('accion', '')}\n")
                        if 'detalles' in evento and evento['detalles']:
                            f.write(f"Detalles: {json.dumps(evento['detalles'], ensure_ascii=False, indent=2)}\n")
                        if 'resultado' in evento and evento['resultado']:
                            f.write(f"Resultado: {evento['resultado']}\n")
                        f.write("-" * 80 + "\n")
            
            return nombre_archivo
            
        except Exception as e:
            logging.error(f"Error al generar informe de auditoría: {e}")
            raise
    
    def limpiar_eventos(self, confirmar: bool = True) -> bool:
        """Limpia todos los eventos de auditoría.
        
        Args:
            confirmar: Si es True, solicita confirmación antes de borrar.
            
        Returns:
            bool: True si se borraron los eventos, False en caso contrario.
        """
        if confirmar:
            try:
                import tkinter as tk
                from tkinter import messagebox
                
                root = tk.Tk()
                root.withdraw()  # Ocultar la ventana principal
                
                respuesta = messagebox.askyesno(
                    "Confirmar borrado",
                    "¿Estás seguro de que deseas borrar todos los registros de auditoría?\n"
                    "Esta acción no se puede deshacer."
                )
                
                if not respuesta:
                    return False
                    
            except Exception:
                # Si hay un error con la interfaz gráfica, continuar sin confirmación
                pass
        
        with self._lock:
            try:
                # Limpiar eventos en memoria
                self._eventos.clear()
                
                # Limpiar archivo de log
                if os.path.exists(self._archivo_log):
                    with open(self._archivo_log, 'w', encoding='utf-8') as f:
                        f.write("")
                
                # Registrar el evento de limpieza
                self.registrar_evento(
                    tipo=TipoEvento.SISTEMA,
                    accion="Limpieza de registros de auditoría",
                    detalles={"accion": "limpieza_completa"},
                    resultado="Todos los registros de auditoría han sido eliminados"
                )
                
                return True
                
            except Exception as e:
                logging.error(f"Error al limpiar los registros de auditoría: {e}")
                return False

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("asistente.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Asistente")

try:
    import customtkinter as ctk
    import tkinter as tk
    from tkinter import messagebox, filedialog, ttk
    from PIL import Image, ImageTk
    import pyautogui
    import psutil
    import pygetwindow as gw
    import keyboard
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    import speech_recognition as sr
    import pyttsx3
    
    # Verificar si VOSK está disponible para reconocimiento de voz offline
    try:
        import vosk
        VOSK_AVAILABLE = True
    except ImportError:
        VOSK_AVAILABLE = False
        logger.warning("VOSK no está instalado. El reconocimiento de voz offline no estará disponible.")
        
    # Configuración de PyAutoGUI
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
    
except ImportError as e:
    logger.error(f"Error al importar dependencias: {e}")
    print("Por favor, instala las dependencias necesarias con:")
    print("pip install customtkinter pillow pyautogui psutil pygetwindow keyboard comtypes pycaw SpeechRecognition pyttsx3")
    if not VOSK_AVAILABLE:
        print("pip install vosk")
    sys.exit(1)

# Configuración de la aplicación
class Config:
    # Rutas
    MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
    VOSK_MODEL = os.path.join(MODEL_DIR, "vosk-model-small-es-0.42")
    HISTORIAL_ARCHIVO = "historial_chat.json"
    
    # Configuración de voz
    IDIOMA_VOZ = "es-ES"
    PALABRAS_ACTIVACION = ["asistente", "hola asistente", "oye asistente", "ok asistente"]
    
    # Interfaz
    TEMA_OSCURO = {
        "bg": "#1a1a1a",
        "fg": "#ffffff",
        "accent": "#2b5bff",
        "accent_hover": "#1a42c4",
        "text": "#ffffff",
        "text_secondary": "#b3b3b3",
        "success": "#4caf50",
        "warning": "#ff9800",
        "error": "#f44336",
        "panel": "#2d2d2d",
        "panel_hover": "#3d3d3d"
    }
    
    TEMA_CLARO = {
        "bg": "#f5f5f5",
        "fg": "#000000",
        "accent": "#2b5bff",
        "accent_hover": "#1a42c4",
        "text": "#000000",
        "text_secondary": "#4d4d4d",
        "success": "#388e3c",
        "warning": "#f57c00",
        "error": "#d32f2f",
        "panel": "#e0e0e0",
        "panel_hover": "#d0d0d0"
    }

class InterfazAsistente(ctk.CTk):
    def __init__(self, reconocedor: ReconocedorVoz, control_windows: ControlWindows):
        super().__init__()
        
        self.reconocedor = reconocedor
        self.control_windows = control_windows
        self.en_ejecucion = True
        self.historial_mensajes = []
        
        # Inicializar sistema de auditoría
        self.auditoria = Auditoria()
        self.auditoria.registrar_evento(
            tipo=TipoEvento.INICIO_APLICACION,
            accion="Aplicación iniciada",
            detalles={"version": "1.0.0", "usuario": self._obtener_usuario_actual()}
        )
        
        self.cargar_historial()
        
        # Configuración de la ventana
        self.title("Asistente Virtual Avanzado")
        self.geometry("1000x700")
        self.minsize(800, 600)
        
        # Variables de estado
        self.escuchando = False
        self.modo_oscuro = True
        self.fuente_normal = ctk.CTkFont(family="Segoe UI", size=12)
        
        # Configurar tema oscuro por defecto
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

    def _calcular_duracion_escucha(self) -> float:
        """Calcula la duración de la sesión de escucha actual."""
        if hasattr(self, '_inicio_escucha'):
            return (datetime.datetime.now() - self._inicio_escucha).total_seconds()
        return 0.0
        
    def _procesar_audio(self):
        """Procesa el audio del micrófono en un hilo separado."""
        self._inicio_escucha = datetime.datetime.now()
        
        try:
            # Registrar inicio de procesamiento de audio
            evento_id = self.auditoria.registrar_evento(
                tipo=TipoEvento.COMANDO_VOZ,
                accion="Inicio de procesamiento de audio",
                detalles={"timestamp": self._inicio_escucha.isoformat()}
            )
            
            texto = self.reconocedor.escuchar()
            
            # Registrar resultado del reconocimiento
            self.auditoria.registrar_evento(
                tipo=TipoEvento.COMANDO_VOZ,
                accion="Audio procesado",
                detalles={
                    "duracion_segundos": self._calcular_duracion_escucha(),
                    "texto_identificado": texto is not None,
                    "longitud_texto": len(texto) if texto else 0,
                    "evento_origen": evento_id
                },
                resultado=texto[:100] + ("..." if texto and len(texto) > 100 else "") if texto else ""
            )
            
            if texto:
                self.after(0, self._mostrar_mensaje, "Tú", texto)
                self.after(0, self._procesar_respuesta, texto)
                
        except Exception as e:
            error_msg = f"Error en el reconocimiento de voz: {e}"
            logging.error(error_msg)
            
            # Registrar error en auditoría
            self.auditoria.registrar_evento(
                tipo=TipoEvento.ERROR,
                accion="Error en reconocimiento de voz",
                detalles={
                    "tipo_error": type(e).__name__,
                    "mensaje": str(e),
                    "duracion_segundos": self._calcular_duracion_escucha()
                },
                resultado="error"
            )
            
            self.after(0, self._mostrar_mensaje, "Sistema", error_msg)

    def _procesar_comando(self, texto: str) -> str:
        """Procesa el comando de voz o texto y devuelve la respuesta."""
        texto = texto.lower().strip()
        
        # Registrar comando en auditoría
        evento_id = self.auditoria.registrar_evento(
            tipo=TipoEvento.COMANDO_VOZ if self.escuchando else TipoEvento.ACCION_USUARIO,
            accion=f"Comando recibido: {texto}",
            detalles={
                "modo": "voz" if self.escuchando else "texto",
                "longitud": len(texto)
            }
        )
        
        try:
            # Comandos de sistema
            if any(palabra in texto for palabra in ["cierra", "termina", "salir"]):
                self.auditoria.registrar_evento(
                    tipo=TipoEvento.SISTEMA,
                    accion="Solicitud de cierre de aplicación",
                    detalles={"comando": texto}
                )
                self.after(1000, self.destroy)
                return "Cerrando la aplicación. ¡Hasta pronto!"
                
            # Procesar otros comandos...
            respuesta = self._procesar_comandos_especificos(texto)
            
            # Registrar respuesta en auditoría
            self.auditoria.registrar_evento(
                tipo=TipoEvento.RESPUESTA_VOZ,
                accion=f"Respuesta generada",
                detalles={
                    "comando_original": texto,
                    "longitud_respuesta": len(respuesta),
                    "evento_origen": evento_id
                },
                resultado=respuesta[:100] + ("..." if len(respuesta) > 100 else "")
            )
            
            return respuesta
            
        except Exception as e:
            # Registrar error en auditoría
            self.auditoria.registrar_evento(
                tipo=TipoEvento.ERROR,
                accion=f"Error al procesar comando: {texto}",
                detalles={
                    "tipo_error": type(e).__name__,
                    "mensaje": str(e),
                    "comando": texto
                },
                resultado="error"
            )
            logging.exception(f"Error al procesar comando: {texto}")
            return f"Lo siento, hubo un error al procesar tu solicitud: {str(e)}"

    def _procesar_comandos_especificos(self, texto: str) -> str:
        """Procesa comandos específicos y devuelve respuestas."""
        # Comandos de sistema
        if any(palabra in texto for palabra in ["hora"]):
            return f"La hora actual es: {datetime.datetime.now().strftime('%H:%M')}"
            
        if any(palabra in texto for palabra in ["fecha"]):
            return f"Hoy es: {datetime.datetime.now().strftime('%d/%m/%Y')}"
            
        if any(palabra in texto for palabra in ["archivos", "documentos"]):
            return "Puedo ayudarte a buscar archivos. ¿Qué tipo de archivo necesitas?"
            
        # Comandos de red
        if "ip" in texto and ("cuál es mi" in texto or "muestra mi" in texto):
            try:
                # Obtener la dirección IP local
                import socket
                hostname = socket.gethostname()
                ip_address = socket.gethostbyname(hostname)
                return f"Tu dirección IP local es: {ip_address}"
            except Exception as e:
                return f"No se pudo obtener la dirección IP: {str(e)}"
                
        elif "ping" in texto and "a " in texto:
            dominio = texto.split("a ")[-1].strip()
            return self._ejecutar_comando_windows(f"ping {dominio}")
            
        # Comandos del sistema de archivos
        elif "listar archivos" in texto or "muestra archivos" in texto:
            ruta = "."
            if "en " in texto:
                ruta = texto.split("en ")[-1].strip()
            
            try:
                archivos = os.listdir(ruta)
                if not archivos:
                    return f"No hay archivos en {ruta}"
                return f"Archivos en {ruta}:\n" + "\n".join(archivos)
            except Exception as e:
                return f"Error al listar archivos: {str(e)}"
                
        # Comandos de procesos
        elif "procesos" in texto and ("cuántos" in texto or "muestra" in texto):
            try:
                procesos = list(psutil.process_iter())
                return f"Hay {len(procesos)} procesos en ejecución."
            except Exception as e:
                return f"Error al contar procesos: {str(e)}"
                
        # Comando para obtener información del sistema
        elif "información del sistema" in texto:
            try:
                info = []
                info.append(f"Sistema: {platform.system()} {platform.release()}")
                info.append(f"Procesador: {platform.processor()}")
                info.append(f"Arquitectura: {platform.machine()}")
                info.append(f"Python: {platform.python_version()}")
                
                # Obtener información de la memoria
                mem = psutil.virtual_memory()
                info.append(f"\nMemoria total: {mem.total / (1024**3):.2f} GB")
                info.append(f"Memoria disponible: {mem.available / (1024**3):.2f} GB")
                info.append(f"Porcentaje de memoria usada: {mem.percent}%")
                
                # Obtener información del disco
                particiones = psutil.disk_partitions()
                for particion in particiones:
                    try:
                        uso = psutil.disk_usage(particion.mountpoint)
                        info.append(f"\nDisco {particion.device} ({particion.mountpoint}):")
                        info.append(f"  Total: {uso.total / (1024**3):.2f} GB")
                        info.append(f"  Usado: {uso.used / (1024**3):.2f} GB")
                        info.append(f"  Libre: {uso.free / (1024**3):.2f} GB")
                        info.append(f"  Porcentaje usado: {uso.percent}%")
                    except Exception as e:
                        info.append(f"  Error al obtener información de {particion.device}: {str(e)}")
                
                return "\n".join(info)
                
            except Exception as e:
                return f"Error al obtener información del sistema: {str(e)}"
                
        # Comando para obtener el clima
        elif "clima" in texto or "tiempo" in texto:
            try:
                # Usar una API de clima (requiere clave de API)
                # Esta es una implementación de ejemplo con OpenWeatherMap
                return "Para obtener el clima, necesitarías configurar una API de clima como OpenWeatherMap."
                
            except Exception as e:
                return f"Error al obtener el clima: {str(e)}"
                
        # Comando para traducir texto
        elif "traduce" in texto and "a" in texto:
            try:
                # Extraer el texto a traducir y el idioma destino
                partes = texto.split("traduce", 1)[1].split("a", 1)
                texto_a_traducir = partes[0].strip()
                idioma_destino = partes[1].strip()
                
                # Mapear nombres de idiomas a códigos (ejemplo básico)
                idiomas = {
                    "inglés": "en",
                    "español": "es",
                    "francés": "fr",
                    "alemán": "de",
                    "italiano": "it",
                    "portugués": "pt"
                }
                
                codigo_idioma = idiomas.get(idioma_destino.lower(), "en")
                
                # En una implementación real, aquí se usaría una API de traducción
                # como Google Translate o DeepL
                return f"Para traducir '{texto_a_traducir}' a {idioma_destino} (código: {codigo_idioma}), necesitarías configurar una API de traducción."
                
            except Exception as e:
                return f"Error al procesar la solicitud de traducción: {str(e)}"
                
        # Comando para configurar recordatorios
        elif "recuérdame" in texto or "recuerda que" in texto:
            try:
                # Extraer el recordatorio del texto
                recordatorio = texto.split("que")[-1].strip()
                
                # Aquí podrías implementar la lógica para guardar el recordatorio
                # en una base de datos o archivo, y programar una notificación
                
                return f"Recordatorio guardado: {recordatorio}"
                
            except Exception as e:
                return f"Error al guardar el recordatorio: {str(e)}"
                
        # Comando para realizar cálculos matemáticos
        elif any(op in texto for op in ["más", "menos", "por", "dividido", "elevado a"]):
            try:
                # Reemplazar términos en español por operadores matemáticos
                expresion = texto\
                    .replace("más", "+")\
                    .replace("menos", "-")\
                    .replace("por", "*")\
                    .replace("dividido entre", "/")\
                    .replace("dividido", "/")\
                    .replace("elevado a", "**")\
                    .replace("al cuadrado", "**2")\
                    .replace("al cubo", "**3")
                
                # Eliminar caracteres no deseados
                import re
                expresion = re.sub(r'[^0-9+\-*/.() ]', '', expresion)
                
                # Evaluar la expresión de forma segura
                try:
                    resultado = eval(expresion)
                    return f"El resultado es: {resultado}"
                except:
                    return "No pude realizar el cálculo. Asegúrate de usar una expresión válida."
                    
            except Exception as e:
                return f"Error al procesar el cálculo: {str(e)}"
                
        # Si no se reconoce ningún comando avanzado
        return ""
