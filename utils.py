from datetime import datetime

def registrar_historial(entrada, accion, filename="historial_comandos.txt"):
    try:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now():%Y-%m-%d %H:%M:%S} | {entrada} -> {accion}\n")
    except Exception as e:
        print(f"Error guardando historial: {e}")

def normalizar_texto(texto):
    # Corrige términos, acentos, etc.
    return texto.lower().replace("compa", "compae")
