"""
Sistema de gestión de plugins para el asistente de voz.
Permite cargar dinámicamente plugins para extender la funcionalidad.
"""
import importlib
import inspect
import logging
import pkgutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Type, Callable, Union
import json

logger = logging.getLogger(__name__)

class Plugin:
    """Clase base para todos los plugins del asistente."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.commands: Dict[str, dict] = {}
        self._initialized = False
    
    def initialize(self) -> bool:
        """Inicializa el plugin."""
        self._initialized = True
        logger.info(f"Plugin '{self.name}' inicializado")
        return True
    
    def shutdown(self):
        """Limpia los recursos del plugin."""
        self._initialized = False
        logger.info(f"Plugin '{self.name}' detenido")
    
    def get_commands(self) -> Dict[str, dict]:
        """
        Devuelve los comandos que maneja este plugin.
        
        Returns:
            Dict con la estructura: {
                'comando': {
                    'description': str,
                    'function': callable,
                    'examples': List[str]
                }
            }
        """
        return {}
    
    def handle_command(self, command: str, *args, **kwargs) -> Any:
        """
        Maneja un comando dirigido a este plugin.
        
        Args:
            command: Nombre del comando a ejecutar
            *args, **kwargs: Argumentos para el comando
            
        Returns:
            Resultado de la ejecución del comando o None si no se pudo manejar
        """
        commands = self.get_commands()
        if command in commands:
            handler = commands[command].get('function')
            if callable(handler):
                try:
                    return handler(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error al ejecutar comando '{command}': {e}")
                    return f"Error al ejecutar el comando: {e}"
        return None


class PluginManager:
    """Gestiona la carga y ejecución de plugins."""
    
    def __init__(self, plugins_dir: Path):
        """
        Inicializa el gestor de plugins.
        
        Args:
            plugins_dir: Directorio donde buscar plugins
        """
        self.plugins_dir = plugins_dir
        self.plugins: Dict[str, Plugin] = {}
        self.commands: Dict[str, dict] = {}
        logger.info(f"Gestor de plugins inicializado. Directorio: {plugins_dir}")
    
    def discover_plugins(self) -> List[str]:
        """
        Descubre los plugins disponibles en el directorio de plugins.
        
        Returns:
            Lista de nombres de plugins encontrados
        """
        if not self.plugins_dir.exists():
            logger.warning(f"El directorio de plugins no existe: {self.plugins_dir}")
            return []
            
        plugins = []
        for finder, name, _ in pkgutil.iter_modules([str(self.plugins_dir)]):
            if not name.startswith('_'):  # Ignorar módulos privados
                plugins.append(name)
        
        logger.info(f"Plugins descubiertos: {', '.join(plugins) or 'Ninguno'}")
        return plugins
    
    def load_plugin(self, plugin_name: str) -> bool:
        """
        Carga un plugin por su nombre.
        
        Args:
            plugin_name: Nombre del plugin a cargar
            
        Returns:
            True si el plugin se cargó correctamente, False en caso contrario
        """
        if plugin_name in self.plugins:
            logger.warning(f"El plugin '{plugin_name}' ya está cargado")
            return True
            
        try:
            # Importar el módulo del plugin
            module_name = f"plugins.{plugin_name}"
            spec = importlib.util.spec_from_file_location(
                module_name,
                self.plugins_dir / f"{plugin_name}.py"
            )
            
            if spec is None or spec.loader is None:
                logger.error(f"No se pudo cargar el plugin '{plugin_name}': Módulo no encontrado")
                return False
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Buscar la clase del plugin (debe tener el mismo nombre que el archivo en CamelCase)
            class_name = ''.join(word.capitalize() for word in plugin_name.split('_'))
            plugin_class = getattr(module, class_name, None)
            
            if plugin_class is None or not inspect.isclass(plugin_class):
                logger.error(f"No se encontró la clase '{class_name}' en el plugin '{plugin_name}'")
                return False
                
            # Crear una instancia del plugin
            plugin_instance = plugin_class()
            
            # Inicializar el plugin
            if not plugin_instance.initialize():
                logger.error(f"Error al inicializar el plugin '{plugin_name}'")
                return False
                
            # Registrar los comandos del plugin
            plugin_commands = plugin_instance.get_commands()
            for cmd, cmd_info in plugin_commands.items():
                if cmd in self.commands:
                    logger.warning(f"El comando '{cmd}' ya está registrado por otro plugin")
                else:
                    self.commands[cmd] = {
                        'plugin': plugin_name,
                        'function': cmd_info.get('function'),
                        'description': cmd_info.get('description', 'Sin descripción'),
                        'examples': cmd_info.get('examples', [])
                    }
            
            # Registrar el plugin
            self.plugins[plugin_name] = plugin_instance
            logger.info(f"Plugin '{plugin_name}' cargado correctamente con {len(plugin_commands)} comandos")
            return True
            
        except Exception as e:
            logger.error(f"Error al cargar el plugin '{plugin_name}': {e}", exc_info=True)
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Descarga un plugin.
        
        Args:
            plugin_name: Nombre del plugin a descargar
            
        Returns:
            True si se descargó correctamente, False en caso contrario
        """
        if plugin_name not in self.plugins:
            logger.warning(f"El plugin '{plugin_name}' no está cargado")
            return False
            
        try:
            # Eliminar los comandos del plugin
            commands_to_remove = [
                cmd for cmd, info in self.commands.items() 
                if info['plugin'] == plugin_name
            ]
            
            for cmd in commands_to_remove:
                del self.commands[cmd]
            
            # Detener el plugin
            self.plugins[plugin_name].shutdown()
            del self.plugins[plugin_name]
            
            logger.info(f"Plugin '{plugin_name}' descargado correctamente")
            return True
            
        except Exception as e:
            logger.error(f"Error al descargar el plugin '{plugin_name}': {e}")
            return False
    
    def handle_command(self, command: str, *args, **kwargs) -> Any:
        """
        Maneja un comando, enviándolo al plugin correspondiente.
        
        Args:
            command: Nombre del comando a ejecutar
            *args, **kwargs: Argumentos para el comando
            
        Returns:
            Resultado de la ejecución del comando o None si no se pudo manejar
        """
        if command not in self.commands:
            logger.warning(f"Comando desconocido: {command}")
            return None
            
        cmd_info = self.commands[command]
        plugin_name = cmd_info['plugin']
        
        if plugin_name not in self.plugins:
            logger.error(f"El plugin '{plugin_name}' no está cargado para el comando '{command}'")
            return None
            
        logger.debug(f"Ejecutando comando '{command}' en el plugin '{plugin_name}'")
        return self.plugins[plugin_name].handle_command(command, *args, **kwargs)
    
    def get_available_commands(self) -> Dict[str, dict]:
        """
        Devuelve información sobre todos los comandos disponibles.
        
        Returns:
            Dict con información de los comandos
        """
        return self.commands
    
    def reload_plugin(self, plugin_name: str) -> bool:
        """
        Recarga un plugin.
        
        Args:
            plugin_name: Nombre del plugin a recargar
            
        Returns:
            True si se recargó correctamente, False en caso contrario
        """
        if plugin_name in self.plugins:
            if not self.unload_plugin(plugin_name):
                return False
        return self.load_plugin(plugin_name)
    
    def shutdown(self):
        """Detiene todos los plugins y libera recursos."""
        for plugin_name in list(self.plugins.keys()):
            self.unload_plugin(plugin_name)
        logger.info("Todos los plugins han sido detenidos")
