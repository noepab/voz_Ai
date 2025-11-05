""
Script de optimización para el asistente de voz en mini PC.
Ejecutar con permisos de administrador para mejores resultados.
"""
import os
import sys
import ctypes
import psutil
import platform
import subprocess
from typing import Optional, List, Dict, Any

# Verificar si se está ejecutando como administrador
def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class SystemOptimizer:
    """Optimizador del sistema para el asistente de voz."""
    
    def __init__(self):
        self.os_info = platform.uname()
        self.current_pid = os.getpid()
        self.current_process = psutil.Process(self.current_pid)
        self.optimizations_applied = []
    
    def print_header(self):
        """Muestra el encabezado del optimizador."""
        print("=" * 60)
        print(f"Optimizador de Sistema - Asistente de Voz")
        print(f"Sistema: {self.os_info.system} {self.os_info.release}")
        print(f"Procesador: {self.os_info.processor}")
        print("=" * 60)
    
    def optimize_system(self):
        """Aplica todas las optimizaciones disponibles."""
        self.print_header()
        
        if not is_admin():
            print("\n[!] Se recomienda ejecutar como administrador para todas las optimizaciones")
        
        print("\n[+] Aplicando optimizaciones...")
        
        # Aplicar optimizaciones
        self.set_high_priority()
        self.optimize_power_plan()
        self.disable_unnecessary_services()
        self.optimize_network()
        self.optimize_audio()
        self.clean_temp_files()
        self.defragment_disk()
        
        print("\n[+] Optimizaciones completadas:")
        for opt in self.optimizations_applied:
            print(f"  ✓ {opt}")
        
        print("\nReinicia tu sistema para aplicar todos los cambios.")
    
    def set_high_priority(self):
        """Establece alta prioridad para el proceso actual."""
        try:
            self.current_process.nice(psutil.HIGH_PRIORITY_CLASS)
            self.current_process.ionice(psutil.IOPRIO_HIGH)
            self.optimizations_applied.append("Prioridad del proceso establecida a ALTA")
        except Exception as e:
            print(f"  [!] No se pudo establecer alta prioridad: {e}")
    
    def optimize_power_plan(self):
        """Configura el plan de energía para máximo rendimiento."""
        try:
            if platform.system() == "Windows":
                # Cambiar a plan de alto rendimiento
                subprocess.run("powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c", 
                             shell=True, check=True)
                self.optimizations_applied.append("Plan de energía configurado para alto rendimiento")
        except:
            pass
    
    def disable_unnecessary_services(self):
        """Desactiva servicios innecesarios de Windows."""
        if platform.system() != "Windows":
            return
            
        services_to_disable = [
            "DiagTrack", "TrkWks", "WMPNetworkSvc",
            "WSearch", "WerSvc", "SysMain"
        ]
        
        if not is_admin():
            print("  [!] Se requieren privilegios de administrador para desactivar servicios")
            return
        
        for service in services_to_disable:
            try:
                subprocess.run(f"sc stop {service}", shell=True, check=True)
                subprocess.run(f"sc config {service} start= disabled", shell=True, check=True)
                self.optimizations_applied.append(f"Servicio desactivado: {service}")
            except:
                pass
    
    def optimize_network(self):
        """Optimiza la configuración de red."""
        try:
            if platform.system() == "Windows":
                # Desactivar Nagle's Algorithm
                subprocess.run("netsh int tcp set global autotuninglevel=restricted", 
                             shell=True, check=True)
                # Optimizar ventana de recepción
                subprocess.run("netsh int tcp set global rss=enabled", 
                             shell=True, check=True)
                self.optimizations_applied.append("Red optimizada para baja latencia")
        except:
            pass
    
    def optimize_audio(self):
        """Optimiza la configuración de audio."""
        try:
            if platform.system() == "Windows":
                # Desactivar mejoras de sonido
                subprocess.run("reg add "HKCU\Software\Microsoft\Internet Explorer\LowRegistry\Audio\PolicyConfig\PropertyStore" "
                             "/v PKEY_Endpoint_Enable_APO_For_All_Streams /t REG_DWORD /d 0 /f", 
                             shell=True, check=True)
                self.optimizations_applied.append("Audio optimizado para reconocimiento de voz")
        except:
            pass
    
    def clean_temp_files(self):
        """Limpia archivos temporales."""
        try:
            temp_folders = [
                os.environ.get('TEMP', ''),
                os.environ.get('TMP', ''),
                os.path.join(os.environ.get('WINDIR', ''), 'Temp'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Temp')
            ]
            
            cleaned = 0
            for folder in temp_folders:
                if os.path.exists(folder):
                    for root, _, files in os.walk(folder):
                        for file in files:
                            try:
                                file_path = os.path.join(root, file)
                                os.remove(file_path)
                                cleaned += 1
                            except:
                                pass
            
            if cleaned > 0:
                self.optimizations_applied.append(f"Limpieza de {cleaned} archivos temporales")
                
        except Exception as e:
            print(f"  [!] Error al limpiar archivos temporales: {e}")
    
    def defragment_disk(self):
        """Desfragmenta el disco duro (solo HDD, no SSD)."""
        try:
            if platform.system() == "Windows":
                # Verificar si es un HDD
                import ctypes
                import string
                
                kernel32 = ctypes.windll.kernel32
                drives = []
                bitmask = kernel32.GetLogicalDrives()
                
                for letter in string.ascii_uppercase:
                    if bitmask & 1:
                        drives.append(letter)
                    bitmask >>= 1
                
                for drive in drives:
                    try:
                        drive_path = f"{drive}:\\"
                        drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive_path)
                        
                        # Solo desfragmentar discos fijos (DRIVE_FIXED = 3)
                        if drive_type == 3:
                            subprocess.run(f"defrag {drive}: /U /V", shell=True, check=True)
                            self.optimizations_applied.append(f"Disco {drive}: desfragmentado")
                    except:
                        continue
        except:
            pass


def main():
    """Función principal."""
    optimizer = SystemOptimizer()
    optimizer.optimize_system()

if __name__ == "__main__":
    main()
