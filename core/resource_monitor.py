"""
Sistema avanzado de monitoreo y optimización de recursos.
"""
import os
import time
import psutil
import gc
import tracemalloc
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import threading
import numpy as np

class ResourceMonitor:
    """Monitor avanzado de recursos del sistema."""
    
    def __init__(self, max_memory_percent: float = 70.0):
        """
        Inicializa el monitor de recursos.
        
        Args:
            max_memory_percent: Porcentaje máximo de RAM permitido antes de optimizar
        """
        self.max_memory_percent = max_memory_percent
        self.running = False
        self.monitor_thread = None
        self.memory_history = []
        self.cpu_history = []
        self.max_history = 1000  # Número máximo de registros a mantener
        self.optimization_callbacks = []
        
        # Iniciar seguimiento de memoria
        tracemalloc.start()
        
        # Configurar alertas
        self.alert_thresholds = {
            'cpu': 85.0,  # Porcentaje
            'memory': 75.0,  # Porcentaje
            'disk': 90.0,  # Porcentaje
            'temperature': 80.0  # Grados Celsius
        }
        
        # Estadísticas
        self.start_time = time.time()
        self.last_optimize_time = 0
        self.optimize_cooldown = 300  # 5 minutos entre optimizaciones
    
    def start_monitoring(self, interval: float = 5.0):
        """Inicia el monitoreo en segundo plano."""
        if self.running:
            return
            
        self.running = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Detiene el monitoreo."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2.0)
    
    def _monitor_loop(self, interval: float):
        """Bucle principal de monitoreo."""
        while self.running:
            try:
                # Obtener métricas
                metrics = self.get_system_metrics()
                
                # Verificar alertas
                self._check_alerts(metrics)
                
                # Optimización automática si es necesario
                if metrics['memory_percent'] > self.max_memory_percent:
                    self.optimize_resources()
                
                # Historial
                self._update_history(metrics)
                
            except Exception as e:
                print(f"Error en el monitoreo: {e}")
                
            time.sleep(interval)
    
    def get_system_metrics(self) -> Dict[str, float]:
        """Obtiene métricas detalladas del sistema."""
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        return {
            'timestamp': time.time(),
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory_percent': process.memory_percent(),
            'memory_used_mb': memory_info.rss / (1024 * 1024),  # MB
            'disk_usage': psutil.disk_usage('/').percent,
            'cpu_temp': self._get_cpu_temperature(),
            'thread_count': process.num_threads(),
            'open_files': len(process.open_files()),
            'garbage': len(gc.garbage)
        }
    
    def _get_cpu_temperature(self) -> float:
        """Obtiene la temperatura de la CPU (soporte para Windows)."""
        try:
            import wmi
            w = wmi.WMI(namespace="root\wmi")
            temp_info = w.MSAcpi_ThermalZoneTemperature()[0]
            return (temp_info.CurrentTemperature / 10.0) - 273.15  # Kelvin a Celsius
        except:
            try:
                # Alternativa para Windows
                import wmi
                w = wmi.WMI()
                temp = w.Win32_PerfFormattedData_Counters_ThermalZoneInformation()[0].HighPrecisionTemperature
                return (temp / 10.0) - 273.15
            except:
                return 0.0  # No se pudo obtener la temperatura
    
    def _check_alerts(self, metrics: Dict[str, float]):
        """Verifica si se han superado los umbrales de alerta."""
        alerts = []
        
        if metrics['cpu_percent'] > self.alert_thresholds['cpu']:
            alerts.append(f"CPU alta: {metrics['cpu_percent']:.1f}%")
            
        if metrics['memory_percent'] > self.alert_thresholds['memory']:
            alerts.append(f"Memoria alta: {metrics['memory_percent']:.1f}%")
            
        if metrics['disk_usage'] > self.alert_thresholds['disk']:
            alerts.append(f"Disco lleno: {metrics['disk_usage']:.1f}%")
            
        if metrics['cpu_temp'] > self.alert_thresholds['temperature'] and metrics['cpu_temp'] > 0:
            alerts.append(f"Temperatura alta: {metrics['cpu_temp']:.1f}°C")
        
        if alerts:
            print("\n[31m[ALERTA] " + " | ".join(alerts) + "[0m\n")
    
    def _update_history(self, metrics: Dict[str, float]):
        """Actualiza el historial de métricas."""
        self.memory_history.append(metrics['memory_used_mb'])
        self.cpu_history.append(metrics['cpu_percent'])
        
        # Mantener el historial dentro del límite
        if len(self.memory_history) > self.max_history:
            self.memory_history.pop(0)
            self.cpu_history.pop(0)
    
    def optimize_resources(self):
        """Optimiza los recursos del sistema."""
        current_time = time.time()
        if (current_time - self.last_optimize_time) < self.optimize_cooldown:
            return
            
        self.last_optimize_time = current_time
        print("\n[33m[OPTIMIZACIÓN] Iniciando limpieza de recursos...[0m")
        
        # 1. Recolectar basura
        gc.collect()
        
        # 2. Limpiar caches de numpy
        try:
            import numpy as np
            np._globals._NoValue = np._NoValue
        except:
            pass
        
        # 3. Limpiar caches de importación
        import sys
        for module in list(sys.modules.keys()):
            if module.startswith('numpy.') or module.startswith('pandas.'):
                sys.modules[module].__dict__.clear()
        
        # 4. Limpiar caches de Python
        import functools
        for func in [f for f in gc.get_objects() if isinstance(f, functools._lru_cache_wrapper)]:
            func.cache_clear()
        
        # 5. Ejecutar callbacks de optimización
        for callback in self.optimization_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"Error en callback de optimización: {e}")
        
        print("\n[32m[OPTIMIZACIÓN] Limpieza completada[0m\n")
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Obtiene el uso de memoria detallado."""
        process = psutil.Process(os.getpid())
        mem = process.memory_info()
        
        return {
            'rss': mem.rss / (1024 * 1024),  # MB
            'vms': mem.vms / (1024 * 1024),   # MB
            'shared': mem.shared / (1024 * 1024),  # MB
            'text': mem.text / (1024 * 1024),  # MB
            'lib': mem.lib / (1024 * 1024),    # MB
            'data': mem.data / (1024 * 1024),  # MB
            'dirty': mem.dirty / (1024 * 1024)  # MB
        }
    
    def get_memory_summary(self) -> str:
        """Devuelve un resumen del uso de memoria."""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return (
            f"Memoria: {mem.percent}% usado ({mem.used/1024/1024:.1f} MB de {mem.total/1024/1024:.1f} MB)\n"
            f"Swap: {swap.percent}% usado ({swap.used/1024/1024:.1f} MB de {swap.total/1024/1024:.1f} MB)"
        )
    
    def register_optimization_callback(self, callback: callable):
        """Registra una función para llamar durante la optimización."""
        if callable(callback):
            self.optimization_callbacks.append(callback)
    
    def __del__(self):
        """Limpia los recursos al destruir el objeto."""
        self.stop_monitoring()
        tracemalloc.stop()


# Uso recomendado:
if __name__ == "__main__":
    monitor = ResourceMonitor(max_memory_percent=70.0)
    monitor.start_monitoring(interval=5.0)
    
    try:
        # Tu código aquí
        import time
        print("Monitoreo de recursos activo. Presiona Ctrl+C para salir.")
        while True:
            print(monitor.get_memory_summary())
            time.sleep(10)
    except KeyboardInterrupt:
        print("\nDeteniendo monitoreo...")
        monitor.stop_monitoring()
