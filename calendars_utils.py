from datetime import datetime, timedelta
from tts import hablar

def leer_proximo_evento():
    import requests
    # Debes tener credenciales OAuth2/Python-Google
    # Ejemplo ficticio con un endpoint propio:
    response = requests.get("https://tuapi.com/calendar/next", params={"token":"TU_TOKEN"})
    if response.status_code == 200:
        evento = response.json()
        resumen = evento.get("summary", "Evento")
        fecha = evento.get("start", "hoy")
        hablar(f"Tu próximo evento es: {resumen} el {fecha}")
    else:
        hablar("No pude obtener tus eventos del calendario.")
