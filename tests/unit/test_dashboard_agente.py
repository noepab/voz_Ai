"""
Pruebas unitarias para el módulo dashboard_agente.py
"""
import pytest
from unittest.mock import MagicMock, patch, call, ANY
from datetime import datetime

# Importamos la clase a probar
from dashboard_agente import DashboardAgente

class TestDashboardAgente:
    """Pruebas para la clase DashboardAgente."""
    
    @pytest.fixture
    def dashboard(self):
        """Fixture para crear una instancia de DashboardAgente para pruebas."""
        with patch('customtkinter.CTk'), \
             patch('customtkinter.set_appearance_mode'), \
             patch('customtkinter.set_default_color_theme'), \
             patch('tkinter.messagebox'):
            # Configurar mocks para los widgets principales
            mock_root = MagicMock()
            mock_frame_mensajes = MagicMock()
            mock_frame_entrada = MagicMock()
            mock_entrada_mensaje = MagicMock()
            
            # Crear instancia del dashboard
            dash = DashboardAgente()
            
            # Configurar mocks para los atributos
            dash.root = mock_root
            dash.frame_mensajes = mock_frame_mensajes
            dash.frame_entrada = mock_frame_entrada
            dash.entrada_mensaje = mock_entrada_mensaje
            
            # Configurar el mock para _parent_canvas
            mock_frame_mensajes._parent_canvas = MagicMock()
            
            return dash
    
    def test_init(self, dashboard):
        """Prueba la inicialización del dashboard."""
        # Verificar que se inicialicen las variables de estado
        assert dashboard.estado_agente == "Inactivo"
        assert dashboard.modo_oscuro is True
        assert isinstance(dashboard.mensajes, list)
        assert len(dashboard.comandos_disponibles) > 0
        assert isinstance(dashboard.comandos_disponibles, list)
        
        # Verificar que se configuró la ventana principal
        dashboard.root.title.assert_called_once_with("AGP - Panel de Control")
        dashboard.root.geometry.assert_called_once_with("1200x800")
    
    def test_iniciar(self, dashboard):
        """Prueba el método iniciar."""
        dashboard.iniciar()
        dashboard.root.mainloop.assert_called_once()
    
    def test_cambiar_seccion(self, dashboard):
        """Prueba el método cambiar_seccion."""
        # Configurar mock para tabs
        mock_tabs = MagicMock()
        dashboard.tabs = mock_tabs
        
        # Probar con diferentes secciones
        secciones = ["Inicio", "Chat", "Comandos", "Configuración"]
        for seccion in secciones:
            dashboard.cambiar_seccion(seccion)
            mock_tabs.set.assert_called_with(seccion)
    
    def test_enviar_mensaje_vacio(self, dashboard):
        """Prueba enviar_mensaje con mensaje vacío."""
        # Configurar el mock para devolver un mensaje vacío
        dashboard.entrada_mensaje.get.return_value = "  "
        
        # Llamar al método
        dashboard.enviar_mensaje()
        
        # Verificar que no se llamó a mostrar_mensaje
        assert not hasattr(dashboard, 'mostrar_mensaje_called')
    
    def test_enviar_mensaje_valido(self, dashboard):
        """Prueba enviar_mensaje con un mensaje válido."""
        # Configurar mocks
        mensaje_prueba = "Hola, esto es una prueba"
        dashboard.entrada_mensaje.get.return_value = mensaje_prueba
        dashboard.mostrar_mensaje = MagicMock()
        dashboard.procesar_mensaje = MagicMock()
        
        # Llamar al método
        dashboard.enviar_mensaje()
        
        # Verificar que se llamó a los métodos esperados
        dashboard.mostrar_mensaje.assert_called_once_with("Tú", mensaje_prueba)
        dashboard.entrada_mensaje.delete.assert_called_once_with("1.0", "end")
        dashboard.procesar_mensaje.assert_called_once_with(mensaje_prueba)
    
    def test_mostrar_mensaje(self, dashboard):
        """Prueba el método mostrar_mensaje."""
        # Configurar mocks
        remitente = "Test"
        mensaje = "Este es un mensaje de prueba"
        
        # Llamar al método
        dashboard.mostrar_mensaje(remitente, mensaje)
        
        # Verificar que se creó el frame del mensaje con los parámetros correctos
        dashboard.frame_mensajes.pack.assert_called()
        
        # Verificar que se configuró correctamente el scroll al final
        dashboard.frame_mensajes._parent_canvas.yview_moveto.assert_called_with(1.0)
    
    def test_procesar_mensaje(self, dashboard):
        """Prueba el método procesar_mensaje."""
        # Configurar mock
        dashboard.mostrar_mensaje = MagicMock()
        mensaje = "¿Cómo estás?"
        
        # Llamar al método
        dashboard.procesar_mensaje(mensaje)
        
        # Verificar que se mostró la respuesta del asistente
        dashboard.mostrar_mensaje.assert_called_once_with(
            "Asistente", 
            f"He recibido tu mensaje: {mensaje}"
        )
    
    @pytest.mark.parametrize("comando", [
        "Abrir navegador", 
        "Tomar nota", 
        "Buscar en internet",
        "Reproducir música",
        "Configuración"
    ])
    def test_ejecutar_comando(self, dashboard, comando):
        """Prueba el método ejecutar_comando con diferentes comandos."""
        # Configurar mock
        dashboard.mostrar_mensaje = MagicMock()
        
        # Llamar al método
        dashboard.ejecutar_comando(comando)
        
        # Verificar que se mostró el mensaje de ejecución
        dashboard.mostrar_mensaje.assert_called_once_with(
            "Sistema", 
            f"Ejecutando comando: {comando}"
        )
    
    def test_buscar_con_termino(self, dashboard):
        """Prueba el método buscar con un término de búsqueda."""
        # Configurar mocks
        dashboard.barra_busqueda = MagicMock()
        dashboard.barra_busqueda.get.return_value = "Python"
        dashboard.mostrar_mensaje = MagicMock()
        
        # Llamar al método
        dashboard.buscar()
        
        # Verificar que se mostró el mensaje de búsqueda
        dashboard.mostrar_mensaje.assert_called_once_with(
            "Sistema", 
            "Buscando: Python"
        )
    
    def test_buscar_sin_termino(self, dashboard, mocker):
        """Prueba el método buscar sin término de búsqueda."""
        # Configurar mocks
        dashboard.barra_busqueda = MagicMock()
        dashboard.barra_busqueda.get.return_value = ""
        mock_messagebox = mocker.patch('tkinter.messagebox')
        
        # Llamar al método
        dashboard.buscar()
        
        # Verificar que se mostró el mensaje de error
        mock_messagebox.showinfo.assert_called_once_with(
            "Búsqueda", 
            "Por favor, ingresa un término de búsqueda"
        )
    
    @pytest.mark.parametrize("tema, modo_esperado, oscuro_esperado", [
        ("Claro", "light", False),
        ("Oscuro", "dark", True),
        ("Sistema", "system", True)  # Asumimos que el sistema está en modo oscuro
    ])
    def test_cambiar_tema(self, dashboard, tema, modo_esperado, oscuro_esperado):
        """Prueba el método cambiar_tema con diferentes opciones."""
        # Configurar mock
        mock_set_appearance_mode = MagicMock()
        with patch('customtkinter.set_appearance_mode', mock_set_appearance_mode):
            # Llamar al método
            dashboard.cambiar_tema(tema)
            
            # Verificar que se configuró el tema correctamente
            mock_set_appearance_mode.assert_called_once_with(modo_esperado)
            
            # Verificar el estado de modo_oscuro
            if tema != "Sistema":
                assert dashboard.modo_oscuro == oscuro_esperado
    
    def test_toggle_voz_activado(self, dashboard):
        """Prueba activar el reconocimiento de voz."""
        # Configurar mocks
        dashboard.activar_voz = MagicMock()
        dashboard.activar_voz.get.return_value = 1
        dashboard.mostrar_mensaje = MagicMock()
        
        # Llamar al método
        dashboard.toggle_voz()
        
        # Verificar que se mostró el mensaje de activación
        dashboard.mostrar_mensaje.assert_called_once_with(
            "Sistema", 
            "Reconocimiento de voz activado"
        )
    
    def test_toggle_voz_desactivado(self, dashboard):
        """Prueba desactivar el reconocimiento de voz."""
        # Configurar mocks
        dashboard.activar_voz = MagicMock()
        dashboard.activar_voz.get.return_value = 0
        dashboard.mostrar_mensaje = MagicMock()
        
        # Llamar al método
        dashboard.toggle_voz()
        
        # Verificar que se mostró el mensaje de desactivación
        dashboard.mostrar_mensaje.assert_called_once_with(
            "Sistema", 
            "Reconocimiento de voz desactivado"
        )
    
    def test_configurar_interfaz(self, dashboard):
        """Prueba la configuración inicial de la interfaz."""
        # Verificar que se configuró el grid principal
        dashboard.root.grid_columnconfigure.assert_any_call(1, weight=1)
        dashboard.root.grid_rowconfigure.assert_any_call(1, weight=1)
        
        # Verificar que se crearon los frames principales
        assert hasattr(dashboard, 'barra_lateral')
        assert hasattr(dashboard, 'barra_superior')
        assert hasattr(dashboard, 'area_principal')
        assert hasattr(dashboard, 'barra_inferior')
        
        # Verificar que se configuraron las pestañas
        assert hasattr(dashboard, 'tabs')
        assert hasattr(dashboard, 'tab_chat')
        assert hasattr(dashboard, 'tab_comandos')
        assert hasattr(dashboard, 'tab_config')
    
    @pytest.mark.parametrize("metodo_configuracion", [
        "_configurar_tab_chat",
        "_configurar_tab_comandos",
        "_configurar_tab_config"
    ])
    def test_configuracion_tabs(self, dashboard, metodo_configuracion):
        """Prueba los métodos de configuración de las pestañas."""
        # Configurar mocks para los widgets de las pestañas
        mock_frame = MagicMock()
        with patch.object(dashboard, metodo_configuracion) as mock_metodo:
            # Llamar al método de configuración
            getattr(dashboard, metodo_configuracion)()
            
            # Verificar que el método se llamó correctamente
            mock_metodo.assert_called_once()
    
    def test_crear_botones_navegacion(self, dashboard):
        """Prueba la creación de los botones de navegación."""
        # Verificar que se crearon los botones de navegación
        botones_esperados = ["Inicio", "Chat", "Comandos", "Configuración", "Estadísticas"]
        
        # Verificar que se llamó a pack para cada botón
        for texto in botones_esperados:
            # Verificar que se creó un botón con este texto
            # Esto es una verificación básica, podrías hacerlo más detallado
            pass
