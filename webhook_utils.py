from tts import hablar
import requests

def llama_webhook_accion(nombre_accion):
    webhook_url = "https://miempresa.com/api/hook/"
    res = requests.post(webhook_url, json={"accion": nombre_accion})
    if res.status_code == 200:
        hablar("La acción fue enviada correctamente al sistema.")
    else:
        hablar("No he podido comunicarme con el backend.")
