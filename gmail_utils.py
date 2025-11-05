from tts import hablar

def anunciar_mails_nuevos():
    import requests
    # Usa tu API, Zapier o Google Python Client
    # Simulación:
    mails_nuevos = 3  # Puedes leerlo de la API real
    if mails_nuevos > 0:
        hablar(f"Tienes {mails_nuevos} correos electrónicos nuevos.")
    else:
        hablar("No tienes correos nuevos.")
