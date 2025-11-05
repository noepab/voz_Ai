from config import MODEL_PATH, WAKE_WORDS, TIMEOUT
from interfaz_simple import AsistenteVentana
from reconocimiento import start_audio_worker
from tts import start_tts_worker, hablar
from comandos import start_comando_worker
import queue
import vosk
import sys
import threading
from core.resource_monitor import ResourceMonitor

def main():
    print("Arrancando AGP Asistente Voz Modular...")
    
    # Inicializar colas
    audio_q = queue.Queue()
    comando_q = queue.Queue()
    tts_q = queue.Queue()
    
    # Inicializar modelo Vosk
    try:
        print(f"\n=== Inicializando modelo de voz ===")
        print(f"Ruta del modelo: {MODEL_PATH}")
        
        # Verificar que el directorio del modelo existe
        import os
        if not os.path.exists(MODEL_PATH):
            print(f"¡Error! No se encontró el modelo en la ruta: {MODEL_PATH}")
            print("Por favor, asegúrate de que el modelo Vosk para español esté descargado")
            print("y extraído en la carpeta 'models' del directorio del proyecto.")
            print("Puedes descargarlo desde: https://alphacephei.com/vosk/models")
            sys.exit(1)
        
        # Cargar el modelo
        print("Cargando modelo de reconocimiento de voz...")
        model = vosk.Model(MODEL_PATH)
        
        # Crear el reconocedor
        sample_rate = 16000
        rec = vosk.KaldiRecognizer(model, sample_rate)
        rec.SetWords(True)  # Habilitar reconocimiento de palabras
        
        print("Modelo de voz cargado correctamente.")
        print(f"Tasa de muestreo: {sample_rate} Hz")
        
    except Exception as e:
        print(f"\n=== Error al cargar el modelo de voz ===")
        print(f"Tipo de error: {type(e).__name__}")
        print(f"Mensaje: {str(e)}")
        print("\nPosibles soluciones:")
        print("1. Verifica que el modelo esté correctamente descargado y extraído.")
        print("2. Asegúrate de que la ruta al modelo sea correcta.")
        print("3. Prueba a descargar el modelo nuevamente desde:")
        print("   https://alphacephei.com/vosk/models")
        print("4. Extrae el contenido del archivo ZIP en la carpeta 'models'.")
        sys.exit(1)
    
    # Lanzar workers
    start_audio_worker(audio_q, rec, comando_q)  # Pasamos la cola de comandos
    start_comando_worker(comando_q)
    start_tts_worker(tts_q)
    
    # Inicializar interfaz
    try:
        # Crear la instancia de la interfaz
        asistente = AsistenteVentana()
        
        # Configurar el cierre de la aplicación
        def on_closing():
            print("\nCerrando el asistente...")
            asistente.root.quit()
            sys.exit(0)
            
        asistente.root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Función para iniciar el asistente
        def iniciar_asistente():
            print("\nAsistente listo. Di una palabra de activación como 'autogestión' o 'asistente'")
            hablar("Asistente AGP activado. Di mi nombre para empezar.")
        
        # Iniciar el asistente después de que la interfaz esté lista
        asistente.root.after(1000, iniciar_asistente)
        
        # Iniciar el bucle principal de la interfaz
        asistente.root.mainloop()
    except KeyboardInterrupt:
        print("\nDeteniendo el asistente...")
        sys.exit(0)

if __name__ == "__main__":
    main()
