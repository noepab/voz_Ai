"""
Script para descargar recursos necesarios para la interfaz.
"""
import os
import urllib.request
from pathlib import Path

# Crear directorio de recursos si no existe
RECURSOS_DIR = Path("recursos")
RECURSOS_DIR.mkdir(exist_ok=True)

def descargar_recurso(url, destino):
    """Descarga un recurso desde una URL."""
    try:
        print(f"Descargando {destino.name}...")
        urllib.request.urlretrieve(url, destino)
        print(f"  ✓ {destino.name} descargado correctamente")
        return True
    except Exception as e:
        print(f"  ✗ Error al descargar {destino.name}: {e}")
        return False

def crear_icono_predeterminado(nombre):
    """Crea un icono predeterminado si no se puede descargar."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Crear una imagen simple con el nombre
        bg_color = (70, 130, 180, 255) if "microfono" in nombre else (50, 50, 50, 255)
        img = Image.new('RGBA', (256, 256), bg_color)
        d = ImageDraw.Draw(img)
        
        # Dibujar un círculo
        d.ellipse([(10, 10), (246, 246)], outline='white', width=5)
        
        # Texto
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        # Texto a mostrar
        if "microfono" in nombre:
            text = "🎤 ON" if "on" in nombre else "🎤 OFF"
        else:
            text = "AGP"
        
        # Calcular tamaño del texto
        text_bbox = d.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Posicionar texto en el centro
        position = ((256 - text_width) // 2, (256 - text_height) // 2)
        d.text(position, text, font=font, fill='white')
        
        # Guardar imagen
        img = img.resize((64, 64), Image.LANCZOS)
        img.save(str(RECURSOS_DIR / nombre))
        print(f"  ✓ {nombre} creado con éxito")
        return True
    except Exception as e:
        print(f"  ✗ Error al crear icono predeterminado: {e}")
        return False

def main():
    print("=== Generando recursos para la interfaz ===\n")
    
    # Lista de recursos a generar
    recursos = ["icono.png", "logo.png", "microfono_on.png", "microfono_off.png"]
    
    for archivo in recursos:
        destino = RECURSOS_DIR / archivo
        if not destino.exists():
            print(f"  • Generando {archivo}...")
            if not crear_icono_predeterminado(archivo):
                print(f"  ✗ No se pudo generar {archivo}")
        else:
            print(f"  ✓ {archivo} ya existe, omitiendo")
    
    print("\n=== Proceso completado ===")
    print(f"Recursos disponibles en: {RECURSOS_DIR.absolute()}")

if __name__ == "__main__":
    main()
