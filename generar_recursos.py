"""
Script para generar recursos predeterminados para la interfaz.
"""
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def crear_directorio_recursos():
    """Crea el directorio de recursos si no existe."""
    recursos_dir = Path("recursos")
    recursos_dir.mkdir(exist_ok=True)
    return recursos_dir

def crear_imagen_predeterminada(tamano, texto, nombre_archivo):
    """Crea una imagen predeterminada con texto centrado."""
    try:
        # Crear una imagen con fondo transparente
        img = Image.new('RGBA', tamano, (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        
        # Colores para el tema claro
        color_fondo = (240, 240, 240, 255)
        color_borde = (200, 200, 200, 255)
        color_texto = (30, 30, 30, 255)
        
        # Dibujar fondo redondeado
        d.rounded_rectangle([(0, 0), tamano], 15, fill=color_fondo, outline=color_borde, width=2)
        
        # Configurar fuente
        try:
            font_size = min(tamano) // 3
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        # Dibujar texto centrado
        text_bbox = d.textbbox((0, 0), texto, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        position = ((tamano[0] - text_width) // 2, (tamano[1] - text_height) // 2)
        
        d.text(position, texto, font=font, fill=color_texto, align="center")
        
        # Guardar imagen
        ruta_guardado = Path("recursos") / nombre_archivo
        img.save(ruta_guardado, "PNG")
        print(f"✓ {nombre_archivo} creado correctamente")
        return True
        
    except Exception as e:
        print(f"✗ Error al crear {nombre_archivo}: {e}")
        return False

def main():
    """Función principal."""
    print("=== Generando recursos predeterminados ===\n")
    
    # Crear directorio de recursos
    crear_directorio_recursos()
    
    # Definir recursos a generar
    recursos = [
        ("icono.png", (64, 64), "AGP"),
        ("logo.png", (200, 200), "AGP\nAsistente"),
        ("microfono_on.png", (64, 64), "🎤 ON"),
        ("microfono_off.png", (64, 64), "🔇 OFF")
    ]
    
    # Generar cada recurso
    exitos = 0
    for nombre, tamano, texto in recursos:
        if crear_imagen_predeterminada(tamano, texto, nombre):
            exitos += 1
    
    print(f"\n=== Proceso completado ===")
    print(f"Recursos generados: {exitos}/{len(recursos)}")
    print(f"Ubicación: {Path('recursos').absolute()}")

if __name__ == "__main__":
    main()
