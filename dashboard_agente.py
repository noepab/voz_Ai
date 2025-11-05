"""
Dashboard completo para el Agente de IA AGP
"""
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from datetime import datetime
import json
import os
import threading

class DashboardAgente:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("AGP - Panel de Control")
        self.root.geometry("1200x800")
        
        # Configuración de temas
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Variables de estado
        self.estado_agente = "Inactivo"
        self.modo_oscuro = True
        self.mensajes = []
        self.comandos_disponibles = [
            "Abrir navegador",
            "Tomar nota",
            "Buscar en internet",
            "Reproducir música",
            "Configuración"
        ]
        
        # Configurar la interfaz
        self._configurar_interfaz()
        
    def _configurar_interfaz(self):
        # Configurar el grid principal
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # ===== BARRA LATERAL IZQUIERDA =====
        self.barra_lateral = ctk.CTkFrame(self.root, width=250, corner_radius=0)
        self.barra_lateral.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.barra_lateral.grid_propagate(False)
        
        # Logo y título
        self.logo_frame = ctk.CTkFrame(self.barra_lateral, fg_color="transparent")
        self.logo_frame.pack(pady=20, padx=10, fill="x")
        
        self.titulo = ctk.CTkLabel(
            self.logo_frame,
            text="AGP AI",
            font=("Roboto", 24, "bold"),
            text_color="#4cc9f0"
        )
        self.titulo.pack(side="left", padx=10)
        
        # Botones de navegación
        self.botones_navegacion = [
            ("Inicio", "🏠"),
            ("Chat", "💬"),
            ("Comandos", "⌨️"),
            ("Configuración", "⚙️"),
            ("Estadísticas", "📊")
        ]
        
        for texto, icono in self.botones_navegacion:
            btn = ctk.CTkButton(
                self.barra_lateral,
                text=f"{icono}  {texto}",
                font=("Segoe UI", 14),
                anchor="w",
                fg_color="transparent",
                hover_color=("gray70", "gray30"),
                command=lambda t=texto: self.cambiar_seccion(t)
            )
            btn.pack(fill="x", padx=10, pady=5)
        
        # Estado del agente
        self.estado_frame = ctk.CTkFrame(self.barra_lateral, fg_color="transparent")
        self.estado_frame.pack(side="bottom", fill="x", padx=10, pady=20)
        
        self.etiqueta_estado = ctk.CTkLabel(
            self.estado_frame,
            text=f"Estado: {self.estado_agente}",
            font=("Segoe UI", 12)
        )
        self.etiqueta_estado.pack(side="left")
        
        # ===== BARRA SUPERIOR =====
        self.barra_superior = ctk.CTkFrame(self.root, height=60, corner_radius=0)
        self.barra_superior.grid(row=0, column=1, sticky="nsew", columnspan=2)
        self.barra_superior.grid_propagate(False)
        
        # Barra de búsqueda
        self.barra_busqueda = ctk.CTkEntry(
            self.barra_superior,
            placeholder_text="Buscar...",
            width=400,
            corner_radius=20
        )
        self.barra_busqueda.pack(side="left", padx=20, pady=10, fill="x", expand=True)
        
        # Botón de búsqueda
        self.boton_buscar = ctk.CTkButton(
            self.barra_superior,
            text="🔍",
            width=40,
            command=self.buscar
        )
        self.boton_buscar.pack(side="left", padx=(0, 20), pady=10)
        
        # ===== ÁREA PRINCIPAL =====
        self.area_principal = ctk.CTkFrame(self.root, corner_radius=0)
        self.area_principal.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        
        # Pestañas
        self.tabs = ctk.CTkTabview(self.area_principal)
        self.tabs.pack(expand=True, fill="both", padx=5, pady=5)
        
        # Pestaña de chat
        self.tab_chat = self.tabs.add("Chat")
        self._configurar_tab_chat()
        
        # Pestaña de comandos
        self.tab_comandos = self.tabs.add("Comandos")
        self._configurar_tab_comandos()
        
        # Pestaña de configuración
        self.tab_config = self.tabs.add("Configuración")
        self._configurar_tab_config()
        
        # Ocultar pestañas por defecto
        self.tabs.set("Chat")
        
        # ===== BARRA INFERIOR =====
        self.barra_inferior = ctk.CTkFrame(self.root, height=40, corner_radius=0)
        self.barra_inferior.grid(row=2, column=1, sticky="nsew", columnspan=2)
        
        self.etiqueta_estado = ctk.CTkLabel(
            self.barra_inferior,
            text="Listo",
            font=("Segoe UI", 10)
        )
        self.etiqueta_estado.pack(side="left", padx=20)
        
        # ===== BARRA LATERAL DERECHA (OPCIONAL) =====
        self.barra_derecha = ctk.CTkFrame(self.root, width=300, corner_radius=0)
        self.barra_derecha.grid(row=0, column=2, rowspan=3, sticky="nsew", padx=(0, 5), pady=5)
        
        # Widgets de la barra derecha
        self.etiqueta_info = ctk.CTkLabel(
            self.barra_derecha,
            text="Información del sistema",
            font=("Segoe UI", 14, "bold")
        )
        self.etiqueta_info.pack(pady=10)
        
        # Ajustar tamaños de columnas
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
    
    def _configurar_tab_chat(self):
        # Área de mensajes
        self.frame_mensajes = ctk.CTkScrollableFrame(self.tab_chat)
        self.frame_mensajes.pack(expand=True, fill="both", padx=5, pady=5)
        
        # Área de entrada
        self.frame_entrada = ctk.CTkFrame(self.tab_chat, height=100)
        self.frame_entrada.pack(fill="x", padx=5, pady=5)
        
        self.entrada_mensaje = ctk.CTkTextbox(self.frame_entrada, height=80)
        self.entrada_mensaje.pack(side="left", expand=True, fill="both", padx=5, pady=5)
        
        self.boton_enviar = ctk.CTkButton(
            self.frame_entrada,
            text="Enviar",
            width=100,
            command=self.enviar_mensaje
        )
        self.boton_enviar.pack(side="right", padx=5, pady=5)
        
        # Atajos de teclado
        self.entrada_mensaje.bind("<Return>", lambda e: self.enviar_mensaje())
    
    def _configurar_tab_comandos(self):
        # Lista de comandos
        self.lista_comandos = ctk.CTkScrollableFrame(self.tab_comandos)
        self.lista_comandos.pack(expand=True, fill="both", padx=5, pady=5)
        
        for comando in self.comandos_disponibles:
            frame = ctk.CTkFrame(self.lista_comandos, height=50)
            frame.pack(fill="x", pady=2)
            
            etiqueta = ctk.CTkLabel(frame, text=comando, font=("Segoe UI", 12))
            etiqueta.pack(side="left", padx=10)
            
            boton = ctk.CTkButton(
                frame,
                text="Ejecutar",
                width=80,
                command=lambda c=comando: self.ejecutar_comando(c)
            )
            boton.pack(side="right", padx=10)
    
    def _configurar_tab_config(self):
        # Configuración de apariencia
        frame_apariencia = ctk.CTkFrame(self.tab_config)
        frame_apariencia.pack(fill="x", padx=10, pady=10)
        
        etiqueta_tema = ctk.CTkLabel(
            frame_apariencia,
            text="Tema:",
            font=("Segoe UI", 12, "bold")
        )
        etiqueta_tema.pack(anchor="w", pady=(0, 5))
        
        self.opcion_tema = ctk.CTkOptionMenu(
            frame_apariencia,
            values=["Claro", "Oscuro", "Sistema"],
            command=self.cambiar_tema
        )
        self.opcion_tema.pack(fill="x", pady=(0, 10))
        
        # Configuración de voz
        frame_voz = ctk.CTkFrame(self.tab_config)
        frame_voz.pack(fill="x", padx=10, pady=10)
        
        etiqueta_voz = ctk.CTkLabel(
            frame_voz,
            text="Configuración de voz:",
            font=("Segoe UI", 12, "bold")
        )
        etiqueta_voz.pack(anchor="w", pady=(0, 5))
        
        self.activar_voz = ctk.CTkSwitch(
            frame_voz,
            text="Activar reconocimiento de voz",
            command=self.toggle_voz
        )
        self.activar_voz.pack(anchor="w", pady=5)
    
    def cambiar_seccion(self, seccion):
        self.tabs.set(seccion)
    
    def enviar_mensaje(self, event=None):
        mensaje = self.entrada_mensaje.get("1.0", "end-1c").strip()
        if mensaje:
            self.mostrar_mensaje("Tú", mensaje)
            self.entrada_mensaje.delete("1.0", "end")
            self.procesar_mensaje(mensaje)
    
    def mostrar_mensaje(self, remitente, mensaje):
        # Crear un frame para el mensaje
        frame_mensaje = ctk.CTkFrame(
            self.frame_mensajes,
            corner_radius=10,
            fg_color=("#f0f0f0", "#2b2b2b") if remitente == "Tú" else ("#e3f2fd", "#1a237e")
        )
        frame_mensaje.pack(fill="x", pady=5, padx=5, anchor="e" if remitente == "Tú" else "w")
        
        # Etiqueta del remitente
        etiqueta_remitente = ctk.CTkLabel(
            frame_mensaje,
            text=remitente,
            font=("Segoe UI", 10, "bold"),
            text_color=("#1a73e8", "#8ab4f8") if remitente != "Tú" else ("#5f6368", "#9aa0a6")
        )
        etiqueta_remitente.pack(anchor="w", padx=10, pady=(5, 0))
        
        # Contenido del mensaje
        etiqueta_mensaje = ctk.CTkLabel(
            frame_mensaje,
            text=mensaje,
            font=("Segoe UI", 12),
            justify="left",
            wraplength=500
        )
        etiqueta_mensaje.pack(fill="x", padx=10, pady=(0, 5))
        
        # Hora del mensaje
        hora_actual = datetime.now().strftime("%H:%M")
        etiqueta_hora = ctk.CTkLabel(
            frame_mensaje,
            text=hora_actual,
            font=("Segoe UI", 8),
            text_color=("#5f6368", "#9aa0a6")
        )
        etiqueta_hora.pack(anchor="e", padx=10, pady=(0, 5))
        
        # Desplazarse al final del chat
        self.frame_mensajes._parent_canvas.yview_moveto(1.0)
    
    def procesar_mensaje(self, mensaje):
        # Aquí iría la lógica para procesar el mensaje
        # Por ahora, solo mostramos una respuesta de ejemplo
        self.mostrar_mensaje("Asistente", f"He recibido tu mensaje: {mensaje}")
    
    def ejecutar_comando(self, comando):
        self.mostrar_mensaje("Sistema", f"Ejecutando comando: {comando}")
        # Aquí iría la lógica para ejecutar el comando
    
    def buscar(self):
        termino = self.barra_busqueda.get().strip()
        if termino:
            self.mostrar_mensaje("Sistema", f"Buscando: {termino}")
        else:
            messagebox.showinfo("Búsqueda", "Por favor, ingresa un término de búsqueda")
    
    def cambiar_tema(self, tema):
        if tema == "Claro":
            ctk.set_appearance_mode("light")
            self.modo_oscuro = False
        elif tema == "Oscuro":
            ctk.set_appearance_mode("dark")
            self.modo_oscuro = True
        else:
            # Modo sistema
            ctk.set_appearance_mode("system")
            # Aquí podrías detectar el tema del sistema
    
    def toggle_voz(self):
        if self.activar_voz.get() == 1:
            self.mostrar_mensaje("Sistema", "Reconocimiento de voz activado")
            # Aquí iría la lógica para activar el reconocimiento de voz
        else:
            self.mostrar_mensaje("Sistema", "Reconocimiento de voz desactivado")
            # Aquí iría la lógica para desactivar el reconocimiento de voz
    
    def iniciar(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = DashboardAgente()
    app.iniciar()
