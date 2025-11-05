"""
Plugin de sistema para comandos básicos del asistente.
"""
import os
import platform
import datetime
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from ..core.plugin_manager import Plugin

logger = logging.getLogger(__name__)

class SystemPlugin(Plugin):
    """Plugin para comandos del sistema."""
    
    def __init__(self):
        super().__init__(
            name="system",
            description="Comandos básicos del sistema"
        )
        self.start_time = datetime.datetime.now()
    
    def get_commands(self) -> Dict[str, dict]:
        """Devuelve los comandos que maneja este plugin."""
        return {
            "hora": {
                "function": self.get_time,
                "description": "Dice la hora actual",
                "examples": ["¿Qué hora es?", "Dime la hora"]
            },
            "fecha": {
                "function": self.get_date,
                "description": "Dice la fecha actual",
                "examples": ["¿Qué día es hoy?", "Dime la fecha"]
            },
            "estado": {
                "function": self.get_status,
                "description": "Muestra el estado del asistente",
                "examples": ["¿Cómo estás?", "Estado del sistema"]
            },
            "apagar": {
                "function": self.shutdown,
                "description": "Apaga el asistente",
                "examples": ["Apágate", "Cierra el programa"]
            }
        }
    
    def get_time(self) -> str:
        """Devuelve la hora actual."""
        now = datetime.datetime.now()
        return f"Son las {now.hour} y {now.minute:02d}"
    
    def get_date(self) -> str:
        """Devuelve la fecha actual."""
        days = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
        months = [
            "enero", "febrero", "marzo", "abril", "mayo", "junio",
            "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
        ]
        
        now = datetime.datetime.now()
        return f"Hoy es {days[now.weekday()]}, {now.day} de {months[now.month-1]} de {now.year}"
    
    def get_status(self) -> str:
        """Devuelve el estado del sistema."""
        uptime = datetime.datetime.now() - self.start_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, _ = divmod(remainder, 60)
        
        status = [
            f"Estoy funcionando correctamente.",
            f"Tiempo activa: {hours} horas y {minutes} minutos.",
            f"Sistema: {platform.system()} {platform.release()}",
            f"Directorio actual: {os.getcwd()}"
        ]
        
        return " ".join(status)
    
    def shutdown(self) -> str:
        """Apaga el asistente."""
        return "shutdown"  # Palabra clave especial para apagar el asistente

# Función requerida para la carga del plugin
def setup() -> SystemPlugin:
    """Función de fábrica para crear una instancia del plugin."""
    return SystemPlugin()
