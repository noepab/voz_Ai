"""Módulo principal del Asistente AGP.

Un asistente de voz modular basado en Vosk con interfaz gráfica,
reconocimiento de comandos y síntesis de voz.
"""

import logging
import os
import sys
import threading
from queue import Queue

import vosk

from config import MODEL_PATH, TIMEOUT, WAKE_WORDS
from core.resource_monitor import ResourceMonitor
from interfaz_simple import AsistenteVentana
from reconocimiento import start_audio_worker
from tts import start_tts_worker, hablar
from comandos import start_comando_worker

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_model_path(model_path: str) -> bool:
    """Valida que el modelo Vosk existe en la ruta especificada.
    
    Args:
        model_path: Ruta al modelo Vosk
        
    Returns:
        True si el modelo existe, False en caso contrario
    """
    if not os.path.exists(model_path):
        logger.error(f"Modelo no encontrado en: {model_path}")
        logger.error("Por favor, asegúrate de que el modelo Vosk para español esté descargado")
        logger.error("Descarga desde: https://alphacephei.com/vosk/models")
        return False
    logger.info(f"Modelo validado: {model_path}")
    return True


def initialize_vosk_model(model_path: str):
    """Inicializa el modelo de reconocimiento de voz Vosk.
    
    Args:
        model_path: Ruta al modelo Vosk
        
    Returns:
        Tupla (model, recognizer) o None si hay error
    """
    try:
        logger.info("="*50)
        logger.info("Inicializando modelo de voz Vosk")
        logger.info(f"Ruta del modelo: {model_path}")
        
        # Validar modelo
        if not validate_model_path(model_path):
            return None
        
        # Cargar modelo
        logger.info("Cargando modelo...")
        model = vosk.Model(model_path)
        
        # Crear reconocedor
        sample_rate = 16000
        rec = vosk.KaldiRecognizer(model, sample_rate)
        rec.SetWords(True)  # Habilitar reconocimiento de palabras
        
        logger.info(f"Modelo cargado exitosamente")
        logger.info(f"Tasa de muestreo: {sample_rate} Hz")
        logger.info("="*50)
        
        return model, rec
        
    except Exception as e:
        logger.error("="*50)
        logger.error(f"Error al inicializar modelo Vosk: {type(e).__name__}")
        logger.error(f"Detalles: {str(e)}")
        logger.error("="*50)
        return None


def start_workers(audio_q: Queue, rec, comando_q: Queue, tts_q: Queue) -> bool:
    """Inicia los workers de procesamiento en segundo plano.
    
    Args:
        audio_q: Cola de audio
        rec: Reconocedor Vosk
        comando_q: Cola de comandos
        tts_q: Cola de síntesis de voz
        
    Returns:
        True si se inician correctamente, False en caso contrario
    """
    try:
        logger.info("Iniciando workers...")
        start_audio_worker(audio_q, rec, comando_q)
        logger.debug("Worker de audio iniciado")
        
        start_comando_worker(comando_q)
        logger.debug("Worker de comandos iniciado")
        
        start_tts_worker(tts_q)
        logger.debug("Worker de TTS iniciado")
        
        logger.info("Todos los workers iniciados correctamente")
        return True
        
    except Exception as e:
        logger.error(f"Error al iniciar workers: {type(e).__name__}: {str(e)}")
        return False


def setup_gui(audio_q: Queue, comando_q: Queue, tts_q: Queue) -> AsistenteVentana:
    """Configura la interfaz gráfica del asistente.
    
    Args:
        audio_q: Cola de audio
        comando_q: Cola de comandos
        tts_q: Cola de síntesis de voz
        
    Returns:
        Instancia de la interfaz o None si hay error
    """
    try:
        logger.info("Inicializando interfaz gráfica...")
        asistente = AsistenteVentana()
        
        # Configurar cierre de aplicación
        def on_closing():
            logger.info("Cerrando asistente...")
            try:
                asistente.root.quit()
            except Exception as e:
                logger.warning(f"Error al cerrar GUI: {e}")
            finally:
                sys.exit(0)
        
        asistente.root.protocol("WM_DELETE_WINDOW", on_closing)
        logger.info("Interfaz gráfica configurada")
        
        return asistente
        
    except Exception as e:
        logger.error(f"Error al configurar GUI: {type(e).__name__}: {str(e)}")
        return None


def main() -> int:
    """Función principal del asistente AGP.
    
    Returns:
        Código de salida (0 si éxito, 1 si error)
    """
    logger.info("")
    logger.info("*" * 50)
    logger.info("Iniciando AGP - Asistente de Voz Modular")
    logger.info("*" * 50)
    logger.info("")
    
    # Inicializar monitor de recursos (opcional)
    monitor = None
    try:
        monitor = ResourceMonitor()
        logger.debug("Monitor de recursos inicializado")
    except Exception as e:
        logger.warning(f"No se pudo inicializar monitor: {e}")
    
    try:
        # Crear colas de comunicación entre procesos
        audio_q = Queue()
        comando_q = Queue()
        tts_q = Queue()
        logger.debug("Colas de comunicación creadas")
        
        # Inicializar modelo Vosk
        result = initialize_vosk_model(MODEL_PATH)
        if result is None:
            logger.error("No se pudo inicializar el modelo Vosk")
            return 1
        
        model, rec = result
        
        # Iniciar workers
        if not start_workers(audio_q, rec, comando_q, tts_q):
            logger.error("No se pudieron iniciar los workers")
            return 1
        
        # Configurar interfaz gráfica
        asistente = setup_gui(audio_q, comando_q, tts_q)
        if asistente is None:
            logger.error("No se pudo configurar la interfaz")
            return 1
        
        # Planificar mensaje de bienvenida
        def welcome_message():
            logger.info("Asistente listo. Esperando palabra de activación...")
            hablar(f"Asistente AGP activado. Di mi nombre para empezar.")
        
        # Usar TIMEOUT de config en lugar de valor hardcoded
        welcome_delay = TIMEOUT if TIMEOUT else 1000
        asistente.root.after(welcome_delay, welcome_message)
        
        # Iniciar bucle principal
        logger.info("Iniciando bucle principal de la interfaz")
        asistente.root.mainloop()
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Interrupción del usuario (Ctrl+C)")
        return 0
        
    except Exception as e:
        logger.critical(f"Error no manejado en main(): {type(e).__name__}")
        logger.critical(f"Detalles: {str(e)}", exc_info=True)
        return 1
        
    finally:
        # Limpiar recursos
        if monitor:
            try:
                monitor.stop()
                logger.debug("Monitor de recursos detenido")
            except Exception as e:
                logger.warning(f"Error al detener monitor: {e}")
        
        logger.info("Limpieza de recursos completada")
        logger.info("Asistente AGP finalizado")


if __name__ == "__main__":
    sys.exit(main())
