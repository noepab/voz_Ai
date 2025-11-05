"""
Asistente de Voz Mejorado - Interfaz Unificada
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
import psutil
import platform
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Callable, Any, Union
from dataclasses import dataclass, asdict, field
from enum import Enum, auto
import customtkinter as ctk
from PIL import Image, ImageTk

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

# Variables globales
modo_dictado = False
estado_actual = "esperando"
buffer_texto = []
ultimo_tema = None

# Configuración de temas
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
        'error': '#ef4444',
        'panel': '#1e293b',
        'panel_hover': '#334155'
    },
    'Emerald Forest': {
        'bg': '#1b4332',
        'fg': '#d8f3dc',
        'accent': '#95d5b2',
        'secondary': '#2d6a4f',
        'button': '#40916c',
        'hover': '#52b788',
        'text': '#ffffff',
        'border': '#2d6a4f',
        'success': '#95d5b2',
        'warning': '#f59e0b',
        'error': '#e63946',
        'panel': '#2d6a4f',
        'panel_hover': '#40916c'
    },
    'Sunset Orange': {
        'bg': '#370617',
        'fg': '#f8f9fa',
        'accent': '#f48c06',
        'secondary': '#6a040f',
        'button': '#f48c06',
        'hover': '#faa307',
        'text': '#ffffff',
        'border': '#6a040f',
        'success': '#2b9348',
        'warning': '#f8961e',
        'error': '#d00000',
        'panel': '#6a040f',
        'panel_hover': '#9d0208'
    },
    'Dark Mode': {
        'bg': '#1a1a1a',
        'fg': '#e0e0e0',
        'accent': '#2b5bff',
        'secondary': '#2d2d2d',
        'button': '#2b5bff',
        'hover': '#1a42c4',
        'text': '#ffffff',
        'border': '#3d3d3d',
        'success': '#4caf50',
        'warning': '#ff9800',
        'error': '#f44336',
        'panel': '#2d2d2d',
        'panel_hover': '#3d3d3d'
    },
    'Light Mode': {
        'bg': '#f5f5f5',
        'fg': '#000000',
        'accent': '#2b5bff',
        'secondary': '#e0e0e0',
        'button': '#2b5bff',
        'hover': '#1a42c4',
        'text': '#000000',
        'border': '#bdbdbd',
        'success': '#388e3c',
        'warning': '#f57c00',
        'error': '#d32f2f',
        'panel': '#e0e0e0',
        'panel_hover': '#d0d0d0'
    }
}

class InterfazAsistente(ctk.CTk):
    """Interfaz avanzada para el asistente de voz."""
    
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana
        self.title("AGP Asistente de Voz")
        self.geometry("1000x700")
        self.minsize(900, 600)
        
        # Variables de estado
        self.escuchando = False
        self.hablando = False
        self.tema_actual = 'Dark Mode'
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
        
        # Inicializar historial de mensajes
        self.historial_mensajes = []
        self.historial_archivo = None
        
        # Cargar recursos
        self._cargar_recursos()
        
        # Configurar la interfaz
        self._configurar_interfaz()
        
        # Iniciar actualización de estadísticas
        self._iniciar_actualizacion_estadisticas()
        
        # Cargar historial de la sesión actual
        self._cargar_historial_diario()
    
    def _cargar_recursos(self):
        """Carga los recursos gráficos necesarios o crea unos por defecto."""
        try:
            # Cargar iconos
            self.icono_microfono = ctk.CTkImage(
                light_image=self._crear_imagen_predeterminada((24, 24), "🎤"),
                dark_image=self._crear_imagen_predeterminada((24, 24), "🎤")
            )
            
            self.icono_detener = ctk.CTkImage(
                light_image=self._crear_imagen_predeterminada((24, 24), "⏹️"),
                dark_image=self._crear_imagen_predeterminada((24, 24), "⏹️")
            )
            
            self.icono_config = ctk.CTkImage(
                light_image=self._crear_imagen_predeterminada((20, 20), "⚙️"),
                dark_image=self._crear_imagen_predeterminada((20, 20), "⚙️")
            )
            
            self.icono_ayuda = ctk.CTkImage(
                light_image=self._crear_imagen_predeterminada((20, 20), "❓"),
                dark_image=self._crear_imagen_predeterminada((20, 20), "❓")
            )
            
        except Exception as e:
            logging.error(f"Error cargando recursos: {e}")
    
    def _crear_imagen_predeterminada(self, size, texto):
        """Crea una imagen predeterminada con texto centrado."""
        from PIL import Image, ImageDraw, ImageFont
        
        # Crear una imagen en blanco
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        
        # Configurar la fuente
        try:
            font = ImageFont.truetype("arial.ttf", 14)
        except:
            font = ImageFont.load_default()
        
        # Dibujar el texto centrado
        text_bbox = d.textbbox((0, 0), texto, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (size[0] - text_width) / 2
        y = (size[1] - text_height) / 2
        
        d.text((x, y), texto, font=font, fill="white")
        return img
    
    def _configurar_interfaz(self):
        """Configura los elementos de la interfaz de usuario."""
        # Configurar el grid principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Crear la barra superior
        self._crear_barra_superior()
        
        # Crear el panel principal con pestañas
        self._crear_panel_principal()
        
        # Crear la barra lateral
        self._crear_barra_lateral()
        
        # Crear la barra de estado
        self._crear_barra_estado()
    
    def _crear_barra_superior(self):
        """Crea la barra superior con título y controles."""
        # Frame para la barra superior
        self.barra_superior = ctk.CTkFrame(self, height=60, corner_radius=0)
        self.barra_superior.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.barra_superior.grid_columnconfigure(1, weight=1)
        
        # Título de la aplicación
        self.titulo = ctk.CTkLabel(
            self.barra_superior,
            text="AGP Asistente de Voz",
            font=self.fuente_titulo
        )
        self.titulo.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        # Controles de la barra superior
        self.frame_controles = ctk.CTkFrame(self.barra_superior, fg_color="transparent")
        self.frame_controles.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        
        # Botón de alternar micrófono
        self.btn_microfono = ctk.CTkButton(
            self.frame_controles,
            text="Iniciar Escucha",
            image=self.icono_microfono,
            command=self._alternar_microfono,
            width=150,
            height=40,
            corner_radius=20,
            fg_color="#2b5bff",
            hover_color="#1a42c4",
            font=self.fuente_normal
        )
        self.btn_microfono.grid(row=0, column=0, padx=5)
        
        # Botón de configuración
        self.btn_config = ctk.CTkButton(
            self.frame_controles,
            text="",
            image=self.icono_config,
            command=self._mostrar_configuracion,
            width=40,
            height=40,
            corner_radius=20,
            fg_color="#2d2d2d",
            hover_color="#3d3d3d"
        )
        self.btn_config.grid(row=0, column=1, padx=5)
    
    def _crear_panel_principal(self):
        """Crea el panel principal con pestañas."""
        # Frame principal
        self.panel_principal = ctk.CTkFrame(self)
        self.panel_principal.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.panel_principal.grid_columnconfigure(0, weight=1)
        self.panel_principal.grid_rowconfigure(1, weight=1)
        
        # Pestañas
        self.tabs = ctk.CTkTabview(self.panel_principal)
        self.tabs.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Pestaña de chat
        self.tab_chat = self.tabs.add("Chat")
        self._configurar_pestana_chat()
        
        # Pestaña de comandos
        self.tab_comandos = self.tabs.add("Comandos")
        self._configurar_pestana_comandos()
        
        # Pestaña de configuración
        self.tab_config = self.tabs.add("Configuración")
        self._configurar_pestana_configuracion()
    
    def _configurar_pestana_chat(self):
        """Configura la pestaña de chat con búsqueda y exportación."""
        # Frame para la barra de búsqueda y exportación
        self.frame_busqueda = ctk.CTkFrame(self.tab_chat, fg_color="transparent")
        self.frame_busqueda.pack(fill="x", padx=5, pady=5)
        
        # Barra de búsqueda
        self.entry_buscar = ctk.CTkEntry(
            self.frame_busqueda,
            placeholder_text="Buscar en la conversación...",
            width=300
        )
        self.entry_buscar.pack(side="left", padx=5)
        
        self.btn_buscar = ctk.CTkButton(
            self.frame_busqueda,
            text="Buscar",
            width=80,
            command=self._buscar_mensajes
        )
        self.btn_buscar.pack(side="left", padx=5)
        
        # Botón de exportar
        self.btn_exportar = ctk.CTkButton(
            self.frame_busqueda,
            text="Exportar",
            width=100,
            command=self._mostrar_menu_exportar
        )
        self.btn_exportar.pack(side="right", padx=5)
        
        # Frame para el área de chat
        self.frame_chat = ctk.CTkFrame(self.tab_chat)
        self.frame_chat.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Área de mensajes
        self.texto_chat = ctk.CTkTextbox(
            self.frame_chat,
            wrap="word",
            font=self.fuente_normal,
            state="disabled"
        )
        self.texto_chat.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Frame para la entrada de texto
        self.frame_entrada = ctk.CTkFrame(self.tab_chat, fg_color="transparent")
        self.frame_entrada.pack(fill="x", padx=5, pady=5)
        
        # Entrada de texto
        self.entry_mensaje = ctk.CTkEntry(
            self.frame_entrada,
            placeholder_text="Escribe un mensaje...",
            font=self.fuente_normal
        )
        self.entry_mensaje.pack(side="left", fill="x", expand=True, padx=5)
        self.entry_mensaje.bind("<Return>", lambda e: self._enviar_mensaje())
        
        # Botón de enviar
        self.btn_enviar = ctk.CTkButton(
            self.frame_entrada,
            text="Enviar",
            command=self._enviar_mensaje,
            width=100
        )
        self.btn_enviar.pack(side="right", padx=5)
        
        # Botón de dictado
        self.btn_dictado = ctk.CTkButton(
            self.frame_entrada,
            text="🎤",
            command=self._iniciar_dictado,
            width=50,
            fg_color="#2d2d2d",
            hover_color="#3d3d3d"
        )
        self.btn_dictado.pack(side="right", padx=5)
    
    def _configurar_pestana_comandos(self):
        """Configura la pestaña de comandos."""
        # Frame para la lista de comandos
        self.frame_comandos = ctk.CTkFrame(self.tab_comandos)
        self.frame_comandos.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Título
        self.lbl_comandos = ctk.CTkLabel(
            self.frame_comandos,
            text="Comandos Disponibles",
            font=self.fuente_subtitulo
        )
        self.lbl_comandos.pack(pady=10)
        
        # Área de texto con los comandos
        self.texto_comandos = ctk.CTkTextbox(
            self.frame_comandos,
            wrap="word",
            font=self.fuente_normal,
            height=300
        )
        self.texto_comandos.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Agregar los comandos al área de texto
        comandos = """
        Comandos de voz disponibles:
        
        - "Hola" - Saluda al asistente
        - "¿Qué hora es?" - Muestra la hora actual
        - "¿Qué día es hoy?" - Muestra la fecha actual
        - "Abre [aplicación]" - Abre una aplicación
        - "Busca en internet [término]" - Realiza una búsqueda en internet
        - "Reproduce [canción/artista]" - Reproduce música
        - "Detener" - Detiene la reproducción actual
        - "Silencia" - Silencia el micrófono
        - "Activa el micrófono" - Reactiva el micrófono
        - "Salir" - Cierra la aplicación
        """
        
        self.texto_comandos.insert("1.0", comandos)
        self.texto_comandos.configure(state="disabled")
    
    def _configurar_pestana_configuracion(self):
        """Configura la pestaña de configuración."""
        # Frame para la configuración
        self.frame_config = ctk.CTkScrollableFrame(self.tab_config)
        self.frame_config.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Título
        self.lbl_config = ctk.CTkLabel(
            self.frame_config,
            text="Configuración",
            font=self.fuente_subtitulo
        )
        self.lbl_config.grid(row=0, column=0, columnspan=2, pady=10, sticky="w")
        
        # Tema
        self.lbl_tema = ctk.CTkLabel(
            self.frame_config,
            text="Tema:",
            font=self.fuente_normal
        )
        self.lbl_tema.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        self.var_tema = ctk.StringVar(value=self.tema_actual)
        self.menu_tema = ctk.CTkOptionMenu(
            self.frame_config,
            values=self.temas_disponibles,
            variable=self.var_tema,
            command=self._cambiar_tema,
            width=200
        )
        self.menu_tema.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Volumen
        self.lbl_volumen = ctk.CTkLabel(
            self.frame_config,
            text=f"Volumen: {int(self.volumen * 100)}%",
            font=self.fuente_normal
        )
        self.lbl_volumen.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        
        self.slider_volumen = ctk.CTkSlider(
            self.frame_config,
            from_=0,
            to=100,
            number_of_steps=100,
            command=lambda v: self._actualizar_volumen(v / 100)
        )
        self.slider_volumen.set(self.volumen * 100)
        self.slider_volumen.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        # Velocidad de habla
        self.lbl_velocidad = ctk.CTkLabel(
            self.frame_config,
            text=f"Velocidad de habla: {self.velocidad:.1f}x",
            font=self.fuente_normal
        )
        self.lbl_velocidad.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        
        self.slider_velocidad = ctk.CTkSlider(
            self.frame_config,
            from_=0.5,
            to=2.0,
            number_of_steps=15,
            command=lambda v: self._actualizar_velocidad(round(v, 1))
        )
        self.slider_velocidad.set(self.velocidad)
        self.slider_velocidad.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        
        # Notificaciones
        self.var_notificaciones = ctk.BooleanVar(value=True)
        self.chk_notificaciones = ctk.CTkCheckBox(
            self.frame_config,
            text="Activar notificaciones",
            variable=self.var_notificaciones,
            command=self._actualizar_notificaciones
        )
        self.chk_notificaciones.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        
        # Botones de acción
        self.frame_botones = ctk.CTkFrame(self.frame_config, fg_color="transparent")
        self.frame_botones.grid(row=5, column=0, columnspan=2, pady=20, sticky="ew")
        
        self.btn_guardar = ctk.CTkButton(
            self.frame_botones,
            text="Guardar Cambios",
            command=self._guardar_configuracion,
            fg_color="#2b5bff",
            hover_color="#1a42c4"
        )
        self.btn_guardar.pack(side="left", padx=5)
        
        self.btn_restaurar = ctk.CTkButton(
            self.frame_botones,
            text="Restaurar Valores por Defecto",
            command=self._restaurar_configuracion,
            fg_color="#6c757d",
            hover_color="#5a6268"
        )
        self.btn_restaurar.pack(side="left", padx=5)
    
    def _crear_barra_lateral(self):
        """Crea la barra lateral con información del sistema."""
        # Frame para la barra lateral
        self.barra_lateral = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.barra_lateral.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        self.barra_lateral.grid_propagate(False)
        
        # Título de la barra lateral
        self.lbl_estado = ctk.CTkLabel(
            self.barra_lateral,
            text="Estado del Sistema",
            font=self.fuente_subtitulo
        )
        self.lbl_estado.pack(pady=10)
        
        # Frame para la información del sistema
        self.frame_info = ctk.CTkFrame(self.barra_lateral, fg_color="transparent")
        self.frame_info.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Información del sistema
        self.lbl_cpu = ctk.CTkLabel(
            self.frame_info,
            text="CPU: Cargando...",
            font=self.fuente_pequena,
            anchor="w"
        )
        self.lbl_cpu.pack(fill="x", pady=2)
        
        self.lbl_memoria = ctk.CTkLabel(
            self.frame_info,
            text="Memoria: Cargando...",
            font=self.fuente_pequena,
            anchor="w"
        )
        self.lbl_memoria.pack(fill="x", pady=2)
        
        self.lbl_disco = ctk.CTkLabel(
            self.frame_info,
            text="Disco: Cargando...",
            font=self.fuente_pequena,
            anchor="w"
        )
        self.lbl_disco.pack(fill="x", pady=2)
        
        self.lbl_red = ctk.CTkLabel(
            self.frame_info,
            text="Red: Desconocido",
            font=self.fuente_pequena,
            anchor="w"
        )
        self.lbl_red.pack(fill="x", pady=2)
        
        # Separador
        self.separador = ctk.CTkFrame(self.barra_lateral, height=2, fg_color="gray")
        self.separador.pack(fill="x", padx=10, pady=10)
        
        # Título de acciones rápidas
        self.lbl_acciones = ctk.CTkLabel(
            self.barra_lateral,
            text="Acciones Rápidas",
            font=self.fuente_subtitulo
        )
        self.lbl_acciones.pack(pady=5)
        
        # Frame para los botones de acción rápida
        self.frame_acciones = ctk.CTkFrame(self.barra_lateral, fg_color="transparent")
        self.frame_acciones.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Botones de acción rápida
        self.btn_hora = ctk.CTkButton(
            self.frame_acciones,
            text="Hora Actual",
            command=self._comando_hora,
            width=120,
            height=30,
            corner_radius=10,
            font=self.fuente_pequena
        )
        self.btn_hora.pack(pady=5)
        
        self.btn_fecha = ctk.CTkButton(
            self.frame_acciones,
            text="Fecha Actual",
            command=self._comando_fecha,
            width=120,
            height=30,
            corner_radius=10,
            font=self.fuente_pequena
        )
        self.btn_fecha.pack(pady=5)
        
        self.btn_navegador = ctk.CTkButton(
            self.frame_acciones,
            text="Abrir Navegador",
            command=self._comando_abrir_navegador,
            width=120,
            height=30,
            corner_radius=10,
            font=self.fuente_pequena
        )
        self.btn_navegador.pack(pady=5)
        
        self.btn_nota = ctk.CTkButton(
            self.frame_acciones,
            text="Tomar Nota",
            command=self._comando_tomar_nota,
            width=120,
            height=30,
            corner_radius=10,
            font=self.fuente_pequena
        )
        self.btn_nota.pack(pady=5)
    
    def _crear_barra_estado(self):
        """Crea la barra de estado inferior."""
        # Frame para la barra de estado
        self.barra_estado = ctk.CTkFrame(self, height=25, corner_radius=0)
        self.barra_estado.grid(row=2, column=0, columnspan=2, sticky="sew")
        
        # Etiqueta de estado
        self.lbl_estado = ctk.CTkLabel(
            self.barra_estado,
            text="Listo",
            font=self.fuente_pequena,
            anchor="w"
        )
        self.lbl_estado.pack(side="left", padx=10)
        
        # Hora actual
        self.lbl_hora = ctk.CTkLabel(
            self.barra_estado,
            text="",
            font=self.fuente_pequena,
            anchor="e"
        )
        self.lbl_hora.pack(side="right", padx=10)
        
        # Actualizar la hora cada segundo
        self._actualizar_hora()
    
    def _actualizar_hora(self):
        """Actualiza la hora en la barra de estado."""
        ahora = datetime.datetime.now().strftime("%H:%M:%S")
        self.lbl_hora.configure(text=ahora)
        self.after(1000, self._actualizar_hora)
    
    def _iniciar_actualizacion_estadisticas(self):
        """Inicia la actualización periódica de las estadísticas del sistema."""
        def actualizar():
            try:
                # Obtener uso de CPU
                cpu_percent = psutil.cpu_percent(interval=1)
                self.lbl_cpu.configure(text=f"CPU: {cpu_percent}%")
                
                # Obtener uso de memoria
                memoria = psutil.virtual_memory()
                memoria_percent = memoria.percent
                memoria_total = memoria.total / (1024 ** 3)  # Convertir a GB
                memoria_usada = memoria.used / (1024 ** 3)  # Convertir a GB
                self.lbl_memoria.configure(
                    text=f"Memoria: {memoria_percent}% ({memoria_usada:.1f} GB / {memoria_total:.1f} GB)"
                )
                
                # Obtener uso de disco
                disco = psutil.disk_usage('/')
                disco_percent = disco.percent
                disco_total = disco.total / (1024 ** 3)  # Convertir a GB
                disco_usado = disco.used / (1024 ** 3)  # Convertir a GB
                self.lbl_disco.configure(
                    text=f"Disco: {disco_percent}% ({disco_usado:.1f} GB / {disco_total:.1f} GB)"
                )
                
                # Obtener estado de la red
                try:
                    direcciones = psutil.net_if_addrs()
                    interfaces = [k for k in direcciones if k != 'lo']
                    if interfaces:
                        self.lbl_red.configure(text=f"Red: {interfaces[0]}" if interfaces else "Red: Desconocido")
                except:
                    pass
                
            except Exception as e:
                logging.error(f"Error actualizando estadísticas: {e}")
            
            # Programar la próxima actualización
            self.after(5000, actualizar)
        
        # Iniciar la actualización
        actualizar()
    
    def _cambiar_tema(self, tema=None):
        """Cambia el tema de la aplicación."""
        if tema is None:
            tema = self.var_tema.get()
        
        self.tema_actual = tema
        tema_config = TEMAS.get(tema, TEMAS['Dark Mode'])
        
        # Cambiar el tema de la aplicación
        if tema in ['Dark Mode', 'Midnight Blue', 'Emerald Forest', 'Sunset Orange']:
            ctk.set_appearance_mode("dark")
            self.tema_oscuro = True
        else:
            ctk.set_appearance_mode("light")
            self.tema_oscuro = False
        
        # Actualizar colores de los widgets
        self._actualizar_colores(tema_config)
    
    def _actualizar_colores(self, tema):
        """Actualiza los colores de los widgets según el tema seleccionado."""
        # Actualizar colores de la barra superior
        self.barra_superior.configure(fg_color=tema['bg'])
        self.titulo.configure(text_color=tema['fg'])
        
        # Actualizar colores de la barra de estado
        self.barra_estado.configure(fg_color=tema['secondary'])
        self.lbl_estado.configure(text_color=tema['fg'])
        self.lbl_hora.configure(text_color=tema['fg'])
        
        # Actualizar colores de los botones
        self.btn_microfono.configure(
            fg_color=tema['accent'],
            hover_color=tema['hover'],
            text_color=tema['fg']
        )
        
        self.btn_config.configure(
            fg_color=tema['panel'],
            hover_color=tema['panel_hover']
        )
        
        # Actualizar colores de las pestañas
        self.tabs.configure(
            fg_color=tema['bg'],
            segmented_button_fg_color=tema['accent'],
            segmented_button_selected_color=tema['accent_hover'],
            segmented_button_selected_hover_color=tema['hover'],
            text_color=tema['fg']
        )
        
        # Actualizar colores del área de chat
        self.texto_chat.configure(
            fg_color=tema['panel'],
            text_color=tema['text'],
            scrollbar_button_color=tema['accent'],
            scrollbar_button_hover_color=tema['hover']
        )
        
        # Actualizar colores de la entrada de texto
        self.entry_mensaje.configure(
            fg_color=tema['panel'],
            text_color=tema['text'],
            placeholder_text_color=tema['text_secondary']
        )
        
        # Actualizar colores de los botones de la barra lateral
        for btn in [self.btn_hora, self.btn_fecha, self.btn_navegador, self.btn_nota]:
            btn.configure(
                fg_color=tema['accent'],
                hover_color=tema['hover'],
                text_color=tema['fg']
            )
    
    def _actualizar_volumen(self, valor):
        """Actualiza el volumen y la etiqueta correspondiente."""
        self.volumen = valor
        self.lbl_volumen.configure(text=f"Volumen: {int(valor * 100)}%")
        # Aquí iría el código para actualizar el volumen del sistema
    
    def _actualizar_velocidad(self, valor):
        """Actualiza la velocidad y la etiqueta correspondiente."""
        self.velocidad = valor
        self.lbl_velocidad.configure(text=f"Velocidad de habla: {valor:.1f}x")
        # Aquí iría el código para actualizar la velocidad de habla del TTS
    
    def _actualizar_notificaciones(self):
        """Actualiza la configuración de notificaciones."""
        estado = self.var_notificaciones.get()
        # Aquí iría el código para activar/desactivar notificaciones
    
    def _guardar_configuracion(self):
        """Guarda la configuración actual."""
        config = {
            'tema': self.var_tema.get(),
            'volumen': self.volumen,
            'velocidad': self.velocidad,
            'notificaciones': self.var_notificaciones.get()
        }
        
        try:
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)
            
            self._mostrar_notificacion("Configuración guardada correctamente", "info")
        except Exception as e:
            self._mostrar_notificacion(f"Error al guardar la configuración: {e}", "error")
    
    def _cargar_configuracion(self):
        """Carga la configuración guardada."""
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r') as f:
                    config = json.load(f)
                
                self.var_tema.set(config.get('tema', self.tema_actual))
                self.volumen = config.get('volumen', self.volumen)
                self.velocidad = config.get('velocidad', self.velocidad)
                self.var_notificaciones.set(config.get('notificaciones', True))
                
                # Aplicar la configuración cargada
                self._cambiar_tema(self.var_tema.get())
                self.slider_volumen.set(self.volumen * 100)
                self.slider_velocidad.set(self.velocidad)
                
        except Exception as e:
            logging.error(f"Error cargando configuración: {e}")
    
    def _restaurar_configuracion(self):
        """Restaura la configuración predeterminada."""
        # Configuración por defecto
        self.var_tema.set('Dark Mode')
        self.volumen = 0.8
        self.velocidad = 1.0
        self.var_notificaciones.set(True)
        
        # Aplicar la configuración predeterminada
        self._cambiar_tema('Dark Mode')
        self.slider_volumen.set(self.volumen * 100)
        self.slider_velocidad.set(self.velocidad)
        
        # Mostrar notificación
        self._mostrar_notificacion("Configuración restaurada a los valores predeterminados", "info")
    
    def _mostrar_notificacion(self, mensaje, tipo="info"):
        """Muestra una notificación al usuario."""
        # Colores según el tipo de notificación
        colores = {
            "info": ("#0d6efd", "#ffffff"),
            "success": ("#198754", "#ffffff"),
            "warning": ("#ffc107", "#212529"),
            "error": ("#dc3545", "#ffffff")
        }
        
        # Obtener colores según el tipo de notificación
        bg_color, fg_color = colores.get(tipo.lower(), ("#0d6efd", "#ffffff"))
        
        # Crear la notificación
        notificacion = ctk.CTkToplevel(self)
        notificacion.title("Notificación")
        notificacion.geometry("300x80+{}+{}".format(
            self.winfo_x() + self.winfo_width() - 320,
            self.winfo_y() + self.winfo_height() - 100
        ))
        notificacion.attributes('-topmost', True)
        notificacion.overrideredirect(True)
        
        # Configurar el frame de la notificación
        frame = ctk.CTkFrame(notificacion, fg_color=bg_color, corner_radius=10)
        frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Etiqueta con el mensaje
        lbl_mensaje = ctk.CTkLabel(
            frame,
            text=mensaje,
            text_color=fg_color,
            font=self.fuente_normal,
            wraplength=280
        )
        lbl_mensaje.pack(expand=True, padx=10, pady=10)
        
        # Cerrar la notificación después de 3 segundos
        notificacion.after(3000, notificacion.destroy)
    
    def _alternar_microfono(self):
        """Alterna el estado del micrófono."""
        if not self.escuchando:
            self._iniciar_escucha()
        else:
            self._detener_escucha()
    
    def _iniciar_escucha(self):
        """Inicia la escucha del micrófono."""
        self.escuchando = True
        self.btn_microfono.configure(
            text="Detener Escucha",
            image=self.icono_detener,
            fg_color="#dc3545",
            hover_color="#bb2d3b"
        )
        
        # Mostrar notificación
        self._mostrar_notificacion("Escuchando... Habla ahora.", "info")
        
        # Aquí iría el código para iniciar la escucha del micrófono
        # Por ahora, simulamos el reconocimiento de voz después de 2 segundos
        self.after(2000, self._simular_reconocimiento_voz)
    
    def _detener_escucha(self):
        """Detiene la escucha del micrófono."""
        self.escuchando = False
        self.btn_microfono.configure(
            text="Iniciar Escucha",
            image=self.icono_microfono,
            fg_color="#2b5bff",
            hover_color="#1a42c4"
        )
        
        # Mostrar notificación
        self._mostrar_notificacion("Escucha detenida.", "info")
        
        # Aquí iría el código para detener la escucha del micrófono
    
    def _simular_reconocimiento_voz(self):
        """Simula el reconocimiento de voz (solo para prueba)."""
        if not self.escuchando:
            return
        
        # Frases de ejemplo para simular reconocimiento
        frases = [
            "Hola, ¿cómo estás?",
            "¿Qué hora es?",
            "Abre el navegador",
            "Reproduce música",
            "Busca información sobre inteligencia artificial",
            "Cierra la aplicación"
        ]
        
        # Seleccionar una frase aleatoria
        frase = random.choice(frases)
        
        # Mostrar la frase reconocida
        self._mostrar_mensaje("Usuario", frase)
        
        # Procesar el comando
        self._procesar_comando(frase)
    
    def _mostrar_mensaje(self, remitente, mensaje):
        """Muestra un mensaje en el área de chat."""
        # Habilitar edición del widget de texto
        self.texto_chat.configure(state="normal")
        
        # Configurar etiquetas para el formato
        self.texto_chat.tag_configure("remitente", font=(self.fuente_normal[0], self.fuente_normal[1], "bold"))
        self.texto_chat.tag_configure("mensaje", font=self.fuente_normal)
        self.texto_chat.tag_configure("hora", font=(self.fuente_pequena[0], self.fuente_pequena[1], "italic"))
        
        # Obtener la hora actual
        hora_actual = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Insertar el mensaje con formato
        self.texto_chat.insert("end", f"{remitente} ", "remitente")
        self.texto_chat.insert("end", f"({hora_autoctonahora})\n", "hora")
        self.texto_chat.insert("end", f"{mensaje}\n\n", "mensaje")
        
        # Desplazarse al final del texto
        self.texto_chat.see("end")
        
        # Deshabilitar edición del widget de texto
        self.texto_chat.configure(state="disabled")
        
        # Guardar el mensaje en el historial
        self._guardar_mensaje_historial(remitente, mensaje)
    
    def _guardar_mensaje_historial(self, remitente, mensaje):
        """Guarda un mensaje en el historial de la sesión actual."""
        mensaje_info = {
            "fecha_hora": datetime.datetime.now().isoformat(),
            "remitente": remitente,
            "mensaje": mensaje
        }
        
        self.historial_mensajes.append(mensaje_info)
        
        # Guardar en archivo si está configurado
        if self.historial_archivo:
            try:
                with open(self.historial_archivo, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(mensaje_info, ensure_ascii=False) + '\n')
            except Exception as e:
                logging.error(f"Error al guardar mensaje en el historial: {e}")
    
    def _cargar_historial_diario(self):
        """Carga el historial de mensajes del día actual."""
        # Crear directorio de historial si no existe
        os.makedirs("historial", exist_ok=True)
        
        # Nombre del archivo con la fecha actual
        fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d")
        self.historial_archivo = os.path.join("historial", f"chat_{fecha_actual}.jsonl")
        
        # Cargar mensajes si el archivo existe
        if os.path.exists(self.historial_archivo):
            try:
                with open(self.historial_archivo, 'r', encoding='utf-8') as f:
                    for linea in f:
                        mensaje = json.loads(linea.strip())
                        self.historial_mensajes.append(mensaje)
                
                # Mostrar mensaje de carga
                self._mostrar_notificacion(f"Historial cargado: {len(self.historial_mensajes)} mensajes", "info")
            except Exception as e:
                logging.error(f"Error al cargar el historial: {e}")
    
    def _es_wake_word(self, texto):
        """Verifica si el texto contiene una palabra de activación."""
        WAKE_WORDS = [
            'autogestión', 'auto gestión', 'auto-gestión', 'autogestion',
            'agp', 'a jipi', 'a jipi', 'a g p',
            'asistente', 'asistencia', 'asistir',
            'illo', 'hijo', 'hija', 'hijito',
            'compae', 'compa', 'compañero', 'compañera',
            'oye', 'oiga', 'escucha', 'hola asistente'
        ]
        
        # Normalizar el texto
        texto = texto.lower().strip()
        
        # Verificar coincidencias exactas primero
        for palabra in WAKE_WORDS:
            if palabra in texto:
                return True
        
        # Usar fuzzy matching para variaciones
        for palabra in WAKE_WORDS:
            # Calcular similitud con la biblioteca difflib
            similitud = difflib.SequenceMatcher(None, texto, palabra).ratio()
            if similitud > 0.7:  # Umbral de similitud ajustable
                logging.info(f"Wake word detectada por similitud: '{texto}' ≈ '{palabra}' ({similitud:.2f})")
                return True
        
        return False

    def _procesar_comando(self, texto):
        """Procesa un comando de voz o texto."""
        if not texto or not texto.strip():
            return
            
        # Convertir a minúsculas para facilitar la comparación
        texto = texto.lower().strip()
        
        # Verificar si es un comando directo o necesita wake word
        es_comando_directo = any(cmd in texto for cmd in [
            'hora', 'fecha', 'busca', 'buscar', 'abre', 'reproduce',
            'cierra', 'salir', 'adiós', 'gracias', 'cómo estás'
        ])
        
        # Si no es un comando directo, verificar wake word
        if not es_comando_directo and not self._es_wake_word(texto):
            logging.debug(f"No se detectó wake word en: {texto}")
            return
            
        # Limpiar el texto quitando las palabras de activación
        for palabra in WAKE_WORDS:
            texto = texto.replace(palabra, '').strip()
        if not texto:
            texto = "¿Sí? ¿En qué puedo ayudarte?"
        
        # Mostrar el comando en la interfaz
        self._mostrar_mensaje("Usuario", texto)
        
        # Procesar comandos específicos
        respuesta = self._procesar_comandos_especificos(texto)
        
        # Si no se encontró un comando específico, usar el procesamiento de conversación
        if not respuesta:
            respuesta = self._procesar_conversacion(texto)
        
        # Mostrar la respuesta
        if respuesta:
            self._mostrar_mensaje("Asistente", respuesta)
            # Aquí iría el código para convertir la respuesta a voz
            if hasattr(self, 'hablar') and callable(self.hablar):
                self.hablar(respuesta)
    
    def _procesar_comandos_especificos(self, texto):
        """Procesa comandos específicos y devuelve respuestas."""
        texto = texto.lower().strip()
        
        # Comandos de saludo
        if any(palabra in texto for palabra in ["hola", "buenos días", "buenas tardes", "buenas noches", "qué tal", "cómo estás"]):
            saludos = [
                "¡Hola! ¿En qué puedo ayudarte hoy?",
                "¡Hola! ¿Cómo estás?",
                "¡Hola! ¿En qué puedo asistirte?",
                "¡Hola! Estoy listo para ayudarte.",
                "¡Buenas! ¿Qué necesitas?"
            ]
            return random.choice(saludos)
        
        # Comandos de tiempo
        if any(palabra in texto for palabra in ["qué hora es", "dime la hora", "hora actual"]):
            hora_actual = datetime.datetime.now().strftime("%H:%M")
            return f"Son las {hora_actual}."
        
        if any(palabra in texto for palabra in ["qué día es hoy", "qué fecha es hoy", "fecha actual"]):
            fecha_actual = datetime.datetime.now().strftime("%A, %d de %B de %Y")
            return f"Hoy es {fecha_actual}."
        
        # Comandos de navegación
        if any(palabra in texto for palabra in ["abre el navegador", "abrir navegador", "abre chrome", "abre firefox"]):
            try:
                webbrowser.open("https://www.google.com")
                return "Abriendo el navegador web en Google."
            except Exception as e:
                return f"No pude abrir el navegador: {str(e)}"
        
        if "busca " in texto or "buscar " in texto or "busca en internet" in texto:
            busqueda = re.sub(r'(busca|buscar|en internet|por favor|quiero)', '', texto, flags=re.IGNORECASE).strip()
            if busqueda:
                try:
                    webbrowser.open(f"https://www.google.com/search?q={busqueda}")
                    return f"Buscando en internet: {busqueda}"
                except Exception as e:
                    return f"No pude realizar la búsqueda: {str(e)}"
        
        # Comandos de sistema
        if any(palabra in texto for palabra in ["cierra la aplicación", "salir", "ciérrate", "hasta luego"]):
            self.after(1000, self.quit)
            return "Cerrando la aplicación. ¡Hasta luego!"
        
        # Comandos de ayuda
        if any(palabra in texto for palabra in ["qué puedes hacer", "ayuda", "qué comandos hay"]):
            return (
                "Puedo ayudarte con las siguientes tareas:\n"
                "• Decir la hora o fecha actual\n"
                "• Buscar en internet\n"
                "• Abrir el navegador\n"
                "• Mantener una conversación básica\n\n"
                "Solo dime qué necesitas y haré lo posible por ayudarte."
            )
        
        # Comandos de control
        if any(palabra in texto for palabra in ["escucha", "atención", "estás ahí"]):
            return "Sí, te escucho. ¿En qué puedo ayudarte?"
            
        if any(palabra in texto for palabra in ["cállate", "silencio", "deja de escuchar"]):
            return "Entendido, me pondré en modo silencio. Di mi nombre cuando necesites ayuda."
        
        return ""
    
    def _procesar_conversacion(self, texto):
        """Procesa el texto como una conversación normal."""
        texto = texto.lower().strip()
        
        # Saludos y estado
        if any(palabra in texto for palabra in ["cómo estás", "qué tal", "cómo te sientes"]):
            return random.choice([
                "¡Estoy funcionando perfectamente, gracias por preguntar!",
                "Todo en orden por aquí, ¿y tú qué tal estás?",
                "Estoy listo para ayudarte en lo que necesites.",
                "¡Genial! Listo para ayudarte con lo que necesites.",
                "Estoy aquí, esperando tus órdenes."
            ])
        
        # Agradecimientos
        elif any(palabra in texto for palabra in ["gracias", "muchas gracias", "te lo agradezco", "muy amable"]):
            return random.choice([
                "¡De nada! Estoy aquí para ayudarte.",
                "¡Es un placer ayudarte!",
                "No hay de qué. ¿Necesitas algo más?",
                "¡Para eso estoy! ¿En qué más puedo ayudarte?",
                "¡No hay problema! Estoy para servirte."
            ])
        
        # Despedidas
        elif any(palabra in texto for palabra in ["adiós", "hasta luego", "nos vemos", "hasta pronto"]):
            return random.choice([
                "¡Hasta luego! Que tengas un excelente día.",
                "¡Adiós! Vuelve pronto.",
                "Hasta la próxima. ¡Cuídate!",
                "¡Hasta pronto! Si necesitas algo, aquí estaré.",
                "¡Que tengas un gran día! Hasta la próxima."
            ])
        
        # Preguntas sobre el asistente
        elif any(palabra in texto for palabra in ["quién eres", "cómo te llamas", "cuál es tu nombre"]):
            return "Soy AGP, tu asistente de voz personal. Estoy aquí para ayudarte con lo que necesites."
        
        # Preguntas sobre habilidades
        elif any(palabra in texto for palabra in ["qué sabes hacer", "qué puedes hacer", "para qué sirves"]):
            return (
                "Puedo ayudarte con diversas tareas como:\n"
                "• Responder preguntas generales\n"
                "• Realizar búsquedas en internet\n"
                "• Decirte la hora y fecha actual\n"
                "• Mantener una conversación básica\n"
                "• Y mucho más. ¡Pregúntame lo que necesites!"
            )
        
        # Preguntas sobre el creador
        elif any(palabra in texto for palabra in ["quién te creó", "quién te programó", "quién es tu creador"]):
            return "Fui creado para ayudarte con diferentes tareas. Estoy aquí para hacerte la vida más fácil."
        
        # Preguntas personales
        elif any(palabra in texto for palabra in ["cómo estás hoy", "qué tal tu día", "cómo te ha ido"]):
            return random.choice([
                "Soy un asistente, así que siempre estoy al 100% listo para ayudarte.",
                "No tengo días buenos ni malos, siempre estoy aquí para ti.",
                "¡Excelente! Sobre todo si puedo ayudarte con algo."
            ])
        
        # Si no se reconoce la intención, usar un modelo de lenguaje o devolver una respuesta genérica
        return self._generar_respuesta_generica(texto)
    
    def _generar_respuesta_generica(self, texto):
        """Genera una respuesta genérica basada en el contexto."""
        # Análisis simple de sentimiento
        palabras_positivas = ["feliz", "genial", "increíble", "maravilloso", "fantástico"]
        palabras_negativas = ["triste", "mal", "enojado", "molesto", "cansado"]
        
        if any(palabra in texto for palabra in palabras_positivas):
            return "¡Me alegra oír eso! ¿En qué más puedo ayudarte?"
            
        if any(palabra in texto for palabra in palabras_negativas):
            return "Lamento escuchar eso. ¿Hay algo en lo que pueda ayudarte a sentirte mejor?"
        
        # Respuestas genéricas basadas en el tipo de mensaje
        if "?" in texto:
            return random.choice([
                "Buena pregunta. ¿Qué más te gustaría saber?",
                "No estoy seguro de saber la respuesta a eso. ¿Puedo ayudarte con algo más?",
                "Interesante pregunta. ¿Hay algo más en lo que pueda ayudarte?"
            ])
        
        # Respuesta genérica por defecto
        return random.choice([
            "No estoy seguro de haber entendido. ¿Podrías reformularlo?",
            "Interesante. ¿Podrías darme más detalles?",
            "No estoy seguro de cómo responder a eso. ¿Hay algo más en lo que pueda ayudarte?",
            "¿Podrías ser más específico? Quiero asegurarme de entenderte bien.",
            "Voy a tomar nota de eso. ¿Hay algo más en lo que pueda ayudarte?"
        ])
    
    def _enviar_mensaje(self):
        """Envía el mensaje escrito en el campo de entrada."""
        mensaje = self.entry_mensaje.get().strip()
        if mensaje:
            self._procesar_comando(mensaje)
            self.entry_mensaje.delete(0, "end")
    
    def _buscar_mensajes(self):
        """Busca mensajes que coincidan con el término de búsqueda."""
        termino = self.entry_buscar.get().strip().lower()
        if not termino:
            self._mostrar_notificacion("Por favor, ingresa un término de búsqueda.", "warning")
            return
        
        # Buscar en los mensajes cargados
        coincidencias = []
        for i, mensaje in enumerate(self.historial_mensajes):
            if termino in mensaje.get('mensaje', '').lower() or termino in mensaje.get('remitente', '').lower():
                coincidencias.append(mensaje)
        
        # Mostrar resultados
        if coincidencias:
            self._mostrar_notificacion(f"Se encontraron {len(coincidencias)} coincidencias.", "success")
            
            # Crear ventana de resultados
            resultados = ctk.CTkToplevel(self)
            resultados.title(f"Resultados de búsqueda: {termino}")
            resultados.geometry("600x400")
            
            # Frame para los resultados
            frame_resultados = ctk.CTkScrollableFrame(resultados)
            frame_resultados.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Mostrar cada coincidencia
            for i, mensaje in enumerate(coincidencias):
                # Frame para cada mensaje
                frame_mensaje = ctk.CTkFrame(frame_resultados, corner_radius=5)
                frame_mensaje.pack(fill="x", pady=2)
                
                # Remitente y fecha
                remitente = mensaje.get('remitente', 'Desconocido')
                fecha = datetime.datetime.fromisoformat(mensaje.get('fecha_hora', datetime.datetime.now().isoformat()))
                fecha_str = fecha.strftime("%d/%m/%Y %H:%M:%S")
                
                lbl_info = ctk.CTkLabel(
                    frame_mensaje,
                    text=f"{remitente} - {fecha_str}",
                    font=(self.fuente_pequena[0], self.fuente_pequena[1], "bold"),
                    anchor="w"
                )
                lbl_info.pack(fill="x", padx=5, pady=(5, 0))
                
                # Contenido del mensaje
                lbl_mensaje = ctk.CTkLabel(
                    frame_mensaje,
                    text=mensaje.get('mensaje', ''),
                    font=self.fuente_pequena,
                    anchor="w",
                    wraplength=550,
                    justify="left"
                )
                lbl_mensaje.pack(fill="x", padx=5, pady=(0, 5))
        else:
            self._mostrar_notificacion("No se encontraron coincidencias.", "info")
    
    def _mostrar_menu_exportar(self):
        """Muestra el menú de opciones de exportación."""
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Exportar a TXT", command=lambda: self._exportar_chat("txt"))
        menu.add_command(label="Exportar a JSON", command=lambda: self._exportar_chat("json"))
        menu.add_command(label="Exportar a PDF", command=lambda: self._exportar_chat("pdf"))
        
        # Mostrar el menú cerca del botón de exportar
        try:
            menu.tk_popup(
                self.btn_exportar.winfo_rootx(),
                self.btn_exportar.winfo_rooty() + self.btn_exportar.winfo_height()
            )
        finally:
            menu.grab_release()
    
    def _exportar_chat(self, formato):
        """Exporta el chat al formato especificado."""
        if not self.historial_mensajes:
            self._mostrar_notificacion("No hay mensajes para exportar.", "warning")
            return
        
        # Obtener la fecha actual para el nombre del archivo
        fecha_actual = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"chat_exportado_{fecha_actual}"
        
        try:
            if formato == "txt":
                nombre_archivo += ".txt"
                with open(nombre_archivo, 'w', encoding='utf-8') as f:
                    for mensaje in self.historial_mensajes:
                        fecha = datetime.datetime.fromisoformat(mensaje.get('fecha_hora', datetime.datetime.now().isoformat()))
                        fecha_str = fecha.strftime("%d/%m/%Y %H:%M:%S")
                        f.write(f"[{fecha_str}] {mensaje.get('remitente', 'Desconocido')}: {mensaje.get('mensaje', '')}\n")
                
                self._mostrar_notificacion(f"Chat exportado a {nombre_archivo}", "success")
                
            elif formato == "json":
                nombre_archivo += ".json"
                with open(nombre_archivo, 'w', encoding='utf-8') as f:
                    json.dump(self.historial_mensajes, f, ensure_ascii=False, indent=2)
                
                self._mostrar_notificacion(f"Chat exportado a {nombre_archivo}", "success")
                
            elif formato == "pdf":
                try:
                    from reportlab.lib.pagesizes import letter
                    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
                    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                    from reportlab.lib.enums import TA_LEFT
                    from reportlab.lib import colors
                    
                    nombre_archivo += ".pdf"
                    
                    # Crear el documento PDF
                    doc = SimpleDocTemplate(nombre_archivo, pagesize=letter)
                    styles = getSampleStyleSheet()
                    
                    # Estilos personalizados
                    styles.add(ParagraphStyle(
                        name='Remitente',
                        parent=styles['Normal'],
                        fontName='Helvetica-Bold',
                        fontSize=10,
                        textColor=colors.blue,
                        spaceAfter=2
                    ))
                    
                    styles.add(ParagraphStyle(
                        name='Mensaje',
                        parent=styles['Normal'],
                        fontName='Helvetica',
                        fontSize=10,
                        textColor=colors.black,
                        spaceAfter=10,
                        leftIndent=20
                    ))
                    
                    # Crear el contenido del PDF
                    contenido = []
                    
                    # Título
                    titulo = Paragraph("Historial de Chat", styles['Title'])
                    contenido.append(titulo)
                    contenido.append(Spacer(1, 12))
                    
                    # Fecha de exportación
                    fecha_exportacion = f"Exportado el: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
                    contenido.append(Paragraph(fecha_exportacion, styles['Italic']))
                    contenido.append(Spacer(1, 20))
                    
                    # Agregar cada mensaje al PDF
                    for mensaje in self.historial_mensajes:
                        fecha = datetime.datetime.fromisoformat(mensaje.get('fecha_hora', datetime.datetime.now().isoformat()))
                        fecha_str = fecha.strftime("%d/%m/%Y %H:%M:%S")
                        remitente = mensaje.get('remitente', 'Desconocido')
                        
                        # Agregar remitente y fecha
                        info = f"<b>{remitente}</b> - {fecha_str}"
                        contenido.append(Paragraph(info, styles['Remitente']))
                        
                        # Agregar mensaje
                        contenido.append(Paragraph(mensaje.get('mensaje', ''), styles['Mensaje']))
                    
                    # Generar el PDF
                    doc.build(contenido)
                    
                    self._mostrar_notificacion(f"Chat exportado a {nombre_archivo}", "success")
                    
                except ImportError:
                    self._mostrar_notificacion("Error: El módulo 'reportlab' no está instalado.", "error")
                    return
                except Exception as e:
                    self._mostrar_notificacion(f"Error al exportar a PDF: {str(e)}", "error")
                    return
            
            else:
                self._mostrar_notificacion("Formato de exportación no válido.", "error")
                return
            
            # Abrir el archivo después de exportar
            try:
                if sys.platform == 'win32':
                    os.startfile(nombre_archivo)
                elif sys.platform == 'darwin':  # macOS
                    subprocess.run(['open', nombre_archivo])
                else:  # Linux y otros
                    subprocess.run(['xdg-open', nombre_archivo])
            except:
                pass
                
        except Exception as e:
            self._mostrar_notificacion(f"Error al exportar el chat: {str(e)}", "error")
    
    def _comando_hora(self):
        """Muestra la hora actual."""
        hora_actual = datetime.datetime.now().strftime("%H:%M:%S")
        self._mostrar_mensaje("Asistente", f"La hora actual es {hora_actual}.")
        # self.hablar(f"Son las {hora_actual.replace(':', ' ')}")
    
    def _comando_fecha(self):
        """Muestra la fecha actual."""
        from datetime import datetime
        from locale import setlocale, LC_TIME
        
        try:
            setlocale(LC_TIME, 'es_ES.UTF-8')
        except:
            try:
                setlocale(LC_TIME, 'Spanish_Spain.1252')
            except:
                pass
        
        fecha_actual = datetime.now()
        fecha_str = fecha_actual.strftime("%A, %d de %B de %Y")
        
        self._mostrar_mensaje("Asistente", f"Hoy es {fecha_str}.")
        # self.hablar(f"Hoy es {fecha_str}")
    
    def _comando_abrir_navegador(self):
        """Abre el navegador web predeterminado."""
        try:
            webbrowser.open("https://www.google.com")
            self._mostrar_mensaje("Asistente", "Abriendo el navegador web.")
        except Exception as e:
            self._mostrar_mensaje("Asistente", f"No pude abrir el navegador: {str(e)}")
    
    def _comando_tomar_nota(self):
        """Abre un diálogo para tomar una nota."""
        # Crear ventana de diálogo
        dialogo = ctk.CTkToplevel(self)
        dialogo.title("Tomar Nota")
        dialogo.geometry("500x300")
        dialogo.transient(self)
        dialogo.grab_set()
        
        # Frame principal
        frame = ctk.CTkFrame(dialogo)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título de la nota
        lbl_titulo = ctk.CTkLabel(frame, text="Título:", font=self.fuente_normal)
        lbl_titulo.pack(anchor="w", pady=(5, 0))
        
        entry_titulo = ctk.CTkEntry(frame, font=self.fuente_normal)
        entry_titulo.pack(fill="x", pady=(0, 10))
        
        # Contenido de la nota
        lbl_contenido = ctk.CTkLabel(frame, text="Contenido:", font=self.fuente_normal)
        lbl_contenido.pack(anchor="w")
        
        text_contenido = ctk.CTkTextbox(frame, font=self.fuente_normal)
        text_contenido.pack(fill="both", expand=True)
        
        # Frame para los botones
        frame_botones = ctk.CTkFrame(frame, fg_color="transparent")
        frame_botones.pack(fill="x", pady=(10, 0))
        
        # Función para guardar la nota
        def guardar_nota():
            titulo = entry_titulo.get().strip()
            contenido = text_contenido.get("1.0", "end-1c").strip()
            
            if not titulo and not contenido:
                self._mostrar_notificacion("La nota está vacía. No se guardará.", "warning")
                dialogo.destroy()
                return
            
            # Crear directorio de notas si no existe
            os.makedirs("notas", exist_ok=True)
            
            # Generar nombre de archivo con la fecha y hora actual
            fecha_actual = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"notas/nota_{fecha_actual}.txt"
            
            try:
                with open(nombre_archivo, 'w', encoding='utf-8') as f:
                    if titulo:
                        f.write(f"# {titulo}\n\n")
                    f.write(contenido)
                
                self._mostrar_notificacion("Nota guardada correctamente.", "success")
                dialogo.destroy()
                
            except Exception as e:
                self._mostrar_notificacion(f"Error al guardar la nota: {str(e)}", "error")
        
        # Botones
        btn_guardar = ctk.CTkButton(
            frame_botones,
            text="Guardar",
            command=guardar_nota,
            width=100
        )
        btn_guardar.pack(side="right", padx=5)
        
        btn_cancelar = ctk.CTkButton(
            frame_botones,
            text="Cancelar",
            command=dialogo.destroy,
            fg_color="#6c757d",
            hover_color="#5a6268",
            width=100
        )
        btn_cancelar.pack(side="right", padx=5)
        
        # Centrar la ventana
        dialogo.update_idletasks()
        ancho = dialogo.winfo_width()
        alto = dialogo.winfo_height()
        x = (dialogo.winfo_screenwidth() // 2) - (ancho // 2)
        y = (dialogo.winfo_screenheight() // 2) - (alto // 2)
        dialogo.geometry(f'{ancho}x{alto}+{x}+{y}')
        
        # Enfocar el campo de título
        entry_titulo.focus_set()
    
    def _iniciar_dictado(self):
        """Abre un diálogo para iniciar el dictado por voz."""
        if not hasattr(self, 'ventana_dictado') or not self.ventana_dictado.winfo_exists():
            self.ventana_dictado = ctk.CTkToplevel(self)
            self.ventana_dictado.title("Dictado por Voz")
            self.ventana_dictado.geometry("500x300")
            self.ventana_dictado.transient(self)
            self.ventana_dictado.grab_set()
            
            # Frame principal
            frame = ctk.CTkFrame(self.ventana_dictado)
            frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Título
            lbl_titulo = ctk.CTkLabel(
                frame,
                text="Dictado por Voz",
                font=self.fuente_subtitulo
            )
            lbl_titulo.pack(pady=(10, 20))
            
            # Área de texto para el dictado
            self.texto_dictado = ctk.CTkTextbox(
                frame,
                font=self.fuente_normal,
                wrap="word"
            )
            self.texto_dictado.pack(fill="both", expand=True, padx=10, pady=5)
            
            # Frame para los botones
            frame_botones = ctk.CTkFrame(frame, fg_color="transparent")
            frame_botones.pack(fill="x", pady=(10, 0))
            
            # Botón de grabar/detener
            self.grabando = False
            
            def alternar_grabacion():
                if not self.grabando:
                    # Iniciar grabación
                    self.grabando = True
                    btn_grabar.configure(
                        text="Detener Grabación",
                        fg_color="#dc3545",
                        hover_color="#bb2d3b"
                    )
                    self.texto_dictado.delete("1.0", "end")
                    self.texto_dictado.insert("1.0", "Escuchando... Habla ahora.\n\n")
                    # Aquí iría el código para iniciar la grabación de voz
                else:
                    # Detener grabación
                    self.grabando = False
                    btn_grabar.configure(
                        text="Iniciar Grabación",
                        fg_color="#2b5bff",
                        hover_color="#1a42c4"
                    )
                    # Aquí iría el código para detener la grabación de voz
            
            btn_grabar = ctk.CTkButton(
                frame_botones,
                text="Iniciar Grabación",
                command=alternar_grabacion,
                width=150,
                height=40,
                corner_radius=20,
                fg_color="#2b5bff",
                hover_color="#1a42c4"
            )
            btn_grabar.pack(side="left", padx=5)
            
            # Función para finalizar el dictado
            def finalizar_dictado():
                texto = self.texto_dictado.get("1.0", "end-1c").strip()
                if texto and not texto == "Escuchando... Habla ahora.\n\n":
                    self.entry_mensaje.delete(0, "end")
                    self.entry_mensaje.insert(0, texto)
                    self._enviar_mensaje()
                self.ventana_dictado.destroy()
            
            btn_listo = ctk.CTkButton(
                frame_botones,
                text="Listo",
                command=finalizar_dictado,
                width=100,
                height=40,
                corner_radius=20,
                fg_color="#28a745",
                hover_color="#218838"
            )
            btn_listo.pack(side="right", padx=5)
            
            # Centrar la ventana
            self.ventana_dictado.update_idletasks()
            ancho = self.ventana_dictado.winfo_width()
            alto = self.ventana_dictado.winfo_height()
            x = (self.ventana_dictado.winfo_screenwidth() // 2) - (ancho // 2)
            y = (self.ventana_dictado.winfo_screenheight() // 2) - (alto // 2)
            self.ventana_dictado.geometry(f'{ancho}x{alto}+{x}+{y}')
            
            # Enfocar la ventana de dictado
            self.ventana_dictado.focus_set()
        else:
            self.ventana_dictado.lift()
    
    def _mostrar_configuracion(self):
        """Muestra la ventana de configuración."""
        # Cambiar a la pestaña de configuración
        self.tabs.set("Configuración")

# Función principal
def main():
    # Configurar el tema de la aplicación
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Crear y ejecutar la aplicación
    app = InterfazAsistente()
    
    # Cargar configuración
    app._cargar_configuracion()
    
    # Mostrar ventana de bienvenida
    app.after(500, lambda: app._mostrar_mensaje(
        "Asistente", 
        "¡Hola! Soy tu asistente de voz. ¿En qué puedo ayudarte hoy?"
    ))
    
    # Iniciar el bucle principal
    app.mainloop()

if __name__ == "__main__":
    main()
