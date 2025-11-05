"""
Interfaz avanzada para el asistente de voz AGP.
Utiliza CustomTkinter para una apariencia moderna y personalizable.
"""
import os
import sys
import time
import json
import threading
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime
from pathlib import Path
import psutil
import platform

# Importar CustomTkinter
import customtkinter as ctk
from PIL import Image, ImageTk
from typing import Optional, Dict, Any, List, Callable

# Configuración de temas
ctk.set_appearance_mode("Dark")  # Tema oscuro por defecto
ctk.set_default_color_theme("dark-blue")  # Tema azul oscuro

# Temas personalizados
TEMAS = {
    'Midnight Blue': {
        'bg': '#0f172a',
        'fg': '#f8fafc',
        'accent': '#3b82f6',
        'secondary': '#1e293b',
        'button': '#2563eb',
        'hover': '#1d4ed8',
        'text': '#ffffff',
        'border': '#334155',
        'success': '#10b981',
        'warning': '#f59e0b',
        'error': '#ef4444'
    },
    'Emerald Forest': {
        'bg': '#1b4332',
        'fg': '#d8f3dc',
        'accent': '#95d5b2',
        'secondary': '#2d6a4f',
        'button': '#40916c',
        'hover': '#52b788',
        'text': '#ffffff'
    },
    'Sunset Orange': {
        'bg': '#2b2d42',
        'fg': '#edf2f4',
        'accent': '#ef233c',
        'secondary': '#d90429',
        'button': '#ff7b00',
        'hover': '#ff8800',
        'text': '#ffffff'
    },
    'Deep Purple': {
        'bg': '#231942',
        'fg': '#e0b1cb',
        'accent': '#9f86c0',
        'secondary': '#5e548e',
        'button': '#be95c4',
        'hover': '#e0b1cb',
        'text': '#ffffff'
    },
    'Ocean Breeze': {
        'bg': '#0077b6',
        'fg': '#caf0f8',
        'accent': '#48cae4',
        'secondary': '#023e8a',
        'button': '#0096c7',
        'hover': '#00b4d8',
        'text': '#ffffff'
    },
    'Dark Mode': {
        'bg': '#121212',
        'fg': '#e0e0e0',
        'accent': '#bb86fc',
        'secondary': '#1e1e1e',
        'button': '#3700b3',
        'hover': '#6200ee',
        'text': '#ffffff'
    },
    'Light Mode': {
        'bg': '#f5f5f5',
        'fg': '#212121',
        'accent': '#6200ee',
        'secondary': '#e0e0e0',
        'button': '#bb86fc',
        'hover': '#9d4edd',
        'text': '#000000'
    },
    'Cyberpunk': {
        'bg': '#1a1a2e',
        'fg': '#ff2a6d',
        'accent': '#05d9e8',
        'secondary': '#2d00f7',
        'button': '#ff2a6d',
        'hover': '#d100d1',
        'text': '#ffffff'
    },
    'Nature Green': {
        'bg': '#2b580c',
        'fg': '#d8ebb5',
        'accent': '#a7beae',
        'secondary': '#4a6741',
        'button': '#5f8d4e',
        'hover': '#8bb174',
        'text': '#ffffff'
    },
    'Royal Gold': {
        'bg': '#1a1a1a',
        'fg': '#ffd700',
        'accent': '#daa520',
        'secondary': '#2a2a2a',
        'button': '#8b6914',
        'hover': '#b8860b',
        'text': '#ffffff'
    }
}

class InterfazAvanzada:
    """Interfaz avanzada para el asistente de voz."""
    
    def __init__(self, title: str = "AGP Asistente de Voz"):
        """Inicializa la interfaz avanzada."""
        self.root = ctk.CTk()
        self.root.title(title)
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)
        
        # Variables de estado
        self.escuchando = False
        self.hablando = False
        self.tema_actual = 'Dark Mode'  # Tema por defecto
        self.tema_oscuro = True
        self.volumen = 0.8
        self.velocidad = 1.0
        self.ultimos_comandos = []
        self.temas_disponibles = list(TEMAS.keys())
        
        # Configuración de fuentes
        self.fuente_titulo = ("Roboto", 24, "bold")
        self.fuente_subtitulo = ("Roboto", 14, "bold")
        self.fuente_normal = ("Segoe UI", 12)
        self.fuente_pequena = ("Segoe UI", 10)
        
        # Cargar recursos
        self._cargar_recursos()
        
        # Inicializar historial de mensajes
        self.historial_mensajes = []
        self.historial_archivo = None
        
        # Cargar preferencias
        self._cargar_preferencias()
        
        # Configurar la interfaz
        self._configurar_interfaz()
        
        # Iniciar actualización de estadísticas
        self._iniciar_actualizacion_estadisticas()
        
        # Cargar historial de la sesión actual
        self._cargar_historial_diario()
    
    def _cargar_recursos(self):
        """Carga los recursos gráficos necesarios o crea unos por defecto."""
        # Inicializar con valores por defecto
        self.icono = None
        self.logo = None
        self.img_microfono_on = None
        self.img_microfono_off = None
        
        try:
            # Intentar cargar los recursos si existen
            if os.path.exists("recursos/icono.png"):
                self.icono = ctk.CTkImage(
                    light_image=Image.open("recursos/icono.png"),
                    dark_image=Image.open("recursos/icono.png"),
                    size=(32, 32)
                )
                self.root.iconbitmap("recursos/icono.png")
                
            if os.path.exists("recursos/logo.png"):
                self.logo = ctk.CTkImage(
                    light_image=Image.open("recursos/logo.png"),
                    dark_image=Image.open("recursos/logo.png"),
                    size=(200, 200)
                )
                
            if os.path.exists("recursos/microfono_on.png"):
                self.img_microfono_on = ctk.CTkImage(
                    light_image=Image.open("recursos/microfono_on.png").resize((24, 24), Image.LANCZOS),
                    dark_image=Image.open("recursos/microfono_on.png").resize((24, 24), Image.LANCZOS),
                    size=(24, 24)
                )
                
            if os.path.exists("recursos/microfono_off.png"):
                self.img_microfono_off = ctk.CTkImage(
                    light_image=Image.open("recursos/microfono_off.png").resize((24, 24), Image.LANCZOS),
                    dark_image=Image.open("recursos/microfono_off.png").resize((24, 24), Image.LANCZOS),
                    size=(24, 24)
                )
                
        except Exception as e:
            print(f"Advertencia: No se pudieron cargar algunos recursos: {e}")
        
        # Si algún recurso no se cargó, crear uno por defecto
        if self.icono is None:
            self.icono = ctk.CTkImage(
                light_image=self._crear_imagen_predeterminada((32, 32), "AGP"),
                dark_image=self._crear_imagen_predeterminada((32, 32), "AGP"),
                size=(32, 32)
            )
            
        if self.logo is None:
            self.logo = ctk.CTkImage(
                light_image=self._crear_imagen_predeterminada((200, 200), "AGP\nAsistente"),
                dark_image=self._crear_imagen_predeterminada((200, 200), "AGP\nAsistente"),
                size=(200, 200)
            )
            
        if self.img_microfono_on is None:
            self.img_microfono_on = ctk.CTkImage(
                light_image=self._crear_imagen_predeterminada((24, 24), "🎤"),
                dark_image=self._crear_imagen_predeterminada((24, 24), "🎤"),
                size=(24, 24)
            )
            
        if self.img_microfono_off is None:
            self.img_microfono_off = ctk.CTkImage(
                light_image=self._crear_imagen_predeterminada((24, 24), "🔇"),
                dark_image=self._crear_imagen_predeterminada((24, 24), "🔇"),
                size=(24, 24)
            )
    
    def _crear_imagen_predeterminada(self, size, texto):
        """Crea una imagen predeterminada con texto centrado."""
        from PIL import Image, ImageDraw, ImageFont
        
        # Crear una imagen con fondo transparente
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        
        # Obtener el tema actual
        tema = ctk.get_appearance_mode().lower()
        color_fondo = (240, 240, 240) if tema == "light" else (50, 50, 50)
        color_texto = (30, 30, 30) if tema == "light" else (220, 220, 220)
        
        # Dibujar fondo redondeado
        d.rounded_rectangle([(0, 0), size], 15, fill=color_fondo)
        
        # Configurar fuente
        try:
            font_size = min(size) // 2
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Dibujar texto centrado
        text_bbox = d.textbbox((0, 0), texto, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
        
        d.text(position, texto, font=font, fill=color_texto, align="center")
        
        return img
    
    def _actualizar_transcripcion(self, texto):
        """Actualiza el texto de la transcripción en la interfaz."""
        if hasattr(self, 'label_transcripcion'):
            self.label_transcripcion.configure(text=texto)
            self.root.update_idletasks()
    
    def _guardar_mensaje_historial(self, remitente: str, mensaje: str):
        """Guarda un mensaje en el historial de la sesión actual."""
        self.historial_mensajes.append({
            'fecha_hora': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'remitente': remitente,
            'mensaje': mensaje
        })
        
        # Guardar en archivo diario
        self._guardar_historial_diario()
    
    def _cargar_historial_diario(self):
        """Carga el historial de mensajes del día actual."""
        try:
            fecha_actual = datetime.now().strftime('%Y-%m-%d')
            historial_dir = Path('historial')
            historial_dir.mkdir(exist_ok=True)
            
            self.historial_archivo = historial_dir / f'chat_{fecha_actual}.json'
            
            if self.historial_archivo.exists():
                with open(self.historial_archivo, 'r', encoding='utf-8') as f:
                    self.historial_mensajes = json.load(f)
                    
                # Mostrar mensajes en el chat
                for msg in self.historial_mensajes[-50:]:  # Mostrar solo los últimos 50 mensajes
                    self.agregar_mensaje(msg['remitente'], msg['mensaje'], guardar=False)
        except Exception as e:
            print(f"Error al cargar el historial: {e}")
    
    def _guardar_historial_diario(self):
        """Guarda el historial de mensajes en un archivo JSON."""
        try:
            if self.historial_archivo:
                with open(self.historial_archivo, 'w', encoding='utf-8') as f:
                    json.dump(self.historial_mensajes, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error al guardar el historial: {e}")
    
    def exportar_conversacion(self, formato: str = 'txt'):
        """Exporta la conversación actual al formato especificado."""
        try:
            fecha_actual = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if formato == 'json':
                nombre_archivo = f'conversacion_{fecha_actual}.json'
                with open(nombre_archivo, 'w', encoding='utf-8') as f:
                    json.dump(self.historial_mensajes, f, ensure_ascii=False, indent=2)
            else:  # txt por defecto
                nombre_archivo = f'conversacion_{fecha_actual}.txt'
                with open(nombre_archivo, 'w', encoding='utf-8') as f:
                    for msg in self.historial_mensajes:
                        f.write(f"[{msg['fecha_hora']}] {msg['remitente']}: {msg['mensaje']}\n")
            
            return nombre_archivo
        except Exception as e:
            print(f"Error al exportar la conversación: {e}")
            return None
    
    def _buscar_en_conversacion(self, termino: str):
        """Busca un término en la conversación actual."""
        if not termino:
            return []
        
        termino = termino.lower()
        coincidencias = []
        
        for i, msg in enumerate(self.historial_mensajes):
            if termino in msg['mensaje'].lower() or termino in msg['remitente'].lower():
                coincidencias.append((i, msg))
        
        return coincidencias
    
    def _configurar_interfaz(self):
        """Configura los elementos de la interfaz de usuario."""
        # Configuración de la ventana principal
        self.root.configure(fg_color=self.tema_actual['bg'])
        
        # Configurar grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Aplicar estilo a los widgets
        estilo = {
            'corner_radius': 8,
            'border_width': 0,
            'fg_color': self.tema_actual['bg'],
            'text_color': self.tema_actual['fg'],
            'font': self.fuente_normal
        }
        
        # Aplicar estilo a los frames
        ctk.CTkFrame.configure(
            self.root,
            corner_radius=estilo['corner_radius'],
            fg_color=self.tema_actual['secondary'],
            border_color=self.tema_actual['border'] if 'border' in self.tema_actual else None
        )
        
        # Configurar estilo de botones
        ctk.CTkButton.configure(
            self.root,
            corner_radius=estilo['corner_radius'],
            fg_color=self.tema_actual['button'],
            hover_color=self.tema_actual['hover'],
            text_color=self.tema_actual['text'],
            font=self.fuente_normal
        )
        
        # Barra superior
        self._crear_barra_superior()
        
        # Panel principal
        self._crear_panel_principal()
        
        # Barra lateral
        self._crear_barra_lateral()
        
        # Barra de estado
        self._crear_barra_estado()
        
        # Aplicar tema
        self._cambiar_tema('Midnight Blue')
    
    def _crear_barra_superior(self):
        """Crea la barra superior con título y controles."""
        frame_superior = ctk.CTkFrame(
            self.root, 
            corner_radius=0,
            fg_color=self.tema_actual['secondary'],
            height=60
        )
        frame_superior.grid(row=0, column=0, columnspan=2, sticky="nsew")
        frame_superior.grid_propagate(False)
        
        # Configurar grid para la barra superior
        frame_superior.grid_columnconfigure(1, weight=1)
        
        # Logo y título
        if self.logo:
            logo_frame = ctk.CTkFrame(frame_superior, fg_color="transparent")
            logo_frame.grid(row=0, column=0, rowspan=2, padx=10, pady=5, sticky="w")
            
            label_logo = ctk.CTkLabel(
                logo_frame,
                image=self.logo,
                text=""
            )
            label_logo.pack(side="left", padx=(5, 10))
            
            label_titulo = ctk.CTkLabel(
                logo_frame,
                text="AGP",
                font=("Roboto", 20, "bold"),
                text_color=self.tema_actual['accent']
            )
            label_titulo.pack(side="left")
            
            label_subtitulo = ctk.CTkLabel(
                logo_frame,
                text="Asistente de Voz",
                font=("Roboto", 12),
                text_color=self.tema_actual['fg']
            )
            label_subtitulo.pack(side="left", padx=(5, 0))
        
        # Barra de búsqueda
        self.barra_busqueda = ctk.CTkEntry(
            frame_superior,
            placeholder_text="Buscar en la conversación...",
            width=300,
            corner_radius=20,
            border_width=1,
            fg_color=self.tema_actual['bg'],
            text_color=self.tema_actual['fg'],
            placeholder_text_color=self.tema_actual['text']
        )
        self.barra_busqueda.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        self.barra_busqueda.bind("<Return>", lambda e: self._buscar_mensajes())
        
        # Botón de búsqueda
        btn_buscar = ctk.CTkButton(
            frame_superior,
            text="",
            width=40,
            height=40,
            corner_radius=20,
            fg_color=self.tema_actual['button'],
            hover_color=self.tema_actual['hover'],
            command=self._buscar_mensajes
        )
        btn_buscar.grid(row=0, column=2, padx=(0, 10), pady=10, sticky="e")
        
        # Botón de tema
        btn_tema = ctk.CTkButton(
            frame_superior,
            text="☀️" if self.tema_oscuro else "🌙",
            width=40,
            height=40,
            corner_radius=20,
            fg_color=self.tema_actual['button'],
            hover_color=self.tema_actual['hover'],
            command=self._alternar_tema
        )
        btn_tema.grid(row=0, column=3, padx=5, pady=10, sticky="e")
        
        # Etiqueta para mostrar el texto del micrófono en tiempo real
        self.label_transcripcion = ctk.CTkLabel(
            frame_superior,
            text="",
            font=self.fuente_pequena,
            text_color=("gray50", "gray70"),
            height=16,
            anchor="w"
        )
        self.label_transcripcion.pack(fill="x", pady=(0, 5))
        
        # Botones de control
        frame_controles = ctk.CTkFrame(frame_superior, fg_color="transparent")
        frame_controles.pack(side="right", padx=10)
        
        # Botón de alternar tema
        self.btn_tema = ctk.CTkButton(
            frame_controles,
            text=f"Tema: {self.tema_actual}",
            command=self._alternar_tema,
            width=180,
            fg_color=("gray70", "gray30"),
            hover_color=("gray60", "gray40")
        )
        self.btn_tema.pack(side="left", padx=5)
        
        # Botón de micrófono
        self.btn_microfono = ctk.CTkButton(
            frame_controles,
            text="Encender Micrófono",
            image=self.img_microfono_off,
            compound="left",
            command=self._alternar_microfono
        )
        self.btn_microfono.pack(side="left", padx=5)
    
    def _crear_panel_principal(self):
        """Crea el panel principal con pestañas."""
        # Crear pestañas
        self.tabview = ctk.CTkTabview(self.root)
        self.tabview.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        # Pestaña de chat
        self.tab_chat = self.tabview.add("Chat")
        self._configurar_pestana_chat()
        
        # Pestaña de comandos
        self.tab_comandos = self.tabview.add("Comandos")
        self._configurar_pestana_comandos()
        
        # Pestaña de configuración
        self.tab_config = self.tabview.add("Configuración")
        self._configurar_pestana_configuracion()
    
    def _configurar_pestana_chat(self):
        """Configura la pestaña de chat con búsqueda y exportación."""
        # Configurar grid
        self.tab_chat.grid_columnconfigure(0, weight=1)
        self.tab_chat.grid_rowconfigure(1, weight=1)
        
        # Frame de búsqueda
        frame_busqueda = ctk.CTkFrame(self.tab_chat, height=40)
        frame_busqueda.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")
        frame_busqueda.grid_columnconfigure(1, weight=1)
        
        # Campo de búsqueda
        self.entrada_busqueda = ctk.CTkEntry(
            frame_busqueda,
            placeholder_text="Buscar en la conversación...",
            font=self.fuente_normal
        )
        self.entrada_busqueda.grid(row=0, column=0, padx=(5, 2), pady=5, sticky="ew")
        
        # Botón de búsqueda
        btn_buscar = ctk.CTkButton(
            frame_busqueda,
            text="Buscar",
            width=80,
            command=self._buscar_mensajes
        )
        btn_buscar.grid(row=0, column=1, padx=2, pady=5)
        
        # Botón de exportar
        btn_exportar = ctk.CTkButton(
            frame_busqueda,
            text="Exportar Chat",
            width=100,
            command=self._mostrar_menu_exportar
        )
        btn_exportar.grid(row=0, column=2, padx=(2, 5), pady=5)
        
        # Área de mensajes
        frame_mensajes = ctk.CTkScrollableFrame(self.tab_chat)
        frame_mensajes.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        frame_mensajes.grid_columnconfigure(0, weight=1)
        
        self.contenedor_mensajes = ctk.CTkFrame(frame_mensajes, fg_color="transparent")
        self.contenedor_mensajes.grid(row=0, column=0, sticky="nsew")
        self.contenedor_mensajes.grid_columnconfigure(0, weight=1)
        
        # Área de entrada
        frame_entrada = ctk.CTkFrame(self.tab_chat, height=100)
        frame_entrada.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="sew")
        frame_entrada.grid_columnconfigure(0, weight=1)
        
        self.entrada_mensaje = ctk.CTkTextbox(
            frame_entrada,
            height=80,
            wrap="word",
            font=self.fuente_normal
        )
        self.entrada_mensaje.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        frame_botones = ctk.CTkFrame(frame_entrada, fg_color="transparent")
        frame_botones.grid(row=1, column=0, sticky="e", pady=(0, 5))
        
        self.btn_enviar = ctk.CTkButton(
            frame_botones,
            text="Enviar",
            command=self._enviar_mensaje
        )
        self.btn_enviar.pack(side="right", padx=5)
        
        self.btn_voz = ctk.CTkButton(
            frame_botones,
            text="Dictar",
            command=self._iniciar_dictado
        )
        self.btn_voz.pack(side="right", padx=5)
    
    def _configurar_pestana_comandos(self):
        """Configura la pestaña de comandos."""
        # Configurar grid
        self.tab_comandos.grid_columnconfigure(0, weight=1)
        self.tab_comandos.grid_rowconfigure(1, weight=1)
        
        # Título
        label_titulo = ctk.CTkLabel(
            self.tab_comandos,
            text="Comandos Disponibles",
            font=self.fuente_subtitulo
        )
        label_titulo.pack(pady=(10, 5), padx=10, anchor="w")
        
        # Frame para los comandos
        frame_comandos = ctk.CTkScrollableFrame(self.tab_comandos)
        frame_comandos.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Lista de comandos
        comandos = [
            ("Hora actual", "Muestra la hora actual", self._comando_hora),
            ("Fecha actual", "Muestra la fecha actual", self._comando_fecha),
            ("Abrir navegador", "Abre el navegador web predeterminado", self._comando_abrir_navegador),
            ("Tomar nota", "Abre una ventana para tomar notas", self._comando_tomar_nota),
            ("Silenciar", "Silencia el micrófono", self._alternar_microfono)
        ]
        
        # Agregar botones para cada comando
        for texto, descripcion, comando in comandos:
            frame = ctk.CTkFrame(frame_comandos, corner_radius=5)
            frame.pack(fill="x", pady=2, padx=5)
            
            btn = ctk.CTkButton(
                frame,
                text=texto,
                command=comando,
                width=150,
                anchor="w"
            )
            btn.pack(side="left", padx=5, pady=5)
            
            label = ctk.CTkLabel(
                frame,
                text=descripcion,
                font=self.fuente_pequena,
                anchor="w"
            )
            label.pack(side="left", fill="x", expand=True, padx=5)
    
    def _configurar_pestana_configuracion(self):
        """Configura la pestaña de configuración."""
        # Configurar grid
        self.tab_config.grid_columnconfigure(0, weight=1)
        self.tab_config.grid_rowconfigure(1, weight=1)
        
        # Frame para las opciones
        frame_opciones = ctk.CTkScrollableFrame(self.tab_config)
        frame_opciones.pack(fill="both", expand=True, padx=10, pady=5)
        
        # ===== Sección de Apariencia =====
        frame_apariencia = ctk.CTkFrame(frame_opciones, fg_color="transparent")
        frame_apariencia.pack(fill="x", pady=(0, 10))
        
        label_apariencia = ctk.CTkLabel(
            frame_apariencia,
            text="Apariencia",
            font=self.fuente_subtitulo
        )
        label_apariencia.pack(anchor="w", pady=(0, 5))
        
        # Tema
        frame_tema = ctk.CTkFrame(frame_apariencia, fg_color="transparent")
        frame_tema.pack(fill="x", pady=2)
        
        label_tema = ctk.CTkLabel(
            frame_tema,
            text="Tema:",
            width=120,
            anchor="w"
        )
        label_tema.pack(side="left")
        
        self.combo_tema = ctk.CTkComboBox(
            frame_tema,
            values=self.temas_disponibles,
            command=self._cambiar_tema,
            width=150
        )
        self.combo_tema.set(self.tema_actual)
        self.combo_tema.pack(side="left", padx=5)
        
        # ===== Sección de Audio =====
        frame_audio = ctk.CTkFrame(frame_opciones, fg_color="transparent")
        frame_audio.pack(fill="x", pady=(10, 10))
        
        label_audio = ctk.CTkLabel(
            frame_audio,
            text="Configuración de Audio",
            font=self.fuente_subtitulo
        )
        label_audio.pack(anchor="w", pady=(0, 5))
        
        # Control de volumen
        frame_volumen = ctk.CTkFrame(frame_audio, fg_color="transparent")
        frame_volumen.pack(fill="x", pady=2)
        
        label_vol = ctk.CTkLabel(
            frame_volumen,
            text="Volumen:",
            width=120,
            anchor="w"
        )
        label_vol.pack(side="left")
        
        self.slider_volumen = ctk.CTkSlider(
            frame_volumen,
            from_=0,
            to=100,
            number_of_steps=100,
            command=self._actualizar_volumen
        )
        self.slider_volumen.set(self.volumen * 100)
        self.slider_volumen.pack(side="left", fill="x", expand=True, padx=5)
        
        self.label_vol_valor = ctk.CTkLabel(
            frame_volumen,
            text=f"{int(self.volumen * 100)}%",
            width=40
        )
        self.label_vol_valor.pack(side="left")
        
        # Control de velocidad
        frame_velocidad = ctk.CTkFrame(frame_audio, fg_color="transparent")
        frame_velocidad.pack(fill="x", pady=2)
        
        label_vel = ctk.CTkLabel(
            frame_velocidad,
            text="Velocidad:",
            width=120,
            anchor="w"
        )
        label_vel.pack(side="left")
        
        self.slider_velocidad = ctk.CTkSlider(
            frame_velocidad,
            from_=0.5,
            to=2.0,
            number_of_steps=15,
            command=self._actualizar_velocidad
        )
        self.slider_velocidad.set(self.velocidad)
        self.slider_velocidad.pack(side="left", fill="x", expand=True, padx=5)
        
        self.label_vel_valor = ctk.CTkLabel(
            frame_velocidad,
            text=f"{self.velocidad:.1f}x",
            width=40
        )
        self.label_vel_valor.pack(side="left")
        
        # ===== Sección de Notificaciones =====
        frame_notif = ctk.CTkFrame(frame_opciones, fg_color="transparent")
        frame_notif.pack(fill="x", pady=(10, 10))
        
        label_notif = ctk.CTkLabel(
            frame_notif,
            text="Notificaciones",
            font=self.fuente_subtitulo
        )
        label_notif.pack(anchor="w", pady=(0, 5))
        
        self.var_notif_sonido = ctk.BooleanVar(value=True)
        self.check_sonido = ctk.CTkCheckBox(
            frame_notif,
            text="Sonido de notificaciones",
            variable=self.var_notif_sonido,
            command=self._actualizar_notificaciones
        )
        self.check_sonido.pack(anchor="w", pady=2)
        
        self.var_notif_ventana = ctk.BooleanVar(value=True)
        self.check_ventana = ctk.CTkCheckBox(
            frame_notif,
            text="Mostrar notificaciones en ventana",
            variable=self.var_notif_ventana,
            command=self._actualizar_notificaciones
        )
        self.check_ventana.pack(anchor="w", pady=2)
        
        # ===== Botones de Acción =====
        frame_botones = ctk.CTkFrame(frame_opciones, fg_color="transparent")
        frame_botones.pack(fill="x", pady=(20, 10))
        
        btn_guardar = ctk.CTkButton(
            frame_botones,
            text="Guardar Configuración",
            command=self._guardar_configuracion,
            width=150
        )
        btn_guardar.pack(side="left", padx=5)
        
        btn_restaurar = ctk.CTkButton(
            frame_botones,
            text="Restaurar Valores por Defecto",
            command=self._restaurar_configuracion,
            fg_color="gray30",
            hover_color="gray40",
            width=200
        )
        btn_restaurar.pack(side="left", padx=5)
    
    # ===== MÉTODOS DE CONFIGURACIÓN =====
    
    def _cargar_preferencias(self):
        """Carga las preferencias guardadas del usuario."""
        try:
            if os.path.exists('preferencias.json'):
                with open('preferencias.json', 'r') as f:
                    preferencias = json.load(f)
                    
                    # Cargar tema
                    if 'tema' in preferencias and preferencias['tema'] in self.temas_disponibles:
                        self.tema_actual = preferencias['tema']
                        self.btn_tema.configure(text=f"Tema: {self.tema_actual}")
                        
                    # Cargar volumen
                    if 'volumen' in preferencias:
                        self.volumen = float(preferencias['volumen'])
                        if hasattr(self, 'slider_volumen'):
                            self.slider_volumen.set(self.volumen * 100)
                    
                    # Cargar velocidad
                    if 'velocidad' in preferencias:
                        self.velocidad = float(preferencias['velocidad'])
                        if hasattr(self, 'slider_velocidad'):
                            self.slider_velocidad.set(self.velocidad)
                    
                    # Aplicar tema guardado
                    if hasattr(self, '_aplicar_tema'):
                        self._aplicar_tema(TEMAS[self.tema_actual])
                        
        except Exception as e:
            print(f"Error al cargar preferencias: {e}")
    
    def _guardar_preferencias(self):
        """Guarda las preferencias del usuario."""
        try:
            preferencias = {
                'tema': self.tema_actual,
                'volumen': self.volumen,
                'velocidad': self.velocidad
            }
            with open('preferencias.json', 'w') as f:
                json.dump(preferencias, f, indent=4)
        except Exception as e:
            print(f"Error al guardar preferencias: {e}")
    
    def _cambiar_tema(self, tema=None):
        """Cambia el tema de la aplicación."""
        if tema is None:
            # Si no se especifica tema, pasar al siguiente en la lista
            current_idx = self.temas_disponibles.index(self.tema_actual)
            next_idx = (current_idx + 1) % len(self.temas_disponibles)
            self.tema_actual = self.temas_disponibles[next_idx]
        else:
            self.tema_actual = tema
            
        tema_actual = TEMAS[self.tema_actual]
        self.tema_oscuro = tema_actual['bg'] in ['#1a1a2e', '#1b4332', '#2b2d42', '#231942', '#121212', '#1a1a1a']
        
        # Actualizar interfaz
        ctk.set_appearance_mode("Dark" if self.tema_oscuro else "Light")
        if hasattr(self, '_aplicar_tema'):
            self._aplicar_tema(tema_actual)
        
        # Actualizar botón de tema
        if hasattr(self, 'btn_tema'):
            self.btn_tema.configure(text=f"Tema: {self.tema_actual}")
        
        # Guardar preferencias
        self._guardar_preferencias()
    
    def _actualizar_volumen(self, valor):
        """Actualiza el volumen y la etiqueta correspondiente."""
        self.volumen = valor / 100
        self.label_vol_valor.configure(text=f"{int(valor)}%")
        # Aquí iría la lógica para actualizar el volumen del reproductor de audio
    
    def _actualizar_velocidad(self, valor):
        """Actualiza la velocidad y la etiqueta correspondiente."""
        self.velocidad = round(valor, 1)
        self.label_vel_valor.configure(text=f"{self.velocidad:.1f}x")
        # Aquí iría la lógica para actualizar la velocidad de habla
    
    def _actualizar_notificaciones(self):
        """Actualiza la configuración de notificaciones."""
        # Aquí iría la lógica para actualizar las preferencias de notificaciones
        pass
    
    def _guardar_configuracion(self):
        """Guarda la configuración actual."""
        config = {
            'tema': self.tema_actual,
            'volumen': self.volumen,
            'velocidad': self.velocidad,
            'notif_sonido': self.var_notif_sonido.get(),
            'notif_ventana': self.var_notif_ventana.get()
        }
        try:
            import json
            with open('config.json', 'w') as f:
                json.dump(config, f)
            self.agregar_mensaje("Sistema", "Configuración guardada correctamente.")
        except Exception as e:
            self.agregar_mensaje("Error", f"No se pudo guardar la configuración: {e}")
    
    def _restaurar_configuracion(self):
        """Restaura la configuración predeterminada."""
        self.combo_tema.set("Dark Mode")
        self.slider_volumen.set(80)
        self._actualizar_volumen(80)
        self.slider_velocidad.set(1.0)
        self._actualizar_velocidad(1.0)
        self.var_notif_sonido.set(True)
        self.var_notif_ventana.set(True)
        self._cambiar_tema("Dark Mode")
        self.agregar_mensaje("Sistema", "Configuración restaurada a los valores predeterminados.")
    
    def _crear_barra_lateral(self):
        """Crea la barra lateral con información del sistema."""
        frame_lateral = ctk.CTkFrame(self.root, width=280, corner_radius=0)
        frame_lateral.grid(row=1, column=1, padx=(0, 10), pady=(0, 10), sticky="nsew")
        frame_lateral.grid_propagate(False)
        frame_lateral.grid_rowconfigure(2, weight=1)  # Hace que el frame de estadísticas ocupe el espacio restante
        
        # Título
        label_titulo = ctk.CTkLabel(
            frame_lateral,
            text="Estado del Sistema",
            font=self.fuente_subtitulo
        )
        label_titulo.pack(pady=(10, 5), padx=10, anchor="w")
        
        # Información del sistema
        self.label_cpu = ctk.CTkLabel(
            frame_lateral,
            text="CPU: 0%",
            font=self.fuente_pequena,
            anchor="w"
        )
        self.label_cpu.pack(fill="x", padx=10, pady=2)
        
        self.label_memoria = ctk.CTkLabel(
            frame_lateral,
            text="Memoria: 0% (0 MB)",
            font=self.fuente_pequena,
            anchor="w"
        )
        self.label_memoria.pack(fill="x", padx=10, pady=2)
        
        self.label_disco = ctk.CTkLabel(
            frame_lateral,
            text="Disco: 0%",
            font=self.fuente_pequena,
            anchor="w"
        )
        self.label_disco.pack(fill="x", padx=10, pady=2)
        
        self.label_red = ctk.CTkLabel(
            frame_lateral,
            text="Red: Inactiva",
            font=self.fuente_pequena,
            anchor="w"
        )
        self.label_red.pack(fill="x", padx=10, pady=2)
        
        # Separador
        ctk.CTkFrame(frame_lateral, height=1, fg_color="gray30").pack(fill="x", pady=10)
        
        # Título de comandos rápidos
        label_comandos = ctk.CTkLabel(
            frame_lateral,
            text="Comandos Rápidos",
            font=self.fuente_subtitulo
        )
        label_comandos.pack(pady=(5, 5), padx=10, anchor="w")
        
        # Botones de comandos rápidos
        comandos = [
            ("Hora actual", self._comando_hora),
            ("Fecha actual", self._comando_fecha),
            ("Abrir navegador", self._comando_abrir_navegador),
            ("Tomar nota", self._comando_tomar_nota)
        ]
        
        for texto, comando in comandos:
            btn = ctk.CTkButton(
                frame_lateral,
                text=texto,
                command=comando,
                anchor="w",
                fg_color="transparent",
                hover_color=("gray70", "gray30"),
                text_color=("gray10", "gray90")
            )
            btn.pack(fill="x", padx=10, pady=2)
    
    def _crear_barra_estado(self):
        """Crea la barra de estado inferior."""
        frame_estado = ctk.CTkFrame(self.root, height=25, corner_radius=0)
        frame_estado.grid(row=2, column=0, columnspan=2, sticky="sew")
        frame_estado.grid_columnconfigure(0, weight=1)
        
        self.label_estado = ctk.CTkLabel(
            frame_estado,
            text="Listo",
            font=self.fuente_pequena,
            anchor="w"
        )
        self.label_estado.pack(side="left", padx=10)
        
        self.label_hora = ctk.CTkLabel(
            frame_estado,
            text=time.strftime("%H:%M:%S"),
            font=self.fuente_pequena,
            anchor="e"
        )
        self.label_hora.pack(side="right", padx=10)
    
    def _comando_hora(self):
        """Muestra la hora actual."""
        from datetime import datetime
        hora_actual = datetime.now().strftime("%H:%M:%S")
        self.agregar_mensaje("Sistema", f"La hora actual es: {hora_actual}")
    
    def _comando_fecha(self):
        """Muestra la fecha actual."""
        from datetime import datetime
        from locale import setlocale, LC_TIME
        
        try:
            setlocale(LC_TIME, 'es_ES.UTF-8')  # Configurar el idioma a español
        except:
            setlocale(LC_TIME, 'spanish')  # Alternativa en algunos sistemas
            
        fecha_actual = datetime.now().strftime("%A, %d de %B de %Y")
        self.agregar_mensaje("Sistema", f"Hoy es {fecha_actual}")
    
    def _comando_abrir_navegador(self):
        """Abre el navegador web predeterminado."""
        import webbrowser
        try:
            webbrowser.open("https://www.google.com")
            self.agregar_mensaje("Sistema", "Abriendo el navegador...")
        except Exception as e:
            self.agregar_mensaje("Error", f"No se pudo abrir el navegador: {e}")
    
    def _comando_tomar_nota(self):
        """Abre un diálogo para tomar una nota."""
        # Crear un diálogo para tomar notas
        dialog = tk.Toplevel(self.root)
        dialog.title("Tomar Nota")
        dialog.geometry("500x300")
        
        # Centrar la ventana
        window_width = 500
        window_height = 300
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Hacer que la ventana sea modal
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Área de texto para la nota
        texto_nota = ctk.CTkTextbox(dialog, font=self.fuente_normal)
        texto_nota.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame para los botones
        frame_botones = ctk.CTkFrame(dialog)
        frame_botones.pack(fill="x", padx=10, pady=5)
        
        # Función para guardar la nota
        def guardar_nota():
            nota = texto_nota.get("1.0", "end-1c").strip()
            if nota:
                # Aquí podrías guardar la nota en un archivo o base de datos
                self.agregar_mensaje("Nota", f"Nota guardada: {nota[:50]}...")
                dialog.destroy()
        
        # Botones
        btn_guardar = ctk.CTkButton(
            frame_botones,
            text="Guardar",
            command=guardar_nota
        )
        btn_guardar.pack(side="right", padx=5)
        
        btn_cancelar = ctk.CTkButton(
            frame_botones,
            text="Cancelar",
            command=dialog.destroy,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30")
        )
        btn_cancelar.pack(side="right", padx=5)
    
    def _iniciar_dictado(self):
        """Abre un diálogo para iniciar el dictado por voz."""
        # Mostrar un diálogo de entrada para simular el dictado
        # En una implementación real, aquí se usaría un reconocedor de voz
        from tkinter import simpledialog
        
        # Crear un diálogo personalizado
        dialog = tk.Toplevel(self.root)
        dialog.title("Dictado por voz")
        dialog.geometry("400x150")
        dialog.resizable(False, False)
        
        # Centrar la ventana
        window_width = 400
        window_height = 150
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Hacer que la ventana sea modal
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Etiqueta de instrucción
        label = ctk.CTkLabel(
            dialog, 
            text="Hable ahora...",
            font=self.fuente_subtitulo
        )
        label.pack(pady=20)
        
        # Botón para simular el final del dictado
        def finalizar_dictado():
            # En una implementación real, aquí se procesaría el audio
            # Por ahora, simulamos un mensaje de prueba
            mensaje = "Este es un mensaje de prueba del dictado por voz"
            self.agregar_mensaje("Tú", mensaje)
            dialog.destroy()
        
        btn_finalizar = ctk.CTkButton(
            dialog,
            text="Finalizar dictado",
            command=finalizar_dictado
        )
        btn_finalizar.pack(pady=10)
        
        # Botón para cancelar
        btn_cancelar = ctk.CTkButton(
            dialog,
            text="Cancelar",
            command=dialog.destroy,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30")
        )
        btn_cancelar.pack()
    
    def _enviar_mensaje(self):
        """Envía el mensaje escrito en el campo de entrada."""
        mensaje = self.entrada_mensaje.get("1.0", "end-1c").strip()
        if not mensaje:
            return
            
        # Agregar el mensaje a la conversación
        self.agregar_mensaje("Tú", mensaje)
        
        # Limpiar el campo de entrada
        self.entrada_mensaje.delete("1.0", "end")
        
        # Aquí podrías agregar la lógica para procesar el mensaje
        # y obtener una respuesta del asistente
        # respuesta = self.procesar_mensaje(mensaje)
        # self.agregar_mensaje("Asistente", respuesta)
    
    def _buscar_mensajes(self):
        """Busca mensajes que coincidan con el término de búsqueda."""
        termino = self.entrada_busqueda.get().strip()
        if not termino:
            return
            
        # Buscar coincidencias
        coincidencias = self._buscar_en_conversacion(termino)
        
        # Resaltar coincidencias
        for widget in self.contenedor_mensajes.winfo_children():
            if hasattr(widget, 'cget') and hasattr(widget, 'configure'):
                # Restaurar colores originales
                if 'mensaje' in widget.winfo_name():
                    widget.configure(
                        fg_color=("#f0f0f0", "#2a2a2a") if 'Sistema' in widget.winfo_children()[0].cget('text') 
                        else ("#e6f3ff", "#1a3a5f")
                    )
        
        # Resaltar coincidencias
        for idx, _ in coincidencias:
            if idx < len(self.contenedor_mensajes.winfo_children()):
                widget = self.contenedor_mensajes.winfo_children()[idx]
                if hasattr(widget, 'configure'):
                    widget.configure(fg_color=("#fff3cd", "#856404"))  # Color de resaltado
        
        # Hacer scroll a la primera coincidencia
        if coincidencias:
            idx = coincidencias[0][0]
            if idx < len(self.contenedor_mensajes.winfo_children()):
                widget = self.contenedor_mensajes.winfo_children()[idx]
                widget.see()
    
    def _mostrar_menu_exportar(self):
        """Muestra el menú de opciones de exportación."""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Exportar a TXT", command=lambda: self._exportar_chat('txt'))
        menu.add_command(label="Exportar a JSON", command=lambda: self._exportar_chat('json'))
        
        # Mostrar el menú cerca del botón de exportar
        x = self.root.winfo_pointerx()
        y = self.root.winfo_pointery()
        menu.post(x, y)
    
    def _exportar_chat(self, formato: str):
        """Exporta el chat al formato especificado."""
        try:
            # Obtener la ruta de guardado
            fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"chat_exportado_{fecha}.{formato}"
            
            # Preguntar al usuario dónde guardar
            ruta_guardado = filedialog.asksaveasfilename(
                defaultextension=f".{formato}",
                filetypes=[(f"Archivo {formato.upper()}", f"*.{formato}")],
                initialfile=nombre_archivo
            )
            
            if not ruta_guardado:
                return  # Usuario canceló
                
            # Exportar según el formato
            if formato == 'json':
                with open(ruta_guardado, 'w', encoding='utf-8') as f:
                    json.dump(self.historial_mensajes, f, ensure_ascii=False, indent=2)
            else:  # txt
                with open(ruta_guardado, 'w', encoding='utf-8') as f:
                    for msg in self.historial_mensajes:
                        f.write(f"[{msg['fecha_hora']}] {msg['remitente']}: {msg['mensaje']}\n")
            
            messagebox.showinfo("Éxito", f"Chat exportado correctamente a:\n{ruta_guardado}")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el chat:\n{str(e)}")

    def _iniciar_actualizacion_estadisticas(self):
        """Inicia la actualización periódica de las estadísticas del sistema."""
        def actualizar():
            while True:
                try:
                    # Actualizar CPU
                    cpu_percent = psutil.cpu_percent()
                    self.label_cpu.configure(text=f"CPU: {cpu_percent}%")
                    
                    # Actualizar memoria
                    mem = psutil.virtual_memory()
                    mem_percent = mem.percent
                    mem_used = mem.used / (1024 * 1024)  # Convertir a MB
                    self.label_memoria.configure(
                        text=f"Memoria: {mem_percent}% ({mem_used:.0f} MB)"
                    )
                    
                    # Actualizar disco
                    disk = psutil.disk_usage('/' if os.name != 'nt' else 'C:')
                    self.label_disco.configure(text=f"Disco: {disk.percent}%")
                    
                    # Actualizar red
                    net_io = psutil.net_io_counters()
                    net_status = "Activa" if net_io.bytes_sent > 0 or net_io.bytes_recv > 0 else "Inactiva"
                    self.label_red.configure(text=f"Red: {net_status}")
                    
                    # Actualizar hora
                    self.label_hora.configure(text=time.strftime("%H:%M:%S"))
                    
                except Exception as e:
                    print(f"Error al actualizar estadísticas: {e}")
                
                # Esperar 1 segundo antes de la próxima actualización
                time.sleep(1)
        
        # Iniciar hilo para actualizaciones en segundo plano
        threading.Thread(target=actualizar, daemon=True).start()
    
    def _alternar_tema(self):
        """Alterna entre tema claro y oscuro."""
        self.tema_oscuro = not self.tema_oscuro
        ctk.set_appearance_mode("Dark" if self.tema_oscuro else "Light")
        self.btn_tema.configure(
            text="Tema Oscuro" if not self.tema_oscuro else "Tema Claro"
        )
    
    def _alternar_microfono(self):
        """Alterna el estado del micrófono."""
        self.escuchando = not self.escuchando
        
        if self.escuchando:
            self.btn_microfono.configure(
                text="Apagar Micrófono",
                image=self.img_microfono_on,
                fg_color=("#3a7ebf", "#1f538d"),
                hover_color=("#325882", "#14375e")
            )
            self.agregar_mensaje("Sistema", "Escuchando...")
        else:
            self.btn_microfono.configure(
                text="Encender Micrófono",
                image=self.img_microfono_off,
            anchor="w",
            fg_color="transparent",
            hover_color=("gray70", "gray30"),
            text_color=("gray10", "gray90")
        )
        btn.pack(fill="x", padx=10, pady=2)

def _crear_barra_estado(self):
    """Crea la barra de estado inferior."""
    frame_estado = ctk.CTkFrame(self.root, height=25, corner_radius=0)
    frame_estado.grid(row=2, column=0, columnspan=2, sticky="sew")
    frame_estado.grid_columnconfigure(0, weight=1)

    self.label_estado = ctk.CTkLabel(
        frame_estado,
        text="Listo",
        font=self.fuente_pequena,
        anchor="w"
    )
    self.label_estado.pack(side="left", padx=10)

    self.label_hora = ctk.CTkLabel(
        frame_estado,
        text=time.strftime("%H:%M:%S"),
        font=self.fuente_pequena,
        anchor="e"
    )
    self.label_hora.pack(side="right", padx=10)

def _iniciar_actualizacion_estadisticas(self):
    """Inicia la actualización periódica de las estadísticas del sistema."""
    def actualizar():
        while True:
            try:
                # Actualizar CPU
                cpu_percent = psutil.cpu_percent()
                self.label_cpu.configure(text=f"CPU: {cpu_percent}%")

                # Actualizar memoria
                mem = psutil.virtual_memory()
                mem_percent = mem.percent
                mem_used = mem.used / (1024 * 1024)  # Convertir a MB
                self.label_memoria.configure(
                    text=f"Memoria: {mem_percent}% ({mem_used:.0f} MB)"
                )

                # Actualizar disco
                disk = psutil.disk_usage('/')
                self.label_disco.configure(text=f"Disco: {disk.percent}%")

                # Actualizar red
                net_io = psutil.net_io_counters()
                net_status = "Activa" if net_io.bytes_sent > 0 or net_io.bytes_recv > 0 else "Inactiva"
                self.label_red.configure(text=f"Red: {net_status}")

                # Actualizar hora
                self.label_hora.configure(text=time.strftime("%H:%M:%S"))

            except Exception as e:
                print(f"Error al actualizar estadísticas: {e}")

            # Esperar 1 segundo antes de la próxima actualización
            time.sleep(1)

    # Iniciar hilo para actualizaciones en segundo plano
    threading.Thread(target=actualizar, daemon=True).start()

def _alternar_tema(self):
    """Alterna entre tema claro y oscuro."""
    self.tema_oscuro = not self.tema_oscuro
    ctk.set_appearance_mode("Dark" if self.tema_oscuro else "Light")
    self.btn_tema.configure(
        text="Tema Oscuro" if not self.tema_oscuro else "Tema Claro"
    )

def _alternar_microfono(self):
    """Alterna el estado del micrófono."""
    self.escuchando = not self.escuchando

    if self.escuchando:
        mensaje = self.entrada_mensaje.get("1.0", "end-1c").strip()
        if not mensaje:
            return
        
        # Agregar a la conversación
        self.agregar_mensaje("Tú", mensaje)
        
        # Limpiar campo de entrada
        self.entrada_mensaje.delete("1.0", "end")
        
        # Aquí iría la lógica para procesar el mensaje
        # self.procesar_mensaje(mensaje)
    
    def _iniciar_dictado(self):
        """Abre un cuadro de diálogo para ingresar texto."""
        from tkinter import simpledialog, Toplevel, ttk, StringVar
        
        # Crear una ventana personalizada
        dialog = Toplevel(self.root)
        dialog.title("Escribe tu mensaje")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        
        # Centrar la ventana
        window_width = 400
        window_height = 200
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Hacer que la ventana sea modal
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Estilo para los botones
        style = ttk.Style()
        style.configure('TButton', padding=5, font=('Segoe UI', 10))
        
        # Frame principal
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Etiqueta de instrucción
        ttk.Label(main_frame, text="Escribe tu mensaje:", font=('Segoe UI', 11)).pack(pady=(0, 10), anchor="w")
        
        # Cuadro de texto
        texto_var = StringVar()
        entry = ttk.Entry(main_frame, textvariable=texto_var, font=('Segoe UI', 11), width=40)
        entry.pack(pady=(0, 20), fill="x")
        entry.focus_set()
        
        # Frame para los botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        # Función para manejar el envío
        def enviar():
            texto = texto_var.get().strip()
            if texto:
                self.entrada_mensaje.delete("1.0", "end")
                self.entrada_mensaje.insert("1.0", texto)
                self.agregar_mensaje("Tú", texto)
                
                # Procesar comandos escritos
                texto_lower = texto.lower()
                if any(palabra in texto_lower for palabra in ['hora', 'qué hora es']):
                    self._comando_hora()
                elif any(palabra in texto_lower for palabra in ['fecha', 'qué día es hoy']):
                    self._comando_fecha()
                elif any(palabra in texto_lower for palabra in ['navegador', 'internet', 'abre el navegador']):
                    self._comando_abrir_navegador()
                elif any(palabra in texto_lower for palabra in ['nota', 'toma una nota']):
                    self._comando_tomar_nota()
                
            dialog.destroy()
            self._alternar_microfono()
        
        # Botón de enviar
        send_btn = ttk.Button(button_frame, text="Enviar", command=enviar)
        send_btn.pack(side="right", padx=5)
        
        # Botón de cancelar
        cancel_btn = ttk.Button(button_frame, text="Cancelar", command=lambda: [dialog.destroy(), self._alternar_microfono()])
        cancel_btn.pack(side="right")
        
        # Asignar la tecla Enter para enviar
        dialog.bind('<Return>', lambda e: enviar())
        dialog.bind('<Escape>', lambda e: [dialog.destroy(), self._alternar_microfono()])
        
        # Cambiar el ícono del botón del micrófono mientras el diálogo está abierto
        self.btn_microfono.configure(
            text="Cancelar entrada",
            fg_color=("#f44336", "#d32f2f"),
            hover_color=("#e53935", "#c62828")
        )
        
        # Restaurar el botón cuando se cierre el diálogo
        def on_closing():
            self._alternar_microfono()
            dialog.destroy()
            
        dialog.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Métodos de comandos rápidos
    def _comando_hora(self, event=None):
        """Muestra la hora actual."""
        try:
            hora_actual = time.strftime("%H:%M:%S")
            self.agregar_mensaje("Asistente", f"La hora actual es: {hora_actual}")
        except Exception as e:
            print(f"Error en comando hora: {e}")
    
    def _comando_fecha(self, event=None):
        """Muestra la fecha actual."""
        try:
            fecha_actual = time.strftime("%A, %d de %B de %Y")
            self.agregar_mensaje("Asistente", f"Hoy es {fecha_actual}")
        except Exception as e:
            print(f"Error en comando fecha: {e}")
    
    def _comando_abrir_navegador(self, event=None):
        """Abre el navegador web."""
        try:
            self.agregar_mensaje("Sistema", "Abriendo navegador...")
            import webbrowser
            webbrowser.open("https://www.google.com")
        except Exception as e:
            self.agregar_mensaje("Error", f"No se pudo abrir el navegador: {e}")
    
    def _comando_tomar_nota(self, event=None):
        """Abre una ventana para tomar notas."""
        try:
            self.agregar_mensaje("Sistema", "Abriendo editor de notas...")
            # Crear una nueva ventana para notas
            ventana_notas = ctk.CTkToplevel(self.root)
            ventana_notas.title("Tomar Nota")
            ventana_notas.geometry("500x400")
            
            # Área de texto para la nota
            area_texto = ctk.CTkTextbox(ventana_notas, wrap="word")
            area_texto.pack(expand=True, fill="both", padx=10, pady=10)
            
            # Botón para guardar
            def guardar_nota():
                nota = area_texto.get("1.0", "end-1c")
                if nota.strip():
                    self.agregar_mensaje("Nota", f"Nota guardada: {nota[:50]}...")
                ventana_notas.destroy()
            
            btn_guardar = ctk.CTkButton(
                ventana_notas,
                text="Guardar Nota",
                command=guardar_nota
            )
            btn_guardar.pack(pady=5)
            
        except Exception as e:
            self.agregar_mensaje("Error", f"No se pudo abrir el editor de notas: {e}")
    
    # Método iniciar eliminado, usamos mainloop() directamente


if __name__ == "__main__":
    # Ejemplo de uso
    app = InterfazAvanzada()
    app.root.mainloop()  # Llamamos a mainloop() directamente en la raíz
