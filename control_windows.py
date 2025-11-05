"""
Módulo para controlar Windows mediante comandos de voz.
Incluye funciones para controlar aplicaciones, sistema de archivos, volumen, etc.
"""

import os
import sys
import subprocess
import pyautogui
import psutil
import pygetwindow as gw
import keyboard
import time
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

class ControlWindows:
    def __init__(self):
        # Configuración de seguridad de PyAutoGUI
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
        # Inicializar control de volumen
        self.dispositivos_audio = AudioUtilities.GetSpeakers()
        self.interface_audio = self.dispositivos_audio.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volumen = cast(self.interface_audio, POINTER(IAudioEndpointVolume))
    
    # --- Control de Aplicaciones ---
    def abrir_aplicacion(self, nombre_app):
        """Abre una aplicación por su nombre."""
        try:
            # Diccionario de aplicaciones comunes
            apps = {
                'calculadora': 'calc.exe',
                'bloc de notas': 'notepad.exe',
                'explorador': 'explorer.exe',
                'word': 'winword.exe',
                'excel': 'excel.exe',
                'powerpoint': 'powerpnt.exe',
                'chrome': 'chrome.exe',
                'edge': 'msedge.exe',
                'firefox': 'firefox.exe',
                'configuración': 'ms-settings:',
                'cmd': 'cmd.exe',
                'powershell': 'powershell.exe'
            }
            
            # Verificar si la aplicación está en el diccionario
            if nombre_app.lower() in apps:
                app = apps[nombre_app.lower()]
                if app.startswith('ms-'):
                    os.system(f'start {app}')
                else:
                    os.startfile(app)
                return f"Abriendo {nombre_app}"
            else:
                # Intentar abrir cualquier otra aplicación
                try:
                    os.startfile(nombre_app)
                    return f"Intentando abrir {nombre_app}"
                except:
                    return f"No se pudo abrir {nombre_app}. Intenta con el nombre exacto del ejecutable."
        except Exception as e:
            return f"Error al abrir la aplicación: {str(e)}"
    
    def cerrar_aplicacion(self, nombre_app):
        """Cierra una aplicación por su nombre."""
        try:
            # Cerrar por nombre de proceso
            for proc in psutil.process_iter(['name']):
                if nombre_app.lower() in proc.info['name'].lower():
                    proc.terminate()
                    return f"Cerrando {nombre_app}"
            return f"No se encontró la aplicación {nombre_app} en ejecución"
        except Exception as e:
            return f"Error al cerrar la aplicación: {str(e)}"
    
    def cambiar_ventana(self, titulo=None):
        """Cambia a una ventana específica o muestra las ventanas abiertas."""
        try:
            if titulo:
                ventanas = gw.getWindowsWithTitle(titulo)
                if ventanas:
                    ventana = ventanas[0]
                    if ventana.isMinimized:
                        ventana.restore()
                    ventana.activate()
                    return f"Cambiando a {titulo}"
                else:
                    return f"No se encontró la ventana: {titulo}"
            else:
                # Mostrar lista de ventanas abiertas
                ventanas = gw.getAllTitles()
                return "Ventanas abiertas: " + ", ".join([v for v in ventanas if v])
        except Exception as e:
            return f"Error al cambiar de ventana: {str(e)}"
    
    # --- Control de Volumen y Multimedia ---
    def ajustar_volumen(self, nivel=None):
        """Ajusta el volumen del sistema."""
        try:
            if nivel is None:
                return f"El volumen actual es al {int(self.volumen.GetMasterVolumeLevelScalar() * 100)}%"
            
            nivel = max(0, min(100, int(nivel)))
            self.volumen.SetMasterVolumeLevelScalar(nivel / 100, None)
            return f"Volumen ajustado al {nivel}%"
        except Exception as e:
            return f"Error al ajustar el volumen: {str(e)}"
    
    def silenciar_volumen(self):
        """Silencia o activa el sonido."""
        try:
            estado_actual = self.volumen.GetMute()
            self.volumen.SetMute(not estado_actual, None)
            return "Sonido silenciado" if not estado_actual else "Sonido activado"
        except Exception as e:
            return f"Error al silenciar el volumen: {str(e)}"
    
    # --- Control de Sistema ---
    def apagar_sistema(self, accion="apagar", tiempo=0):
        """Controla el estado del sistema."""
        try:
            if tiempo > 0:
                tiempo_segundos = tiempo * 60  # Convertir minutos a segundos
                comando = f"shutdown /s /t {tiempo_segundos}" if accion == "apagar" else f"shutdown /r /t {tiempo_segundos}"
                subprocess.run(comando, shell=True)
                return f"El sistema se {accion}á en {tiempo} minutos"
            else:
                if accion == "apagar":
                    subprocess.run("shutdown /s /t 0", shell=True)
                    return "Apagando el sistema..."
                elif accion == "reiniciar":
                    subprocess.run("shutdown /r /t 0", shell=True)
                    return "Reiniciando el sistema..."
                elif accion == "suspender":
                    os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
                    return "Poniendo el sistema en suspensión..."
        except Exception as e:
            return f"Error al {accion} el sistema: {str(e)}"
    
    # --- Control de Archivos ---
    def abrir_archivo(self, ruta):
        """Abre un archivo con su aplicación predeterminada."""
        try:
            if os.path.exists(ruta):
                os.startfile(ruta)
                return f"Abriendo {os.path.basename(ruta)}"
            else:
                return f"No se encontró el archivo: {ruta}"
        except Exception as e:
            return f"Error al abrir el archivo: {str(e)}"
    
    def buscar_archivo(self, nombre, directorio="C:\\"):
        """Busca un archivo en el sistema."""
        try:
            # Limitamos la búsqueda a 3 niveles de profundidad por rendimiento
            resultados = []
            for raiz, dirs, archivos in os.walk(directorio, topdown=True):
                nivel = raiz.count(os.sep)
                if nivel > 3:  # Límite de profundidad
                    dirs[:] = []  # No recorrer subdirectorios
                    continue
                
                for archivo in archivos:
                    if nombre.lower() in archivo.lower():
                        resultados.append(os.path.join(raiz, archivo))
                        if len(resultados) >= 5:  # Límite de resultados
                            break
                
                if len(resultados) >= 5:
                    break
            
            if resultados:
                return "Archivos encontrados:\n" + "\n".join(resultados[:5])
            else:
                return f"No se encontraron archivos que coincidan con: {nombre}"
        except Exception as e:
            return f"Error al buscar archivos: {str(e)}"
    
    # --- Accesos directos ---
    def ejecutar_comando(self, comando):
        """Ejecuta un comando de Windows."""
        try:
            resultado = subprocess.run(
                comando,
                shell=True,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            return resultado.stdout or "Comando ejecutado correctamente"
        except Exception as e:
            return f"Error al ejecutar el comando: {str(e)}"
    
    # --- Control de Entrada ---
    def escribir_texto(self, texto):
        """Escribe texto en la posición actual del cursor."""
        try:
            pyautogui.write(texto, interval=0.1)
            return "Texto escrito correctamente"
        except Exception as e:
            return f"Error al escribir texto: {str(e)}"
    
    def presionar_tecla(self, tecla):
        """Presiona una tecla o combinación de teclas."""
        try:
            keyboard.press_and_release(tecla)
            return f"Tecla {tecla} presionada"
        except Exception as e:
            return f"Error al presionar la tecla: {str(e)}"

# Ejemplo de uso
if __name__ == "__main__":
    control = ControlWindows()
    print(control.abrir_aplicacion("calculadora"))
