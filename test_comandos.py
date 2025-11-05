import comandos

def test_broma():
    comandos.ejecutar_comando("dime una broma")
    # Aquí comprobarías respuestas con un mock de TTS/registro

def test_url():
    comandos.ejecutar_comando("abrir google")
    # Comprueba que realmente hace la acción (usa mocks)
