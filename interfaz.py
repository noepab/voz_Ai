import tkinter as tk
from tkinter import ttk
from collections import deque
import time
import platform

class AsistenteVentana:
    def __init__(self):
        # Colores
        self.COLOR_FONDO = "#1E1E2E"
        self.COLOR_TEXTO = "#FFFFFF"
        self.COLOR_BOTON = "#3B82F6"
        self.COLOR_BOTON_HOVER = "#2563EB"
        self.COLOR_ACTIVO = "#10B981"
        self.COLOR_ESPERA = "#F59E0B"
        self.COLOR_ERROR = "#EF4444"
        
        # Configuración de la ventana
        self.root = tk.Tk()
        self.root.title("Asistente de Voz")
        self.root.geometry("300x400")
        self.root.configure(bg=self.COLOR_FONDO)
        self.root.resizable(False, False)
        
        # Variables de estado
        self.estado = "inactivo"
        self.historial = deque(maxlen=10)
        
        # Configurar la interfaz
        self._configurar_interfaz()
        
        # Iniciar la ventana
        self.root.after(100, self._animar_entrada)
        self.root.mainloop()
    
    def _configurar_interfaz(self):
        """Configura los elementos de la interfaz de usuario"""
        # Frame principal
        self.main_frame = tk.Frame(self.root, bg=self.COLOR_FONDO)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Indicador de estado
        self.estado_frame = tk.Frame(self.main_frame, bg=self.COLOR_FONDO)
        self.estado_frame.pack(pady=(0, 20))
        
        self.canvas = tk.Canvas(self.estado_frame, width=150, height=150, 
                              bg=self.COLOR_FONDO, highlightthickness=0)
        self.canvas.pack()
        
        # Círculo de estado
        self.circulo = self.canvas.create_oval(25, 25, 125, 125, 
                                             fill=self.COLOR_FONDO,
                                             outline=self.COLOR_TEXTO,
                                             width=2)
        
        # Texto de estado
        self.texto_estado = tk.Label(self.estado_frame, 
                                    text="Listo",
                                    font=("Arial", 12, "bold"),
                                    bg=self.COLOR_FONDO,
                                    fg=self.COLOR_TEXTO)
        self.texto_estado.pack(pady=(10, 0))
        
        # Historial
        historial_frame = tk.Frame(self.main_frame, bg=self.COLOR_FONDO)
        historial_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(historial_frame, 
                text="Historial:",
                font=("Arial", 10, "bold"),
                bg=self.COLOR_FONDO,
                fg=self.COLOR_TEXTO,
                anchor="w").pack(fill=tk.X)
        
        self.historial_texto = tk.Text(historial_frame,
                                     height=8,
                                     bg="#2D3748",
                                     fg=self.COLOR_TEXTO,
                                     font=("Arial", 9),
                                     wrap=tk.WORD,
                                     padx=10,
                                     pady=10,
                                     state=tk.DISABLED)
        self.historial_texto.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Barra de desplazamiento
        scrollbar = ttk.Scrollbar(self.historial_texto)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.historial_texto.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.historial_texto.yview)
        
        # Botón de cerrar
        self.btn_cerrar = tk.Button(self.main_frame,
                                  text="Cerrar",
                                  command=self._cerrar_aplicacion,
                                  bg=self.COLOR_BOTON,
                                  fg="white",
                                  bd=0,
                                  padx=20,
                                  pady=8,
                                  font=("Arial", 10, "bold"),
                                  cursor="hand2")
        self.btn_cerrar.pack(pady=(15, 0))
        
        # Configurar hover del botón
        self.btn_cerrar.bind("<Enter>", lambda e: self.btn_cerrar.config(bg=self.COLOR_BOTON_HOVER))
        self.btn_cerrar.bind("<Leave>", lambda e: self.btn_cerrar.config(bg=self.COLOR_BOTON))
    
    def _animar_entrada(self):
        """Animación de entrada suave"""
        for i in range(0, 101, 5):
            if not self.root.winfo_exists():
                return
            alpha = i / 100
            self.root.attributes('-alpha', alpha)
            self.root.update()
            time.sleep(0.01)
    
    def _cerrar_aplicacion(self):
        """Cierra la aplicación con animación"""
        for i in range(100, -1, -5):
            if not self.root.winfo_exists():
                return
            alpha = i / 100
            self.root.attributes('-alpha', max(0, alpha))
            self.root.update()
            time.sleep(0.01)
        self.root.destroy()
    
    def actualizar_estado(self, estado, texto):
        """Actualiza el estado del asistente"""
        self.estado = estado
        color = self.COLOR_FONDO
        
        if estado == "activo":
            color = self.COLOR_ACTIVO
        elif estado == "espera":
            color = self.COLOR_ESPERA
        elif estado == "error":
            color = self.COLOR_ERROR
        
        self.canvas.itemconfig(self.circulo, fill=color)
        self.texto_estado.config(text=texto)
        self._agregar_al_historial(texto)
    
    def _agregar_al_historial(self, texto):
        """Agrega un mensaje al historial"""
        timestamp = time.strftime("%H:%M:%S")
        self.historial.append(f"[{timestamp}] {texto}")
        
        # Actualizar el widget de texto
        self.historial_texto.config(state=tk.NORMAL)
        self.historial_texto.delete(1.0, tk.END)
        
        for mensaje in reversed(self.historial):
            self.historial_texto.insert(tk.END, f"{mensaje}\n")
        
        self.historial_texto.config(state=tk.DISABLED)
        self.historial_texto.see(tk.END)

# Instancia global del asistente
asistente = None

def iniciar_interfaz():
    """Inicia la interfaz del asistente"""
    global asistente
    asistente = AsistenteVentana()
    return asistente
        self.instruccion.pack(pady=(5, 0))
        
        # Panel de historial con efecto de vidrio
        self.historial_container = tk.Frame(main_frame, bg='')
        self.historial_container.pack(fill='both', expand=True, pady=(10, 0))
        
        # Canvas para el fondo con efecto de vidrio
        self.historial_canvas = tk.Canvas(self.historial_container, 
                                        bg=self.estilos.COLOR_FONDO, 
                                        highlightthickness=0, 
                                        bd=0)
        self.historial_canvas.pack(fill='both', expand=True)
        
        # Dibujar fondo con efecto de vidrio
        self._draw_glass_panel(self.historial_canvas, 0, 0, 280, 150, 12)
        
        # Título del historial con icono
        titulo_frame = tk.Frame(self.historial_canvas, bg=self.estilos.COLOR_INACTIVO)
        titulo_frame.place(x=10, y=8, width=260, height=24)
        
        # Icono de historial
        self.historial_canvas.create_text(20, 20, text="📋", 
                                        font=("Segoe UI Emoji", 12), 
                                        anchor='w',
                                        fill=self.estilos.COLOR_TEXTO)
                                        
        # Título
        tk.Label(titulo_frame, text="HISTORIAL DE COMANDOS", 
                bg=self.estilos.COLOR_INACTIVO, 
                fg=self.estilos.COLOR_TEXTO,
                font=self.estilos.obtener_fuente(9, True),
                anchor='w').place(x=30, y=0, width=230, height=24)
        
        # Línea decorativa con color sólido
        self.historial_canvas.create_line(10, 32, 270, 32, 
                                        fill=self.estilos.COLOR_INACTIVO, 
                                        width=1)
        
        # Contenedor con scroll personalizado
        self.scroll_frame = tk.Frame(self.historial_canvas, 
                                   bg=self.estilos.COLOR_FONDO)
        self.scroll_frame.place(x=10, y=40, width=260, height=100)
        
        # Canvas para el contenido desplazable
        self.scroll_canvas = tk.Canvas(self.scroll_frame, 
                                      bg=self.estilos.COLOR_FONDO, 
                                      highlightthickness=0, 
                                      bd=0)
        self.scroll_canvas.pack(side='left', fill='both', expand=True)
        
        # Frame para el contenido
        self.scroll_content = tk.Frame(self.scroll_canvas, 
                                     bg=self.estilos.COLOR_FONDO)
        self.scroll_window = self.scroll_canvas.create_window((0, 0), 
                                                            window=self.scroll_content, 
                                                            anchor='nw',
                                                            tags=("scroll_frame",))
        
        # Configurar el scroll
        scrollbar = ttk.Scrollbar(self.scroll_frame, 
                                orient='vertical', 
                                command=self.scroll_canvas.yview)
        scrollbar.pack(side='right', fill='y')
        self.scroll_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Configurar el evento de desplazamiento
        self.scroll_content.bind('<Configure>', self._on_frame_configure)
        self.scroll_canvas.bind('<Configure>', self._on_canvas_configure)
        
        # Estilo personalizado para la barra de desplazamiento
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Vertical.TScrollbar",
                       background=self.estilos.COLOR_INACTIVO,
                       arrowcolor=self.estilos.COLOR_TEXTO,
                       bordercolor=self.estilos.COLOR_FONDO,
                       lightcolor=self.estilos.COLOR_INACTIVO,
                       darkcolor=self.estilos.COLOR_INACTIVO,
                       troughcolor=f"{self.estilos.COLOR_FONDO}80",
                       arrowwidth=2,
                       arrowsize=12)
        
        # Frame para el historial de comandos
        self.historial_label = tk.Label(self.scroll_content, 
                                      text="", 
                                      bg=self.estilos.COLOR_FONDO, 
                                      fg=self.estilos.COLOR_TEXTO, 
                                      font=self.estilos.obtener_fuente(9), 
                                      justify=tk.LEFT, 
                                      anchor='nw',
                                      wraplength=230)
        self.historial_label.pack(padx=2, pady=2, fill='both')
        
        # Botón para limpiar el historial
        self.btn_limpiar = tk.Button(self.historial_canvas, 
                                    text="×", 
                                    font=("Arial", 12, "bold"),
                                    fg=self.estilos.COLOR_TEXTO,
                                    bg=self.estilos.COLOR_FONDO,
                                    bd=0,
                                    activeforeground=self.estilos.COLOR_ERROR,
                                    activebackground=self.estilos.COLOR_FONDO,
                                    command=self._limpiar_historial,
                                    cursor="hand2")
        self.btn_limpiar.place(x=250, y=5, width=20, height=20)
        
        # Configurar hover para el botón
        self.btn_limpiar.bind("<Enter>", lambda e: self.btn_limpiar.config(fg=self.estilos.COLOR_ERROR))
        self.btn_limpiar.bind("<Leave>", lambda e: self.btn_limpiar.config(fg=self.estilos.COLOR_TEXTO))
        
        # Estado inicial
        self.color_actual = "gray"
        self.texto_estado = "Iniciando..."
        self.ultimo_estado = ""
        self.buffer_texto = deque(maxlen=5)  # Historial reducido para mostrar solo los últimos comandos
        
        # Actualizar la interfaz
        self._actualizar_interfaz()
        
        # Iniciar animación de entrada
        self._animar_entrada()
        
        # Iniciar bucle de animación
        self._animar()
    
    def _animar_entrada(self):
        """Animación de entrada suave"""
        for i in range(0, 101, 5):
            if not self.root.winfo_exists():
                return
            alpha = i / 100
            self.root.attributes('-alpha', alpha * 0.95)  # 95% de opacidad máxima
            self.root.update()
            time.sleep(0.01)
    
    def _animar(self):
        """Bucle principal de animación"""
        self.animar_particulas()
        self.actualizar_ondas()
        self.root.after(30, self._animar)
    
    def _create_title_bar(self):
        """Crea una barra de título personalizada"""
        # Barra de título
        self.title_bar = tk.Frame(self.main_container, bg=self.estilos.COLOR_FONDO, 
                                relief='flat', bd=0, height=30)
        self.title_bar.place(x=0, y=0, width=320, height=30)
        
        # Título de la aplicación
        title_label = tk.Label(self.title_bar, text="AUTOGESTIÓN PRO", 
                             bg=self.estilos.COLOR_FONDO,
                             fg=self.estilos.COLOR_TEXTO,
                             font=self.estilos.obtener_fuente(10, True))
        title_label.place(x=12, y=5)
        
        # Botón de cerrar
        close_btn = tk.Label(self.title_bar, text="✕", 
                           font=("Arial", 12, "bold"),
                           fg=self.estilos.COLOR_TEXTO,
                           bg=self.estilos.COLOR_FONDO,
                           cursor="hand2")
        close_btn.place(x=290, y=0, width=30, height=30)
        close_btn.bind("<Button-1>", lambda e: self._cerrar_aplicacion())
        close_btn.bind("<Enter>", lambda e: close_btn.config(bg="#EF4444", fg="white"))
        close_btn.bind("<Leave>", lambda e: close_btn.config(bg=self.estilos.COLOR_FONDO, 
                                                           fg=self.estilos.COLOR_TEXTO))
        
        # Línea decorativa inferior
        self.title_bar.lower()
    
    def _cerrar_aplicacion(self):
        """Cierra la aplicación con animación"""
        for i in range(95, -1, -5):
            if not self.root.winfo_exists():
                return
            alpha = i / 100
            self.root.attributes('-alpha', max(0, alpha))
            self.root.update()
            time.sleep(0.01)
        self.root.destroy()
    
    def _start_move(self, event):
        """Inicia el arrastre de la ventana"""
        self._offsetx = event.x
        self._offsety = event.y
    
    def _on_drag(self, event):
        """Maneja el arrastre de la ventana"""
        x = self.root.winfo_pointerx() - self._offsetx
        y = self.root.winfo_pointery() - self._offsety
        self.root.geometry(f"+{x}+{y}")
    
    def _draw_rounded_rect(self, canvas, x1, y1, x2, y2, radius=25, **kwargs):
        """Dibuja un rectángulo con esquinas redondeadas"""
        points = [x1+radius, y1,
                 x1+radius, y1,
                 x2-radius, y1,
                 x2-radius, y1,
                 x2, y1,
                 x2, y1+radius,
                 x2, y1+radius,
                 x2, y2-radius,
                 x2, y2-radius,
                 x2, y2,
                 x2-radius, y2,
                 x2-radius, y2,
                 x1+radius, y2,
                 x1+radius, y2,
                 x1, y2,
                 x1, y2-radius,
                 x1, y2-radius,
                 x1, y1+radius,
                 x1, y1+radius,
                 x1, y1]
        return canvas.create_polygon(points, **kwargs, smooth=True)
    
    def _create_glass_effect(self):
        """Crea un efecto de vidrio esmerilado"""
        # Fondo con ruido para efecto de vidrio
        for _ in range(200):
            x = 90 + (random.random() - 0.5) * 160
            y = 90 + (random.random() - 0.5) * 160
            r = random.random() * 2
            self.canvas.create_oval(x-r, y-r, x+r, y+r, 
                                  fill='white', 
                                  outline='',
                                  state='hidden',
                                  tags=('noise',))
    
    def _create_gradient_circle(self, x, y, radius, color1, color2):
        """Crea un círculo con gradiente radial"""
        for i in range(radius, 0, -1):
            ratio = i / radius
            r = int(int(color1[1:3], 16) * ratio + int(color2[1:3], 16) * (1 - ratio))
            g = int(int(color1[3:5], 16) * ratio + int(color2[3:5], 16) * (1 - ratio))
            b = int(int(color1[5:7], 16) * ratio + int(color2[5:7], 16) * (1 - ratio))
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.canvas.create_oval(x-i, y-i, x+i, y+i, fill=color, outline='', tags=('gradient',))
    
    def _init_particulas(self):
        """Inicializa las partículas flotantes"""
        for _ in range(15):
            x = random.randint(20, 160)
            y = random.randint(20, 160)
            size = random.uniform(0.5, 2)
            speed = random.uniform(0.2, 0.8)
            angle = random.uniform(0, 2 * math.pi)
            self.particulas.append({
                'x': x, 'y': y, 'size': size, 'speed': speed, 'angle': angle,
                'item': None
            })
    
    def animar_particulas(self):
        """Anima las partículas flotantes"""
        for p in self.particulas:
            # Actualizar posición
            p['x'] += math.cos(p['angle']) * p['speed']
            p['y'] += math.sin(p['angle']) * p['speed']
            
            # Rebotar en los bordes
            if p['x'] <= 20 or p['x'] >= 160:
                p['angle'] = math.pi - p['angle']
            if p['y'] <= 20 or p['y'] >= 160:
                p['angle'] = -p['angle']
            
            # Mantener dentro del círculo
            dx = p['x'] - 90
            dy = p['y'] - 90
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 70:
                # Redirigir hacia el centro
                p['angle'] = math.atan2(dy, dx) + math.pi
                p['x'] = 90 + math.cos(p['angle']) * 70
                p['y'] = 90 + math.sin(p['angle']) * 70
            
            # Dibujar partícula
            if p['item']:
                self.canvas.delete(p['item'])
            
            alpha = min(0.6, 0.3 + (70 - dist) / 70 * 0.3)  # Más opacas cerca del borde
            p['item'] = self.canvas.create_oval(
                p['x']-p['size'], p['y']-p['size'],
                p['x']+p['size'], p['y']+p['size'],
                fill='white', outline='', tags=('particle',)
            )
            self.canvas.itemconfig(p['item'], stipple=f"gray{int(alpha*255):02x}")
    
    def _on_hover(self, is_hovering):
        """Efecto al pasar el ratón sobre el indicador"""
        if is_hovering and not self.animacion_activa:
            self.canvas.itemconfig(self.logo_texto, fill=self.estilos.COLOR_PRIMARIO)
        else:
            self.canvas.itemconfig(self.logo_texto, fill=self.estilos.COLOR_TEXTO)
    
    def _draw_glass_panel(self, canvas, x, y, width, height, radius):
        """Dibuja un panel con efecto de vidrio"""
        # Fondo con transparencia (usando un color sólido en lugar de transparencia)
        canvas.create_rectangle(x, y, x+width, y+height, 
                              fill=self.estilos.COLOR_INACTIVO, 
                              outline='', 
                              tags=('glass_bg',))
        
        # Borde con brillo (usando un color más claro para el borde)
        canvas.create_rectangle(x, y, x+width, y+height, 
                              outline=self.estilos.COLOR_TEXTO,
                              width=1,
                              tags=('glass_border',))
    
    def _on_frame_configure(self, event):
        """Actualiza la región de desplazamiento"""
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        """Ajusta el tamaño del frame de contenido"""
        self.scroll_canvas.itemconfig(self.scroll_window, width=event.width)
    
    def _limpiar_historial(self):
        """Limpia el historial de comandos"""
        self.buffer_texto.clear()
        self.historial_label.config(text="")
    
    def _actualizar_interfaz(self):
        """Actualiza los elementos de la interfaz"""
        # Mapeo de colores para el borde
        bordes = {
            "green": self.estilos.COLOR_EXITO,
            "blue": self.estilos.COLOR_PRIMARIO,
            "yellow": self.estilos.COLOR_ALERTA,
            "red": self.estilos.COLOR_ERROR,
            "gray": self.estilos.COLOR_INACTIVO
        }
        
        # Aplicar el color del borde
        color_borde = bordes.get(self.color_actual, self.estilos.COLOR_INACTIVO)
        self.canvas.itemconfig(self.circulo_bg, fill=color_border)
        
        # Actualizar el color del texto del logo según el estado
        if self.color_actual in ["blue", "yellow"]:
            self.canvas.itemconfig(self.logo_texto, fill=self.estilos.COLOR_TEXTO)
        else:
            self.canvas.itemconfig(self.logo_texto, fill=self.estilos.COLOR_TEXTO)
        
        # Actualizar título de la ventana
        if hasattr(self, 'root') and self.root.winfo_exists():
            self.root.title(f"AGP Asistente - {self.texto_estado}" if self.texto_estado else "AGP Asistente")
            self.root.update_idletasks()
    
    def iniciar_animacion(self):
        """Inicia la animación de escucha"""
        self.animacion_activa = True
        self._crear_onda()
    
    def detener_animacion(self):
        """Detiene la animación de escucha"""
        self.animacion_activa = False
        for onda in self.ondas:
            if 'item' in onda:
                self.canvas.delete(onda['item'])
        self.ondas.clear()
    
    def _crear_onda(self):
        """Crea una nueva onda de sonido"""
        if not self.animacion_activa:
            return
            
        # Crear nueva onda
        self.ondas.append({
            'x': 90, 'y': 90, 'radius': 70, 'alpha': 1.0, 'width': 2
        })
        
        # Programar próxima onda
        if len(self.ondas) < 3:  # Máximo 3 ondas a la vez
            self.root.after(300, self._crear_onda)
    
    def actualizar_ondas(self):
        """Actualiza la animación de las ondas"""
        for onda in self.ondas[:]:
            onda['radius'] += 1.5
            onda['alpha'] -= 0.02
            
            if onda['alpha'] <= 0:
                if 'item' in onda:
                    self.canvas.delete(onda['item'])
                self.ondas.remove(onda)
                continue
                
            # Actualizar o crear el elemento de la onda
            if 'item' in onda and self.canvas.type(onda['item']) != '':
                self.canvas.delete(onda['item'])
                
            color = self.estilos.COLOR_PRIMARIO
            if self.color_actual == 'yellow':
                color = self.estilos.COLOR_ALERTA
            elif self.color_actual == 'red':
                color = self.estilos.COLOR_ERROR
                
            alpha_hex = f"{int(onda['alpha'] * 255):02x}"
            outline_color = f"{color}{alpha_hex}"
            
            x0 = onda['x'] - onda['radius']
            y0 = onda['y'] - onda['radius']
            x1 = onda['x'] + onda['radius']
            y1 = onda['y'] + onda['radius']
            
            onda['item'] = self.canvas.create_oval(
                x0, y0, x1, y1,
                outline=outline_color,
                width=onda['width'],
                tags=('wave',)
            )
    
    def cambiar_color(self, color, texto=""):
        """Cambia el color del indicador y actualiza el texto de estado"""
        self.ultimo_estado = self.texto_estado
        self.color_actual = color
        self.texto_estado = texto
        
        # Mapeo de colores a códigos hexadecimales
        colores = {
            "green": self.estilos.COLOR_EXITO,
            "blue": self.estilos.COLOR_PRIMARIO,
            "yellow": self.estilos.COLOR_ALERTA,
            "red": self.estilos.COLOR_ERROR,
            "gray": self.estilos.COLOR_INACTIVO
        }
        
        # Actualizar la interfaz
        color_elegido = colores.get(color, self.estilos.COLOR_INACTIVO)
        self.canvas.itemconfig(self.circulo, fill=color_elegido)
        self.label_estado.config(text=texto, fg=self.estilos.COLOR_TEXTO)
        
        # Agregar al historial si es un nuevo comando o estado
        if texto and texto != self.ultimo_estado:
            timestamp = time.strftime("%H:%M:%S")
            self.buffer_texto.append(f"[{timestamp}] {texto}")
            
            # Actualizar el historial con formato mejorado
            texto_historial = ""
            for i, item in enumerate(reversed(self.buffer_texto), 1):
                # Resaltar el último comando
                if i == 1:
                    texto_historial += f"➤ {item}\n"
                else:
                    texto_historial += f"  {item}\n"
            
            self.historial_label.config(text=texto_historial.strip())
            
            # Hacer scroll al final del historial
            self.scroll_canvas.yview_moveto(1.0)
        
        # Actualizar instrucción basada en el estado
        if color == "blue":
            self.instruccion.config(text="Escuchando... Di tu comando", 
                                  fg=self.estilos.COLOR_TEXTO)
            self.iniciar_animacion()
        elif color == "yellow":
            self.instruccion.config(text="Procesando tu solicitud...", 
                                  fg=self.estilos.COLOR_TEXTO)
        elif color == "green":
            self.instruccion.config(text="Di 'Autogestión' o 'AGP' para comenzar", 
                                  fg=self.estilos.COLOR_TEXTO)
            self.detener_animacion()
        elif color == "red":
            self.instruccion.config(text="Error detectado. Intenta de nuevo", 
                                  fg=self.estilos.COLOR_ERROR)
        
        # Actualizar título de la ventana
        if hasattr(self, 'root') and self.root.winfo_exists():
            self.root.title(f"AGP Asistente - {texto}" if texto else "AGP Asistente")
            
        # Forzar actualización de la interfaz
        self._actualizar_interfaz()

        # Iniciar animación
        self.animar_onda()
    
    def cambiar_color(self, color, texto=""):
        """Cambia el color del indicador y actualiza el texto de estado"""
        self.ultimo_estado = self.texto_estado
        self.color_actual = color
        self.texto_estado = texto
        
        # Mapeo de colores a códigos hexadecimales
        colores = {
            "green": self.COLOR_EXITO,    # Listo/éxito
            "blue": self.COLOR_ACTIVO,    # Escuchando
            "yellow": self.COLOR_ALERTA,  # Procesando
            "red": self.COLOR_ERROR,      # Error
            "gray": self.COLOR_INACTIVO   # Inactivo
        }
        
        # Actualizar la interfaz
        color_elegido = colores.get(color, self.COLOR_INACTIVO)
        self.canvas.itemconfig(self.circulo, fill=color_elegido)
        self.canvas.itemconfig(self.logo_texto, fill=self.COLOR_TEXTO)
        self.label_estado.config(text=texto, fg=self.COLOR_TEXTO)
        
        # Agregar al historial si es un nuevo comando o estado
        if texto and texto != self.ultimo_estado:
            timestamp = time.strftime("%H:%M:%S")
            self.buffer_texto.append(f"[{timestamp}] {texto}")
            # Actualizar el historial con formato mejorado
            texto_historial = ""
            for i, item in enumerate(reversed(self.buffer_texto), 1):
                # Resaltar el último comando
                if i == 1:
                    texto_historial += f"➤ {item}\n"
                else:
                    texto_historial += f"  {item}\n"
            self.historial_label.config(text=texto_historial.strip())
            
            # Hacer scroll al final del historial
            self.historial_label.master.master.update_idletasks()
            self.historial_label.master.master.yview_moveto(1.0)
        
        # Actualizar instrucción basada en el estado
        if color == "blue":
            self.instruccion.config(text="Escuchando... Di tu comando", 
                                  fg=self.COLOR_TEXTO_SECUNDARIO)
        elif color == "yellow":
            self.instruccion.config(text="Procesando tu solicitud...", 
                                  fg=self.COLOR_TEXTO_SECUNDARIO)
        elif color == "green":
            self.instruccion.config(text="Di 'Autogestión' o 'AGP' para comenzar", 
                                  fg=self.COLOR_TEXTO_SECUNDARIO)
        elif color == "red":
            self.instruccion.config(text="Error detectado. Intenta de nuevo", 
                                  fg=self.COLOR_ERROR)
        
        # Actualizar título de la ventana
        self.root.title(f"AGP Asistente - {texto}" if texto else "AGP Asistente")
    
    def animar_onda(self):
        """Anima el indicador de actividad"""
        if self.animacion_activa:
            # Obtener el tamaño actual del círculo de onda
            coords = self.canvas.coords(self.onda)
            if coords[0] <= 20:  # Si la onda alcanzó el tamaño máximo
                self.canvas.coords(self.onda, 30, 30, 130, 130)  # Reiniciar tamaño
                self.canvas.itemconfig(self.onda, fill=self.COLOR_FONDO)  # Hacerlo transparente
            else:
                # Aumentar el tamaño de la onda
                coords = [c-3 for c in coords[:2]] + [c+3 for c in coords[2:]]
                self.canvas.coords(self.onda, *coords)
                
                # Hacer la onda más transparente a medida que crece
                alpha = int(255 * (1 - (coords[0] - 20) / 20))
                if alpha > 0:
                    color = self.canvas.itemcget(self.circulo, 'fill')
                    # Asegurarse de que el color sea válido
                    if color and color != '':
                        self.canvas.itemconfig(self.onda, fill=color)
                        # Aplicar transparencia
                        self.canvas.itemconfig(self.onda, stipple=f"gray{min(alpha, 255)}")
        
        # Programar la próxima animación
        self.root.after(50, self.animar_onda)
    
    def iniciar_animacion(self):
        """Inicia la animación de escucha"""
        self.animacion_activa = True
        self.canvas.itemconfig(self.onda, fill=self.canvas.itemcget(self.circulo, 'fill'))
    
    def detener_animacion(self):
        """Detiene la animación de escucha"""
        self.animacion_activa = False
        self.canvas.coords(self.onda, 25, 25, 125, 125)
        self.canvas.itemconfig(self.onda, fill="#1a1a1a")
    
    def _actualizar_interfaz(self):
        """Actualiza los elementos de la interfaz"""
        # Mapeo de colores para el borde
        bordes = {
            "green": self.COLOR_EXITO,    # Verde esmeralda
            "blue": self.COLOR_ACTIVO,    # Azul brillante
            "yellow": self.COLOR_ALERTA,  # Ámbar
            "red": self.COLOR_ERROR,      # Rojo
            "gray": self.COLOR_INACTIVO   # Gris azulado oscuro
        }
        
        # Aplicar el color del borde
        color_borde = bordes.get(self.color_actual, self.COLOR_INACTIVO)
        self.canvas.itemconfig(self.circulo_borde, outline=color_borde)
        
        # Actualizar el color del texto del logo según el estado
        if self.color_actual in ["blue", "yellow"]:
            self.canvas.itemconfig(self.logo_texto, fill=self.COLOR_TEXTO)
        else:
            self.canvas.itemconfig(self.logo_texto, fill=self.COLOR_TEXTO_SECUNDARIO)
        
        # Forzar actualización de la interfaz
        self.root.update_idletasks()

# Instancia global del indicador de estado
led = IndicadorEstado()
